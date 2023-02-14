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
SERVER_MESSAGE = 7
DISCONNECT = 8
defined_operations = set([REGISTER, LOGIN, LIST, DELETE, SEND, RECEIVE, SERVER_MESSAGE, DISCONNECT])
p_sizes = {
    "ver": 1,
    "op": 1,
    "h_len": 1,
    "m_len": 2
}

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


# Continually listens to messages from server on another thread
def listening_thread(client):
    connected = True
    while connected:
        connected = listen_from_server(client)


# a separate thread for listening to messages from server that are par the wired protocol.
# Returns True on success, False on failure
def listen_from_server(client):
    version = int.from_bytes(client.recv(p_sizes["ver"]), BYTE_ORDER)
    if version != VERSION:
        print(f"Server version {version} is not compatible with client version {VERSION}.")
        # TODO: send message to server to disconnect it
        return False
    # 2. operation code
    operation = int.from_bytes(client.recv(p_sizes["op"]), BYTE_ORDER)
    if operation not in defined_operations:
        print(f"Operation {operation} not supported!")
        # TODO: send message to client to disconnect it
        return False
    # TODO: not sure what to do with header_length
    _header_length = int.from_bytes(client.recv(p_sizes["h_len"]), BYTE_ORDER)
    # 3. message length
    message_length = int.from_bytes(client.recv(p_sizes["m_len"]), BYTE_ORDER)
    # 4. message data
    message_data = client.recv(message_length).decode(FORMAT)

    # if receiving from another client, print out
    if operation == RECEIVE:
        username, content = message_data.split("~:>")
        print(f"([{username}] {content})")
        return True
    # if receiving from server, print differently
    elif operation == SERVER_MESSAGE:
        print("[SERVER] " + message_data)
        return True
    # register op code == account registered/logged-in successfully
    elif operation == REGISTER or operation == LOGIN:
        print("[SERVER] " + message_data)
        return True
    elif operation == LIST:
        print(message_data)
        return True
    elif operation == DISCONNECT:
        print("[SERVER] " + message_data)
        return True


# prompts user to register an account
def register_user(client):
    disconnect: False
    while True:
        register = input("Would you like to register for a new account? (yes/no/disconnect) ")
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
            send(client, f"{username}~{password}", REGISTER)

            # wait for server response
            successful = False
            while not successful:
                successful = listen_from_server(client)
            break
        elif register.lower() == 'no':
            login_user(client)
        elif register.lower() == 'disconnect':
            disconnect_client(client, "disconnect", DISCONNECT)

            successful = False
            while not successful:
                successful = listen_from_server(client)
            disconnect = True
            break
    return disconnect

# prompts user to login
def login_user(client):
    disconnect = False
    while True:
        login = input("Would you like to log in? (yes/no/disconnect) ")
        if login.lower() == 'yes':
            # log in the user
            username = input("Username: ")
            if not username:
                print("Username cannot be empty.")
                continue
            password = input("Password: ")
            send(client, f"{username}~{password}", LOGIN)

            loggedIn = False
            while not loggedIn:
                loggedIn = listen_from_server(client)
            break
        elif login.lower() == 'no':
            register_user(client)
        elif login.lower() == 'disconnect':
            disconnect_client(client, "disconnect", DISCONNECT)

            successful = False
            while not successful:
                successful = listen_from_server(client)
            disconnect = True
            break
    return disconnect

def list_users(client, msg, operation_code):
    send(client, msg, operation_code)

def delete_user(client, msg, operation_code):
    while True:
        delete = input("Are you sure you want to delete your account? (yes/no) ")
        if delete.lower() == 'yes':
            password = input("Enter your password: ")
            send(client, password, DELETE)
            deleted = False
            while not deleted:
                deleted = listen_from_server(client)
            break
        elif delete.lower() == 'no':
            listen_from_server(client)

def disconnect_client(client, msg, operation_code):
    send(client, msg, operation_code)


def start():
    # returns client socket on success
    client = connect()
    if client is None:
        return 
    
    if register_user(client):
        return
    if login_user(client):
        return

    # start another listening thread for server messages
    threading.Thread(target=listening_thread, args=(client, )).start()
    # input thread for user messages
    disconnected = False
    while not disconnected:
        message = input()
        if message:
            if message == "./list":
                list_users(client, message, LIST)
            elif message == "./delete": 
                delete_user(client, message, DELETE)
                register_user(client)
            elif message == "./disconnect":
                disconnect_client(client, message, DISCONNECT)
                disconnected = True
            else:
                send(client, message, SEND)


if __name__ == "__main__":
    start()