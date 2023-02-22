from concurrent import futures
import grpc
import time
import chat_pb2 as chat
import chat_pb2_grpc as rpc
from collections import deque
import threading
import bcrypt
import socket
import errno

# Chat Server class for handling gRPC connected clients and their requests
class ChatServer(rpc.ChatServerServicer):

    def __init__(self):
        # List with all the chat history
        self.users = {}
        # maps context.peer() to username
        self.clients = {}
        # thread locks for preventing race conditions in users and clients
        self.users_lock = threading.Lock()
        self.clients_lock = threading.Lock()


    # hash password again for storage
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(FORMAT), bcrypt.gensalt())


    # return true if password matches hashed password
    def check_password(self, password, hashed_password):
        # print(hashed_password)
        return bcrypt.checkpw(password.encode(FORMAT), hashed_password)


    # The stream which will be used to send new messages to clients
    def ChatStream(self, _request_iterator, context):
        # For every client a infinite loop starts (in gRPC's own managed thread)
        user = None
        while True:
            try: 
                if context.peer() in self.clients:
                    user = self.clients[context.peer()]
                if not user:
                    continue
                # Check if there are any new messages if logged in
                while len(self.users[user]['unread']) > 0:
                    message = self.users[user]['unread'].popleft()
                    yield message
            except IOError as e:
                # ignore recoverable EAGAIN and EWOULDBLOCK error
                if e.errno == errno.EAGAIN and e.errno == errno.EWOULDBLOCK:
                    continue
            except Exception as e:
                print(e)
                yield chat.ServerResponse(success=False, message="[SERVER] Error sending message")
                

    # Send a message to the server then to the receiver
    def SendNote(self, request: chat.Note, context):
        try: 
            # check version
            if request.version != 1:
                return chat.ServerResponse(success=False, message="[SERVER] Version mismatch")
            
            # check if the user is logged in
            current_user = None
            if context.peer() in self.clients:
                current_user = self.clients[context.peer()]
            if current_user is None or not current_user:
                return chat.ServerResponse(success=False, message="[SERVER] You are not logged in")

            # Check if the receiver exists
            if request.receiver not in self.users:
                return chat.ServerResponse(success=False, message="[SERVER] User does not exist")
            
            # append to unread
            with self.users_lock:
                self.users[request.receiver]['unread'].append(request)
            return chat.ServerResponse(success=True, message="")
        
        except Exception as e:
            print(e)
            return chat.ServerResponse(success=False, message="[SERVER] Error sending message")
    
    
    # Acount Creaton
    def CreateAccount(self, request: chat.AccountInfo, context):
        try: 
            # Check if the username is already taken
            if request.username in self.users:
                return chat.ServerResponse(success=False, message="[SERVER] Username already taken")
            # Create the account
            with self.users_lock:
                self.users[request.username] = {
                    "password": self.hash_password(request.password), 
                    "client": None,
                    "logged_in": False,
                    "unread": deque()
                }
            # success message
            return chat.ServerResponse(success=True, message=f"[SERVER] Account {request.username} created")
        
        except Exception as e:
            print(e)
            return chat.ServerResponse(success=False, message="[SERVER] Error creating account")
    

    # Account Login: a client must be logged in on one device at a time, else they are logged out of previous device
    def Login(self, request: chat.AccountInfo, context):
        try: 
            # Check if the username exists
            if request.username not in self.users:
                return chat.ServerResponse(success=False, message="[SERVER] Username does not exist")
            # Check if the password is correct
            if not self.check_password(request.password, self.users[request.username]['password']):
                return chat.ServerResponse(success=False, message="[SERVER] Incorrect password")
            # warn previous client of the user account if logged in on new client
            if request.username in self.users and self.users[request.username]["client"] is not None:
                detection = chat.Note(message = f"Logged out: detected {request.username} login on another client.")
                self.users[request.username]["unread"].append(detection)
                # wait for previous client to get message
                time.sleep(1)
                prev_client = self.users[request.username]["client"]
                with self.clients_lock:
                    self.clients[prev_client] = None
                
            # Logout previous user
            if context.peer() in self.clients and self.clients[context.peer()] is not None:
                prev_user = self.clients[context.peer()]
                with self.users_lock:
                    self.users[prev_user]["logged_in"] = False
                    self.users[prev_user]["client"] = None

            # login new user
            with self.clients_lock:
                self.clients[context.peer()] = request.username
            with self.users_lock:
                self.users[request.username]['client'] = context.peer()
                self.users[request.username]['logged_in'] = True
            # successfully logged in
            return chat.ServerResponse(success=True, message=f"[SERVER] Logged in as {request.username}")
        
        except Exception as e:
            print(e)
            return chat.ServerResponse(success=False, message="[SERVER] Error logging in")


    # Account Logout of the current client
    def Logout(self, request: chat.Empty, context):
        # Check if the username exists
        if context.peer() not in self.clients or self.clients[context.peer()] is None:
            return chat.ServerResponse(success=False, message="[SERVER] You are not logged in")
        
        # Logout the user: change both users and clients dicts
        username = self.clients[context.peer()]
        with self.users_lock:
            self.users[username]['logged_in'] = False
            self.users[username]['client'] = None
        with self.clients_lock:
            self.clients[context.peer()] = None

        return chat.ServerResponse(success=True, message=f"[SERVER] Logged out of user {username}")


    # Account list
    def ListAccounts(self, request: chat.AccountInfo, context):
        # Lists all users in the users dict
        for user in self.users.keys():
            if request.username == "*" or not request.username or request.username in user:
                yield chat.ServerResponse(success=True, message=f"{user}")


    # Account delete
    def DeleteAccount(self, request: chat.AccountInfo, context):
        try: 
            # Check if the username exists: return if not
            if request.username not in self.users:
                yield chat.ServerResponse(success=False, message="[SERVER] Username does not exist")
                return
            # Check if the password is correct: return if incorrect
            if not self.check_password(request.password, self.users[request.username]['password']):
                yield chat.ServerResponse(success=False, message=f"[SERVER] Incorrect password for account {request.username}")
                return
            # Yield success message before actual deletion so user can be logout
            yield chat.ServerResponse(success=True, message="")
                
            # warn the currently logged in client on the deleted account
            prev_client = self.users[request.username]["client"]
            if prev_client is not None:
                detection = chat.Note(message = f"Logged out: account {request.username} has been deleted.")
                with self.users_lock:
                    self.users[request.username]["unread"].append(detection)
                with self.clients_lock:
                    self.clients[prev_client] = None
            with self.users_lock:
                del self.users[request.username]

            # actual account deletion detection
            yield chat.ServerResponse(success=True, message=f"[SERVER] Account {request.username} deleted")
            return
        except KeyError or ValueError:
            return chat.ServerResponse(success=False, message="[SERVER] Failed: make sure information is entered correctly")
        except Exception as e:
            return chat.ServerResponse(success=False, message=f"[SERVER] Failed: {e}")


# main thread for handling clients
if __name__ == '__main__':
    FORMAT = "utf-8"
    port = 43210
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) 
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    print('[SERVER STARTING] Listening on port ' + str(port) + '...')

    addr_host = socket.gethostbyname(socket.gethostname())
    server.add_insecure_port(f'{addr_host}:{port}')
    server.start()

    server.wait_for_termination()