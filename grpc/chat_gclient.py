import threading
import grpc
import chat_pb2 as chat
import chat_pb2_grpc as rpc
import time 

address = 'localhost'
port = 43210


class Client:
    def __init__(self):
        # the frame to put ui components on
        self.username = ""
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)
        # create new listening thread for when new message streams come in
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        
        self.communicate_with_server()


    def __listen_for_messages(self):
        for note in self.conn.ChatStream(chat.Empty()):
            print("R[{}] {}".format(note.sender, note.message))


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
                password = input("Password: ")

                re_password = input("Re-enter password: ")
                if password != re_password:
                    print("Passwords do not match.")
                    continue
                # TODO: Hash password
                # AccountInfo
                n = chat.AccountInfo()
                n.username = username
                n.password = password
                response = self.conn.CreateAccount(n)
                print(response.message)
                if response.success:
                    return True
                return False
            elif register.lower() == 'no':
                return False
    
    
    # login user
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
                n.password = password
                response = self.conn.Login(n)

                print(response.message)
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
        if response.success:
            self.username = ""
        print(response.message)


    # list accounts
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
       
    # deletes an account
    def delete_account(self, account):
        n = chat.AccountInfo()
        if account:
            n.username = account
        else:
            n.username = self.username
        password = input(f"Password for account {}: ")
        response = self.conn.DeleteAccount(n)
        if response.success:
            self.username = ""
        print(response.message)


    # communicate with server loop
    def communicate_with_server(self):
        # register user
        self.register_user()
        # login user
        logged_in = self.login_user()
        if logged_in:
            # TODO: self.load_unread()
            pass

        while True:
            message = input()
            if not message:
                continue
            elif message[:8].lower() == "./delete":
                self.delete_account(message[8:].strip().lower())
            elif message.lower() == "./help":
                # print_help()
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


if __name__ == '__main__':
    Client()  # this starts a client and thus a thread which keeps connection to server open