import socket 
import threading 


SERVER = socket.gethostbyname(socket.gethostname())
PORT = 12345
FORMAT = "utf-8"
active_clients = []


# listen for upcoming messages from a client
def listen_for_messages(client, username):
    while True:

        response = client.recv(1024).decode(FORMAT)
        if response:
            final_message = f"{username} ~:> {response}"
            send_message_to_all(final_message)
        else:
            print(f"The message from client {username} is empty")


def send_message_to_client(client, message):
    client.sendall(message.encode())


def send_message_to_all(message):
    for client in active_clients:
        send_message_to_client(client[1], message)


def handle_client(client, addr):
    # listens for client message that contains username
    # log client in
    while True:
        username = client.recv(1024).decode(FORMAT)
        if username:
            active_clients.append((username, client))
            break
        else:
            print("Client username is empty")
    threading.Thread(target=listen_for_messages, args=(client, username, )).start()


# main function 
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind((SERVER, PORT))
    except:
        print(f"UNABLE TO BIND TO HOST {SERVER} AND PORT {PORT}")

    print("[SERVER STARTED]")
    server.listen()
    
    # keep listening to client connections
    while True:

        # block until new connection connected
        client, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")

        threading.Thread(target=handle_client, args=(client, addr)).start()




if __name__ == "__main__":
    main()