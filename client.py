import threading
import socket
import time

PORT = 11112
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
BYTE_ORDER = "big"

"""
wired protocol definitions: 
1. version (1 bytes)
2. operation code (1 bytes)
3. header length (1 byte)
4. message length (2 bytes)
4. message data (message length bytes)
"""
# 1. version
VERSION = 1
# 2. operation_codes
REGISTER = 1
LOGIN = 2
LIST = 3
DELETE = 4
SEND = 5
RECEIVE = 6
DISCONNECT = 7
defined_operations = set([REGISTER, LOGIN, LIST, DELETE, SEND, RECEIVE, DISCONNECT])

# 1. connect client to server
def connect():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        print(f"Connected to {SERVER} on port {PORT}.")
    except ConnectionRefusedError:
        print('Connection refused. Check if server is running.')
        return None
    return client


# send client message as per standards defined by the wired protocol
def send(client, msg, operation_code):
    # 1. version
    version = VERSION.to_bytes(1, BYTE_ORDER)
    # 2. operation code
    operation = operation_code.to_bytes(1, BYTE_ORDER)
    # 4. message data and message length
    message = msg.encode(FORMAT)
    message_length = len(message).to_bytes(2, BYTE_ORDER)
    # 3. header length 
    header_length = (1 + len(version) + len(operation) + len(message_length)).to_bytes(1, BYTE_ORDER)
    # 5. send message
    client.send(version + operation + header_length + message_length + message)


# listens to messages on another thread while allowing user to send messages
def communicate_to_server(client):

    threading.Thread(target=listen_for_server_messages, args=(client, )).start()
    while True:
        message = input()
        if message:
            send(client, message, SEND)


def listen_for_server_messages(client):
    while True:
        message = client.recv(1024).decode(FORMAT)
        if message:
            username, content = message.split("~:>")
            print(f"[{username}]> {content}")

def start():
    # returns client socket on success
    client = connect()
    if client is None:
        return 
    
    # ask the user if they want to register or log in
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


            send(client, f"register~{username}~{password}", REGISTER)



            # wait for server response
            registered = False
            while not registered:
                message = client.recv(1024).decode(FORMAT)
                if message:
                    print(message)
                    if "Successfully" in message:
                        registered = True
                    print(registered)
            if registered:
                break
        elif register.lower() == 'no':
            break

    # log in the user
    while True:
        login = input("Would you like to log in? (yes/no) ")
        if login.lower() == 'yes':
            # log in the user
            username = input("Username: ")
            if not username:
                print("Username cannot be empty.")
                continue
            password = input("Password: ")
            send(client, f"login~{username}~{password}", LOGIN)
            loggedin = False
            while not loggedin:
                message = client.recv(1024).decode(FORMAT)
                if message:
                    print(message)
                    if "Successfully" in message:
                        loggedin = True
            if loggedin:
                break
        elif login.lower() == 'no':
            message = client.recv(1024).decode(FORMAT)
            if message:
                print(message)
                break
    print("CHECK POINT")
    communicate_to_server(client)

    # wait for server response
    # while True:
    #     msg = input("Message (q for quit): ")
    #     if msg == 'q':
    #         break
    #     send(client, msg)

    # send(client, DISCONNECT_MESSAGE)
    # time.sleep(1)
    # print('Disconnected from server.')


start()