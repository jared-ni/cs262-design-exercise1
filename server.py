import socket
import threading

# put all message handling thread in separate thread, 
# so doesn't hold up other clients

# tells us the length of the message that comes next
# 64 bytes: tells us the length of the message we're receiving
HEADER = 64

PORT = 5050
# get current server's IPv4 address
SERVER = socket.gethostbyname(socket.gethostname())
# bind socket to port address, anything that connects with addr will hit this socket
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
# when we receive this message, we disconnect
DISCONNECT_MESSAGE = "!DISCONNECT"

# IPv4 address, streaming data through socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# anything that 
server.bind(ADDR)


def handle_client(conn, addr):
    print(f"[NEW CONECTION] {addr} connected.")

    connected = True
    while connected:
        # how many bytes we want to receive? blocking until receive client
        # we might send hello, or helloooooo, how do we know how much to receive? 
        # header has the protocol
        msg_length = conn.recv(HEADER).decode(FORMAT)
        # if msg not empty, we can proceed
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            
            # server sending back to client
            conn.send("Msg received".encode(FORMAT))
    
    conn.close()

# allow server to start listening to connections and pass them to handle_client in new thread
def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        # blocks until new connection, returns new socket object and address of client
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()