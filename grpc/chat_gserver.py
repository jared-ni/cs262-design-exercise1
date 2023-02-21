from concurrent import futures
import grpc
import time
import chat_pb2 as chat
import chat_pb2_grpc as rpc
from collections import deque
import threading
import bcrypt


class ChatServer(rpc.ChatServerServicer):

    def __init__(self):
        # List with all the chat history
        self.users = {}
        # maps context.peer() to username
        self.clients = {}
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
            if context.peer() in self.clients:
                user = self.clients[context.peer()]
            if not user:
                continue
            # Check if there are any new messages if logged in
            while len(self.users[user]['unread']) > 0:
                message = self.users[user]['unread'].popleft()
                yield message


    # Send a message to the server then to the receiver
    def SendNote(self, request: chat.Note, context):
        current_user = self.clients[context.peer()]
        if not current_user:
            return chat.ServerResponse(success=False, message="[SERVER] You are not logged in")

        # Check if the receiver exists
        if request.receiver not in self.users:
            return chat.ServerResponse(success=False, message="[SERVER] User does not exist")
        
        # append to unread
        with self.users_lock:
            self.users[request.receiver]['unread'].append(request)
        return chat.ServerResponse(success=True, message="")
    
    
    # Acount Creaton
    def CreateAccount(self, request: chat.AccountInfo, context):
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
        return chat.ServerResponse(success=True, message=f"[SERVER] Account {request.username} created")
    

    # Account Login 
    # TODO: Need to fix loggin in on multiple clients
    def Login(self, request: chat.AccountInfo, context):
        # Check if the username exists
        if request.username not in self.users:
            return chat.ServerResponse(success=False, message="[SERVER] Username does not exist")
        # Check if the password is correct
        if not self.check_password(request.password, self.users[request.username]['password']):
            return chat.ServerResponse(success=False, message="[SERVER] Incorrect password")
        
        if request.username in self.users and self.users[request.username]["client"] is not None:
            detection = chat.Note(message = f"Logged out: detected {request.username} login on another client.")
            self.users[request.username]["unread"].append(detection)
            # wait for previous client to get message
            time.sleep(1)
            prev_client = self.users[request.username]["client"]
            with self.clients_lock:
                self.clients[prev_client] = None
            
        # Login the user
        self.users[request.username]['logged_in'] = True

        if context.peer() in self.clients and self.clients[context.peer()] is not None:
            prev_user = self.clients[context.peer()]
            with self.users_lock:
                self.users[prev_user]["logged_in"] = False
                self.users[prev_user]["client"] = None
        with self.clients_lock:
            self.clients[context.peer()] = request.username
        with self.users_lock:
            self.users[request.username]['client'] = context.peer()
            self.users[request.username]['logged_in'] = True

        return chat.ServerResponse(success=True, message=f"[SERVER] Logged in as {request.username}")


    # Account Logout
    def Logout(self, request: chat.Empty, context):
        print("logout")
        print(self.clients)
        print(self.users)
        # Check if the username exists
        if context.peer() not in self.clients or self.clients[context.peer()] is None:
            return chat.ServerResponse(success=False, message="[SERVER] You are not logged in")
        # Logout the user
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
        # Check if the username exists
        print("request: ")
        print(request)
        if request.username not in self.users:
            return chat.ServerResponse(success=False, message="[SERVER] Username does not exist")
        # Check if the password is correct
        if self.check_password(request.password, self.users[request.username]['password']):
            return chat.ServerResponse(success=False, message=f"[SERVER] Incorrect password for account {request.username}")
        # Delete the account
        if self.clients[context.peer()].lower() == request.username.lower():
            with self.clients_lock:
                del self.clients[context.peer()]
        with self.users_lock:
            del self.users[request.username]
        return chat.ServerResponse(success=True, message=f"[SERVER] Account {request.username} deleted")


# main thread for handling clients
if __name__ == '__main__':
    FORMAT = "utf-8"
    port = 43210
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) 
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    print('[SERVER STARTING] Listening on port ' + str(port) + '...')
    server.add_insecure_port('localhost:' + str(port))
    server.start()

    server.wait_for_termination()