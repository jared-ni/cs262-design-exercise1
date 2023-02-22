import threading
import grpc
import chat_pb2 as chat
import chat_pb2_grpc as rpc
import time 
from hashlib import blake2b
import sys
import errno
import signal
import socket

# Generate grpc server code by running 
# 'python3 -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/chat.proto'

# client-side hashing key of account password. Passwords cannot be unhashed. 
CLIENT_KEY = b'cs262IsFunAndWaldoIsCool'
FORMAT = "utf-8"

# client class for all client-side functionalities
class Client:
    def __init__(self):
        # the frame to put ui components on
        self.username = ""
        self.address = socket.gethostbyname(socket.gethostname())
        self.port = 43210

        # configure server address, if on Jared's Mac, try 10.250.151.166
        try:
            while True:
                response = input("Is the server on this machine? (yes/no) ")
                if response.lower() == 'yes':
                    break
                elif response.lower() == 'no':
                    if len(sys.argv) != 2:
                        print(sys.argv)
                        print("Usage: python3 chat_gclient.py <host>")
                        return
                    self.address = sys.argv[1]
                    break
        except KeyboardInterrupt:
            print("\n[DISCONNECTED]")
            exit(0)

        # create a gRPC channel + stub
        addr = str(self.address) + ":" + str(self.port)
        channel = grpc.insecure_channel(addr)
        self.conn = rpc.ChatServerStub(channel)

    
    # call to start everything: listening thread and the input thread
    def start(self):
        # create new listening thread for when new message streams come in
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        self.communicate_with_server()


    # listening thread for incoming messages from other users
    def __listen_for_messages(self):
        for note in self.conn.ChatStream(chat.Empty()):
            print(">[{}] {}".format(note.sender, note.message))


    # send message to server then to receiver
    def send_message(self, user, message):
        n = chat.Note()
        n.version = 1
        n.operation_code = 0
        n.sender = self.username
        n.receiver = user
        n.message = message

        # get server response and print error message if unsuccessful
        response = self.conn.SendNote(n)
        if not response.success:
            print(response.message)
            return False
        return True
    

    # register user
    def register_user(self):
        while True:
            register = input("Would you like to register for a new account? (yes/no) ")
            if register.lower() == 'yes':
                # register the user
                username = input("Username: ")
                if not username:
                    print("Username cannot be empty.")
                    continue
                # check that username doesn't contain ':'
                if ":" in username:
                    print("Username cannot contain ':'")
                    continue
                password = input("Password: ")

                re_password = input("Re-enter password: ")
                if password != re_password:
                    print("Passwords do not match.")
                    continue
                
                # send gRPC message for registering user
                n = chat.AccountInfo()
                n.username = username
                n.password = self.get_hashed_password(password)
                response = self.conn.CreateAccount(n)
                print(response.message)
                if response.success:
                    return True
                return False
            elif register.lower() == 'no':
                return False
    
    
    # login user provided by argument
    def login_user(self):
        while True:
            login = input("Would you like to log in? (yes/no) ")
            if login.lower() == 'yes':
                # log in the user
                username = input("Username: ")
                if not username:
                    print("Username cannot be empty.")
                    continue
                password = input("Password: ")
                n = chat.AccountInfo()
                n.username = username
                n.password = self.get_hashed_password(password)
                response = self.conn.Login(n)

                print(response.message)
                self.print_commands()
                if response.success:
                    self.username = username
                    return True
                else:
                    return False
            elif login.lower() == 'no':
                return False
    

    # logout user
    def logout(self):
        n = chat.Empty()
        response = self.conn.Logout(n)
        print(response.message)
        if response.success:
            self.username = ""


    # list all server accounts currently registered
    def list_accounts(self, magic_word):
        n = chat.AccountInfo()
        n.username = magic_word.strip()

        print("Current accounts:")
        for account in self.conn.ListAccounts(n):
            if not account.success:
                print("Account Listing Error")
                break
            print(account.message)
        print()
       

    # deletes an account, either provided by argument or current user
    def delete_account(self, account):
        n = chat.AccountInfo()
        if account:
            n.username = account
        else:
            n.username = self.username
        n.password = input(f"Password for account {n.username}: ")
        n.password = self.get_hashed_password(n.password)

        # get server response and print error message if unsuccessful, else print success message
        for response in self.conn.DeleteAccount(n):
            print(response.message)
            if not response.success:
                print("Account deletion failed.")
                return False
            elif response.success and n.username == self.username:
                self.username = ""
                print("Account deleted. You have been logged out.")
            elif response.success:
                print(f"Account {n.username} has been deleted.")
        return True
    

    # prints out the help menu
    def print_help(self):
        print("Commands:")
        print("\t./list <user>: list all users if <user> is empty, else list all users that contain <user>,")
        print("\t./register: register a new account,")
        print("\t./login: log in to an existing account,")
        print("\t./delete <user>: delete account <user> (<user> = current user by default),")
        print("\t./logout: disconnect from the server,")
        print("\t<user>: <message>: send a message to <user>.")


    # prints directional commands
    def print_commands(self):
        print("Commands: <user>: <message>, ./list, ./register, ./login, ./delete, ./logout. Type ./help for more info.")


    # disconnect from server
    def disconnect(self):
        self.logout()
        print("\nDisconnected from server.")
        exit(0)


    # get double-hashed password from an already hashed password
    def get_hashed_password(self, password):
        h = blake2b(key=CLIENT_KEY, digest_size=16)
        h.update(password.encode(FORMAT))
        return h.hexdigest()


    # communicate with server loop
    def communicate_with_server(self):
        # handle ctrl-z and ctrl-c
        signal.signal(signal.SIGTSTP, lambda x, y: self.disconnect())
        signal.signal(signal.SIGINT, lambda x, y: self.disconnect())

        # register user
        self.register_user()
        # login user
        logged_in = self.login_user()
        # unread is automatically loaded when user logs in
        
        while True:
            try: 
                message = input()
                if not message:
                    continue
                elif message[:8].lower() == "./delete":
                    self.delete_account(message[8:].strip().lower())
                elif message.lower() == "./help":
                    self.print_help()
                    pass
                elif message[:6].lower() == "./list":
                    # TODO: MAGIC WORD
                    self.list_accounts(message[7:].strip().lower())
                elif message.lower() == "./register":
                    successful = self.register_user()
                    time.sleep(0.5)
                    if not successful:
                        self.register_user()
                    # if not logged in and registered, login
                    elif not self.username and successful:
                        self.login_user()
                elif message.lower() == "./login":
                    self.login_user()
                elif message.lower() == "./logout":
                    self.logout()
                else:
                    firstColon = message.find(':')
                    if firstColon == -1:
                        print("Use: <user>: <message>")
                        continue
                    user = message[:firstColon]
                    message = message[firstColon + 1:]
                    self.send_message(user, message)
            except IOError as e:
                # ignore recoverable EAGAIN and EWOULDBLOCK error
                if e.errno == errno.EAGAIN and e.errno == errno.EWOULDBLOCK:
                    continue
                print('Reading error', str(e))
                self.disconnect()
            except Exception as e:
                print(e)
                self.disconnect()
    

if __name__ == '__main__':
    client = Client()  # this starts a client and thus a thread which keeps connection to server open
    client.start()