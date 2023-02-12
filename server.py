import threading
import socket

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

# dictionary for storing client connections
clients = {}
clients_lock = threading.Lock()

# handle account registration and login
def handle_account(conn):
    # registration (optional)
    account = conn.recv(1024).decode(FORMAT)
    if account:
        reg_type, username, password = account.split("~")
        if reg_type == "register":
            if username in clients:
                # if username already exists, send error message
                conn.sendall("Username already exists!".encode(FORMAT))
                return
            # add new user to clients dictionary
            clients[username] = {
                "password": password.encode(FORMAT), 
                "client": conn
            }
            conn.send(f"Successfully registered {username}!".encode(FORMAT))
        elif reg_type == "login":
            if username not in clients:
                # if username doesn't exist, send error message
                conn.sendall("Username does not exist!".encode(FORMAT))
                return
            if clients[username]["password"] != password.encode(FORMAT):
                # if password is incorrect, send error message
                conn.sendall("Incorrect password!".encode(FORMAT))
                return
            conn.send(f"Successfully logged in {username}!".encode(FORMAT))
    return username

# handle client in separate thread
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try: 
        # Parse wired protocol header
        # 1. version
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
        header_length = int.from_bytes(conn.recv(p_sizes["h_len"]), BYTE_ORDER)
        # 3. message length
        message_length = int.from_bytes(conn.recv(p_sizes["m_len"]), BYTE_ORDER)
        # 4. message data
        message_data = conn.recv(message_length).decode(FORMAT)

        print(f"version: {version}")
        print(f"operation: {operation}")
        print(f"header_length: {header_length}")
        print(f"message_length: {message_length}")
        print(f"message_data: {message_data}")


        handle_account(conn)
        username = handle_account(conn)

        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                continue
            
            # TODO: need to break when get disconnect message
        
            # find receiver and message
            print(f"[{addr, username}] {msg}")

            receiverEnd = msg.find(":")
            receiver = msg[:receiverEnd]
            message = msg[receiverEnd+1:]

            if receiver not in clients:
                continue
            receiver_socket = clients[receiver]["client"]
            receiver_socket.send(f"[{username}] ~:> {message}".encode(FORMAT))

    finally:
        # with clients_lock:
        #     clients.remove(conn)
        print(f"[{addr}] disconnected.")
        conn.close()


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

start()
