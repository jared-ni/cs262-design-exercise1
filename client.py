import socket 

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
# how do we not hardcode the server address if running on two machines? 
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    # pad with spaces to make sure we send 64 bytes
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

    # receiving message from server. Also use the header protocol. 
    print(client.recv(2048).decode(FORMAT))



send("Hello world")
input()
send("Hello Everyone!")
input()
send("hello Jared!")
input()
send(DISCONNECT_MESSAGE)