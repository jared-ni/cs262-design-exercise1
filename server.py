import threading
import socket
import time
import bcrypt
from collections import deque

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
5. message data (message length bytes)
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
UNREAD = 8
DISCONNECT = 9
defined_operations = set([REGISTER, LOGIN, LIST, DELETE, SEND, RECEIVE, 
                          SERVER_MESSAGE, UNREAD, DISCONNECT])
p_sizes = {
    "ver": 1,
    "op": 1,
    "h_len": 1,
    "m_len": 2
}


# bind server to current address and allow for reconnections
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

# dictionary for storing user information
users = {}
users_lock = threading.Lock()
# dictionary for storing clients. maps socket to user
clients = {}
clients_lock = threading.Lock()


# send message to client as per standards defined by the wired protocol
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


# hash password again for storage
def hash_password(password):
    return bcrypt.hashpw(password.encode(FORMAT), bcrypt.gensalt())

# return true if password matches hashed password
def check_password(password, hashed_password):
    # print(hashed_password)
    return bcrypt.checkpw(password.encode(FORMAT), hashed_password)


# handle account registration and login
def handle_register(client, payload):
    if not payload:
        return
    try:
        username, password = payload.split("~")
        # if username already exists, send error message
        if username in users:
            send(client, "Username already exists!", SERVER_MESSAGE)
            return
        # add new user to clients dictionary
        with users_lock:
            users[username] = {
                # TODO: hash password
                "password": hash_password(password),
                "client": client,
                "logged_in": False,
                "messages": [],
                "unread": deque()
            }
        send(client, f"Successfully registered {username}!", REGISTER)
    except ValueError:
        return
    

# handle account login
def handle_login(client, payload):
    print(f"handle_login: {client}, {payload}")
    if not payload:
        return 
    try:
        username, password = payload.split("~")
        # if username doesn't exist, send error message
        if username not in users:
            send(client, "Username does not exist!", SERVER_MESSAGE)
            return
        # TODO: hash password
        if not check_password(password, users[username]["password"]):
            send(client, "Incorrect password!", SERVER_MESSAGE)
            return
        
        # TODO: lock clients dictionary
        with users_lock:
            users[username]["logged_in"] = True
        # if user was previously logged in, log them out
        with clients_lock:
            if client in clients:
                prev_user = clients[client]
                with users_lock:
                    users[prev_user]["logged_in"] = False
                    users[prev_user]["client"] = None
            # save client's current logged in username, and save client in users dictionary
            clients[client] = username
            with users_lock:
                users[username]["logged_in"] = True
                users[username]["client"] = client

        send(client, f"Successfully logged in {username}!", LOGIN)
    except:
        return
    

# handle sending messages
def handle_send(client, payload):
    print(f"handle_send: {client}, {payload}")

    if client not in clients:
        send(client, "You are not logged in! Type ./help for instructions.", SERVER_MESSAGE)
        return
    if not payload:
        return
    
    # try:
        # get receiver and message
    receiverEnd = payload.find(":")
    message = payload[receiverEnd+1:]
    if receiverEnd == -1 or not message:
        send(client, "Syntax for sending a message to a user: <username>: <message>. Type ./help for additional commands.", SERVER_MESSAGE)
        return
    receiver = payload[:receiverEnd]
    if receiver not in users:
        send(client, f"User {receiver} does not exist!", SERVER_MESSAGE)
        return

    print("message: " + receiver + " " + message)
    # send message to receiver
    # TODO: what to do when receiver is not logged in?
    with users_lock:
        receiver_socket = users[receiver]["client"]
        if not users[receiver]["logged_in"]:
            users[receiver]["unread"].appendleft(f"{clients[client]}~:>{message}")
        else:
            send(receiver_socket, f"{clients[client]}~:>{message}", RECEIVE)

    # except Exception as e:
    #     print(e)
    #     client.send(f"Error: {e} on line {e.args}".encode(FORMAT))
    #     return


# handles unread messages by sending them to the client
def handle_unread(client):
    # check if user is logged in
    if client not in clients:
        send(client, "You are not logged in! Type ./help for instructions.", SERVER_MESSAGE)
        return
    # get unread messages from user account
    username = clients[client]
    # send unread messages to client
    with users_lock:
        while users[username]["unread"]:
            message = users[username]["unread"].pop()
            send(client, message, RECEIVE)
    return True



# print out all users registered
def handle_list(client, payload):
    print(f"handle_list: {client}, {payload}")
    
    # Lists all users in the users dict
    send(client, f"List of users:", LIST)
    for user in users:
        send(client, f"{user}", LIST)


# delete current user's account
def handle_delete(client, payload):
    print(f"handle_delete: {client}, {payload}")
    
    if client not in clients:
        send(client, "You are not logged in! Type ./help for instructions.", SERVER_MESSAGE)
        return

    username = clients[client]
    if not check_password(payload, users[username]["password"]):
        send(client, "Incorrect password!", SERVER_MESSAGE)
        return
    else:
        with users_lock:
            del users[username]
        send(client, f"Successfully deleted user {username}", DELETE)


# handle disconnect
def handle_disconnect(client):
    if client not in clients:
        send(client, "You are not logged in! Type ./help for instructions.", SERVER_MESSAGE)
        return
    
    username = clients[client]
    # TODO: make user handle multiple client logins
    with users_lock:
        if username and username in users:
            users[username]["client"] = None
            users[username]["logged_in"] = False
            del clients[client]

    send(client, "[CLIENT DISCONNECTED]", DISCONNECT)
    time.sleep(2)
    client.close()


# handle client in separate thread
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try: 
        connected = True
        while connected:
            # Parse wired protocol header
            # TODO: need to break when get disconnect message
            # 1. client version number must match server version number
            version = int.from_bytes(conn.recv(p_sizes["ver"]), BYTE_ORDER)
            if version != VERSION:
                print(f"Version {version} not supported!")
                # TODO: send message to client to disconnect it
                return
            # 2. operation code
            operation = int.from_bytes(conn.recv(p_sizes["op"]), BYTE_ORDER)
            if operation not in defined_operations:
                print(f"Operation {operation} not supported!")
                # TODO: send message to client to disconnect it
                return 
            # TODO: not sure what to do with header_length
            _header_length = int.from_bytes(conn.recv(p_sizes["h_len"]), BYTE_ORDER)
            # 3. message length
            message_length = int.from_bytes(conn.recv(p_sizes["m_len"]), BYTE_ORDER)
            # 4. message data
            message_data = conn.recv(message_length).decode(FORMAT)

            # handle specific operation
            if operation == REGISTER:
                handle_register(conn, message_data)
            elif operation == LOGIN:
                handle_login(conn, message_data)
            elif operation == SEND:
                handle_send(conn, message_data)
            elif operation == LIST:
                handle_list(conn, message_data)
            elif operation == DELETE:
                handle_delete(conn, message_data)
            elif operation == UNREAD:
                handle_unread(conn)
            elif operation == DISCONNECT:
                raise Exception

    except:
        # TODO: What do we do when client disconnects?
        print(f"[{addr}] disconnected.")
        handle_disconnect(conn)


# handle clients
def start():
    print("[SERVER STARTED]!")
    server.listen()
    while True:
        # block until new connection 
        conn, addr = server.accept()
        # locks client data structure when adding new client
        # with clients_lock:
        #     clients.add(conn)
        # new thread for each client so it doesn't block the server
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start()
