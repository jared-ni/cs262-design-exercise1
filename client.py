import threading
import socket
import time

PORT = 48789
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

logged_in = False

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
    elif operation == REGISTER:
        print("[SERVER] " + message_data)
        return True
    elif operation == LOGIN:
        logged_in = True
        print("[SERVER] " + message_data)
        print("Commands: ./list, ./register, ./login, ./delete, ./disconnect, <user>: <message>. Type ./help for more info.")
        return True
    elif operation == LIST:
        print(message_data)
        return True
    elif operation == DISCONNECT:
        logged_in = False
        print("[SERVER] " + message_data)
        return False


# prompts user to register an account. Returns whether disconnected
def register_user(client):
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
            return False
        elif register.lower() == 'no':
            return False
        elif register.lower() == 'disconnect':
            send(client, "", DISCONNECT)
            return True


# prompts user to login. Return whether user disconnected
def login_user(client):
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
            return False
        elif login.lower() == 'no':

            return False
        elif login.lower() == 'disconnect':
            send(client, "", DISCONNECT)
            return True


# lists the current accounts on the server
def list_users(client, msg, operation_code):
    send(client, msg, operation_code)


# delete the current user. Return whether account is deleted
def delete_user(client):
    if not logged_in:
        print("You are not logged in.")
        return False
    while True:
        response = input("Are you sure you want to delete your account? (yes/no) ")
        if response.lower() == 'yes':
            password = input("Enter your password: ")
            send(client, password, DELETE)
            time.sleep(0.5)
            return True
        elif response.lower() == 'no':
            return False


# delete the current user. Return whether account is deleted
def disconnect_client(client):
    while True:
        response = input("Are you sure you want to disconnect? (yes/no) ")
        if response.lower() == 'yes':
            send(client, "", DISCONNECT)
            return True
        elif response.lower() == 'no':
            return False


def print_help():
    print("Commands:")
    print("\t./list: list all users,")
    print("\t./register: register a new account,")
    print("\t./login: log in to an existing account,")
    print("\t./delete: delete your account,")
    print("\t./disconnect: disconnect from the server,")
    print("\t<user>: <message>: send a message to a user.")

# main function
def start():
    # returns client socket on success
    client = connect()
    if client is None:
        return 
    
    # start another listening thread for server messages
    threading.Thread(target=listening_thread, args=(client, )).start()

    register_user(client)
    time.sleep(0.5)
    login_user(client)

    # input thread for user messages
    disconnected = False
    while not disconnected:
        message = input().lower()
        if message:
            if message == "./help":
                print_help()
            elif message == "./list":
                list_users(client, message, LIST)
            elif message == "./register":
                register_user(client)
            elif message == "./login":
                login_user(client)
            elif message == "./delete":
                if not logged_in:
                    print("You are not logged in.")
                    continue
                if delete_user(client):
                    register_user(client)
                    login_user(client)
            elif message == "./disconnect":
                if not logged_in:
                    print("You are not logged in.")
                    continue
                send(client, False, DISCONNECT)
            else:
                send(client, message, SEND)


if __name__ == "__main__":
    start()