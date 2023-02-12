import threading
import socket
import time

PORT = 11112
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!*DISCONNECT*"

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


def send(client, msg):
    message = msg.encode(FORMAT)
    client.send(message)


def start():
    # ask user if they want to connect
    answer = input('Would you like to connect? (yes/no) ')
    if answer.lower() != 'yes':
        return 

    # returns client socket on success
    client = connect()
    if client is None:
        return 
    
    # ask the user if they want to register or log in
    while True:
        register = input("Would you like to register for a new account? (yes/no) ")
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
            send(client, f"register~{username}~{password}")
            # wait for server response
            while True:
                message = client.recv(1024).decode(FORMAT)
                if message:
                    print(message)
                    break
        elif register.lower() == 'no':
            break

    # log in the user
    while True:
        login = input("Would you like to log in? (yes/no) ")
        if login.lower() == 'yes':
            # log in the user
            username = input("Username: ")
            if not username:
                print("Username cannot be empty.")
                continue
            password = input("Password: ")
            send(client, f"login~{username}~{password}")
            break

        else:
            continue

    # wait for server response
    while True:
        msg = input("Message (q for quit): ")
        if msg == 'q':
            break
        send(client, msg)

    send(client, DISCONNECT_MESSAGE)
    time.sleep(1)
    print('Disconnected from server.')


start()