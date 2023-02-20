from concurrent import futures
import grpc
import time
import chat_pb2 as chat
import chat_pb2_grpc as rpc
from collections import deque


class ChatServer(rpc.ChatServerServicer):

    def __init__(self):
        # List with all the chat history
        self.users = {}
        # maps context.peer() to username
        self.clients = {}

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
        print("sender: " + request.sender)
        print("receiver: " + request.receiver)
        print("message: " + request.message)
        print()
        current_user = self.clients[context.peer()]
        if not current_user:
            return chat.ServerResponse(success=False, message="[SERVER] You are not logged in")

        # Check if the receiver exists
        if request.receiver not in self.users:
            return chat.ServerResponse(success=False, message="[SERVER] User does not exist")
        
        # append to unread
        self.users[request.receiver]['unread'].append(request)
        print(self.users)
        return chat.ServerResponse(success=True, message="")
    
    
    # Acount Creaton
    def CreateAccount(self, request: chat.AccountInfo, context):
        # Check if the username is already taken
        if request.username in self.users:
            return chat.ServerResponse(success=False, message="[SERVER] Username already taken")
        # Create the account
        self.users[request.username] = {
            "password": request.password, 
            "client": context.peer(),
            "logged_in": False,
            "unread": deque()
        }
        print(self.users)
        return chat.ServerResponse(success=True, message=f"[SERVER] Account {request.username} created")
    

    # Account Login 
    # TODO: Need to fix loggin in on multiple clients
    def Login(self, request: chat.AccountInfo, context):
        # Check if the username exists
        if request.username not in self.users:
            return chat.ServerResponse(success=False, message="[SERVER] Username does not exist")
        # Check if the password is correct
        if self.users[request.username]['password'] != request.password:
            return chat.ServerResponse(success=False, message="[SERVER] Incorrect password")
        # Login the user
        self.users[request.username]['logged_in'] = True

        if context.peer() in self.clients and self.clients[context.peer()] is not None:
            prev_user = self.clients[context.peer()]
            self.users[prev_user]["logged_in"] = False
            self.users[prev_user]["client"] = None
        self.clients[context.peer()] = request.username
        self.users[request.username]['client'] = context.peer()
        self.users[request.username]['logged_in'] = True

        print(self.clients)
        return chat.ServerResponse(success=True, message=f"[SERVER] Logged in as {request.username}")


    # Account Logout
    def Logout(self, request: chat.Empty, context):
        # Check if the username exists
        if context.peer() not in self.clients or self.clients[context.peer()] is None:
            return chat.ServerResponse(success=False, message="[SERVER] You are not logged in")
        # Logout the user
        username = self.clients[context.peer()]
        print("Username: " + username)

        self.users[username]['logged_in'] = False
        self.users[username]['client'] = None
        del self.clients[context.peer()]

        return chat.ServerResponse(success=True, message=f"[SERVER] Logged out of user {username}")

    # Account list
    def ListAccounts(self, request: chat.AccountInfo, context):
        print("ListAccounts")
        # Lists all users in the users dict
        for user in self.users.keys():
            if request.username == "*" or not request.username or request.username in user:
                yield chat.ServerResponse(success=True, message=f"{user}")
                


if __name__ == '__main__':
    port = 43210
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) 
    rpc.add_ChatServerServicer_to_server(ChatServer(), server) 
    print('Starting server. Listening...')
    server.add_insecure_port('localhost:' + str(port))
    server.start()

    server.wait_for_termination()