import threading
import socket

PORT = 11111
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!*DISCONNECT*"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


clients = set()
clients_lock = threading.Lock()


# handle client in separate thread
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try: 
        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                break
            
            print(f"[{addr}] {msg}")
            with clients_lock:
                for client in clients:
                    client.sendall(f"[{addr}] {msg}".encode(FORMAT))
    finally:
        with clients_lock:
            clients.remove(conn)
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
        with clients_lock:
            clients.add(conn)
        # new thread for each client so it doesn't block the server
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()

