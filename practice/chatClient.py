import socket
import threading

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 12345
FORMAT = "utf-8"


# gets messages from server
def listen_for_server_messages(client):
    while True:
        message = client.recv(1024).decode(FORMAT)
        if message:
            username, content = message.split("~:>")
            print(f"[{username}]> {content}")
        else:
            print("The message from server is empty")


def send_message_to_server(client):
    while True:
        message = input("Message: ")
        if message:
            client.sendall(message.encode())
        else:
            print("Message cannot be empty")


# communicate with server
def communicate_to_server(client):
    username = input("Enter your username: ")
    if username:
        client.sendall(username.encode(FORMAT))
    else:
        print("Username cannot be empty")

    threading.Thread(target=listen_for_server_messages, args=(client, )).start()
    send_message_to_server(client)


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER, PORT))
        print(f"CONNECTED TO SERVER {SERVER} AND PORT {PORT}")
    except:
        print(f"UNABLE TO CONNECT TO SERVER {SERVER} AND PORT {PORT}")

    communicate_to_server(client)

if __name__ == "__main__":
    main()