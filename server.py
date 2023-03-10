import threading
import socket
import time
import bcrypt
import errno
from collections import deque

PORT = 48789
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
BYTE_ORDER = "big"

"""
wired protocol header definitions: 
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
# wired protocol header sizes
p_sizes = { "ver": 1, "op": 1, "h_len": 1, "m_len": 2 }


# bind server to current address and allow for reconnections
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

# dictionary for storing user information
users = {}
# dictionary for storing clients and maps socket to user
clients = {}
# locks for preventing race conditions in users and clients
users_lock = threading.Lock()
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
    try: 
        client.send(version + operation + header_length + message_length + message)
    except ConnectionResetError or BrokenPipeError:
        return


# hash password again: server side encryption
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
        username, password = payload.split("~:>")
        # if username already exists, send error message
        if username in users:
            send(client, "Username already exists!", SERVER_MESSAGE)
            return
        # add new user to clients dictionary
        with users_lock:
            users[username] = {
                # hashed password
                "password": hash_password(password),
                "client": None,
                "logged_in": False,
                "unread": deque()
            }
        send(client, f"Successfully registered {username}!", REGISTER)
    except ValueError or IndexError or BrokenPipeError:
        return
    

# handle account login: sends to client's listening thread whether server-side login was successful
def handle_login(client, payload):
    if not payload:
        return 
    try:
        username, password = payload.split("~:>")
        # if username doesn't exist, send error message
        if username not in users:
            send(client, "Username does not exist!", SERVER_MESSAGE)
            return
        # hashes password
        if not check_password(password, users[username]["password"]):
            send(client, "Incorrect password!", SERVER_MESSAGE)
            return
        
        # locks clients dictionary when changing global dictionary
        with users_lock:
            users[username]["logged_in"] = True
        # if client was previously logged in, log them out
        # logs out user on previous client
        if username in users and users[username]["client"] is not None:
            prev_client = users[username]["client"]
            with clients_lock:
                clients[prev_client] = None
            send(prev_client, f"Logged out: detected {username} login on another client.", DISCONNECT)

        with clients_lock:
            if client in clients and clients[client] is not None:
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
    

# handle sending messages between two users
# send message to receiver immediately if they are logged in
# adds message to receiver's unread array if receiver is not logged in
def handle_send(client, payload):
    # check if sender is logged in
    if client not in clients:
        send(client, "You are not logged in! Type ./help for instructions.", SERVER_MESSAGE)
        return
    # if no message, return
    if not payload:
        return
    
    # get receiver and message
    receiverEnd = payload.find(":")
    message = payload[receiverEnd+1:]
    if receiverEnd == -1 or not message:
        send(client, "Syntax for sending a message to a user: <username>: <message>. Type ./help for additional commands.", 
             SERVER_MESSAGE)
        return
    receiver = payload[:receiverEnd]
    if receiver not in users:
        send(client, f"User {receiver} does not exist!", SERVER_MESSAGE)
        return
    
    # send message to receiver
    try:
        with users_lock:
            receiver_socket = users[receiver]["client"]
            if not users[receiver]["logged_in"]:
                users[receiver]["unread"].appendleft(f"{clients[client]}~:>{message}")
            else:
                send(receiver_socket, f"{clients[client]}~:>{message}", RECEIVE)

    except KeyError or TypeError or AttributeError or BrokenPipeError:
        send(client, f"Please check the format of your message. Type ./help for help. ", SERVER_MESSAGE)
        return


# handles unread messages by sending them to the client
def handle_unread(client):
    # check if user is logged in
    if client not in clients or clients[client] is None:
        send(client, "You are not logged in! Type ./help for instructions.", SERVER_MESSAGE)
        return
    # get unread messages from user account
    username = clients[client]
    # send unread messages to client
    with users_lock:
        while users[username]["unread"]:
            try: 
                message = users[username]["unread"].pop()
                send(client, message, RECEIVE)
            except IOError as e:
                if e.errno == errno.EAGAIN and e.errno == errno.EWOULDBLOCK:
                    continue
            except BrokenPipeError:
                break
    return


# print out all users registered with text wildcard
def handle_list(client, payload):
    if not payload or payload == "*":
        # Lists all users in the users dict
        send(client, f"List of users:", LIST)
        for user in users:
            send(client, f"{user}", LIST)
    else:
        # Lists all users in the users dict that contain the payload
        send(client, f"List of users that contain {payload}:", LIST)
        magic_word_size = len(payload)
        for user in users:
            # continue if username is too short
            if magic_word_size > len(user):
                continue
            
            if payload in user:
                send(client, f"{user}", LIST)


# delete current user's account
def handle_delete(client, payload):
    try: 
        username, password = payload.split("~:>")
        if not username and client in clients:
            print("!")
            username = clients[client]
        if not username or username not in users:
            print("!!")
            send(client, f"Account {username} does not exist!", SERVER_MESSAGE)
            return
        if not check_password(password, users[username]["password"]):
            print("!!!")
            send(client, f"Incorrect password for account {username}!", SERVER_MESSAGE)
            return
        else:
            # if deleting current client's account, log them out
            if client in clients and clients[client] == username:
                send(client, f":::", DELETE)

            # log out of the deleted_user's client
            with clients_lock:
                deleted_client = users[username]["client"]
                if deleted_client is not None:
                    send(deleted_client, f"Logged out: Account {username}", DELETE)
                    del clients[deleted_client]
            # actually deleting the user
            with users_lock:
                del users[username]
            send(client, f"Successfully deleted user {username}", DELETE)

    except Exception as e:
        print(e)
        send(client, f"Syntax for deleting an account: ./delete <username>", SERVER_MESSAGE)


# handle disconnect
def handle_disconnect(client):
    # check if user is logged in
    if client not in clients:
        send(client, "You are not logged in! Type ./help for instructions.", SERVER_MESSAGE)
        return
    # deleting client from clients dictionary
    try: 
        username = clients[client]
        with users_lock:
            if username and username in users:
                users[username]["client"] = None
                users[username]["logged_in"] = False
                del clients[client]
        send(client, "[CLIENT DISCONNECTED]", DISCONNECT)
    
    except ValueError or KeyError or Exception as e:
        print(e)
        return


# handle client in separate thread
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    with clients_lock:
        clients[conn] = None

    while True:
        try: 
            # parse wired protocol header
            # 1. client version number must match server version number
            version = int.from_bytes(conn.recv(p_sizes["ver"]), BYTE_ORDER)
            if version != VERSION:
                print(f"Version {version} not supported!")
                return
            # 2. operation code
            operation = int.from_bytes(conn.recv(p_sizes["op"]), BYTE_ORDER)
            if operation not in defined_operations:
                print(f"Operation {operation} not supported!")
                return 
            # 3. header length
            header_length = int.from_bytes(conn.recv(p_sizes["h_len"]), BYTE_ORDER)
            if header_length != 5:
                print(f"Header length {header_length} not supported!")
            # 4. message length
            message_length = int.from_bytes(conn.recv(p_sizes["m_len"]), BYTE_ORDER)
            # 5. message data
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
                handle_disconnect(conn)

        # handle recoverable errors
        except IOError as e:
            if e.errno == errno.EAGAIN and e.errno == errno.EWOULDBLOCK:
                continue
        except:
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
        # new thread for each client so it doesn't block the server
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start()