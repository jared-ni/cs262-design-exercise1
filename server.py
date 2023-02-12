import threading
import socket
from collections import defaultdict

PORT = 11112
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!*DISCONNECT*"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# allows for reconnections
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)


clients = {}
clients_lock = threading.Lock()


# handle client in separate thread
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try: 
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

        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                continue
            
            if msg == DISCONNECT_MESSAGE:
                connected = False
                break
        
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
