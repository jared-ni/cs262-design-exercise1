import threading
import socket
import time
from hashlib import blake2b
from sys import exit 
import signal
import errno
import sys


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
SERVER_MESSAGE = 7
UNREAD = 8
DISCONNECT = 9
defined_operations = set([REGISTER, LOGIN, LIST, DELETE, SEND, RECEIVE, SERVER_MESSAGE, UNREAD, DISCONNECT])
p_sizes = {
    "ver": 1,
    "op": 1,
    "h_len": 1,
    "m_len": 2
}
CLIENT_KEY = b'cs262IsFunAndWaldoIsCool'

logged_in = [False]


# send client message as per standards defined by the wired protocol
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
    except BrokenPipeError or OSError:
        print("Connection to server lost.")
        logged_in[0] = False
        forced_disconnect(client)
    except Exception as e:
        # recoverable EAGAIN and EWOULDBLOCK error: try again
        if e.errno == errno.EAGAIN and e.errno == errno.EWOULDBLOCK:
            return
        print('Sending error', str(e))
        forced_disconnect(client)

# Continually listens to messages from server on another thread
def listening_thread(client):
    connected = True
    while connected:
        try: 
            connected = listen_from_server(client, logged_in)
        except ConnectionAbortedError or KeyboardInterrupt:
            print("Connection to server lost.")
            logged_in[0] = False
            forced_disconnect(client)
        except IOError as e:
            # ignore recoverable EAGAIN and EWOULDBLOCK error
            if e.errno == errno.EAGAIN and e.errno == errno.EWOULDBLOCK:
                continue
            print('Reading error', str(e))
            forced_disconnect(client)
        except Exception as e:
            forced_disconnect(client)


# a separate thread for listening to messages from server that are par the wired protocol.
# Returns True on success, False on failure
def listen_from_server(client, logged_in):
    version = int.from_bytes(client.recv(p_sizes["ver"]), BYTE_ORDER)
    if not version: 
        print(f"Server/Client connection might be lost.")
        forced_disconnect(client)
    if version != VERSION:
        print(f"Server/Client connection might be lost, or server version {version} is not compatible with client version {VERSION}.")
        forced_disconnect(client)
    # 2. operation code
    operation = int.from_bytes(client.recv(p_sizes["op"]), BYTE_ORDER)
    if operation not in defined_operations:
        print(f"Operation {operation} not supported!")
        forced_disconnect(client)
    # TODO: not sure what to do with header_length
    _header_length = int.from_bytes(client.recv(p_sizes["h_len"]), BYTE_ORDER)
    # 3. message length
    message_length = int.from_bytes(client.recv(p_sizes["m_len"]), BYTE_ORDER)
    # 4. message data
    message_data = client.recv(message_length).decode(FORMAT)

    # if receiving from another client, print out
    if operation == RECEIVE:
        username, content = message_data.split("~:>")
        print(f"([{username}] {content})")
        return True
    # if receiving from server, print differently
    elif operation == SERVER_MESSAGE:
        print("[SERVER] " + message_data)
        return True
    # register op code == account registered/logged-in successfully
    elif operation == REGISTER:
        print("[SERVER] " + message_data)
        return True
    elif operation == LOGIN:
        logged_in[0] = True
        print("[SERVER] " + message_data)
        print_commands()
        return True
    elif operation == DELETE:
        logged_in[0] = False
        print("[SERVER] " + message_data)
        return True
    elif operation == LIST:
        print(message_data)
        return True
    elif operation == DISCONNECT:
        logged_in[0] = False
        print("[SERVER] " + message_data)
        return False


# get hashed password
def get_hashed_password(password):
    h = blake2b(key=CLIENT_KEY, digest_size=16)
    h.update(password.encode(FORMAT))
    return h.hexdigest()


# prompts user to register an account. Returns whether successful
def register_user(client):
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
            # TODO: Hash password
            password = get_hashed_password(password)
            send(client, f"{username}~{password}", REGISTER)
            return True
        elif register.lower() == 'no':
            print_commands()
            return False


# prompts user to login. Return whether successful
def login_user(client):
    while True:
        login = input("Would you like to log in? (yes/no) ")
        if login.lower() == 'yes':
            # log in the user
            username = input("Username: ")
            if not username:
                print("Username cannot be empty.")
                continue
            password = input("Password: ")
            password = get_hashed_password(password)
            send(client, f"{username}~{password}", LOGIN)
            return True
        elif login.lower() == 'no':
            print_commands()
            return False


# delete the current user. Return whether account is deleted
def delete_user(client):
    if not logged_in[0]:
        print("You are not logged in.")
        return False
    while True:
        response = input("Are you sure you want to delete your account? (yes/no) ")
        if response.lower() == 'yes':
            password = input("Enter your password: ")
            password = get_hashed_password(password)
            send(client, password, DELETE)
            time.sleep(0.5)
            return True
        elif response.lower() == 'no':
            print_commands()
            return False


# delete the current user. Return whether account is deleted
def disconnect_client(client):
    while True:
        response = input("Are you sure you want to disconnect? (yes/no) ")
        if response.lower() == 'yes':
            send(client, "", DISCONNECT)
            return True
        elif response.lower() == 'no':
            print_commands()
            return False
        
# forced disconnect from server
def forced_disconnect(client):
    print("\nDisconnected from server.")
    send(client, "", DISCONNECT)
    time.sleep(0.5)
    client.close()
    exit(0)

# prints out the help menu
def print_help():
    print("Commands:")
    print("\t./list: list all users,")
    print("\t./register: register a new account,")
    print("\t./login: log in to an existing account,")
    print("\t./delete: delete your account,")
    print("\t./disconnect: disconnect from the server,")
    print("\t<user>: <message>: send a message to a user.")

def print_commands():
    print("Commands: <user>: <message>, ./list, ./register, ./login, ./delete, ./disconnect. Type ./help for more info.")


# main function
def start():
    # checks for host import
    PORT = 48789
    SERVER = socket.gethostbyname(socket.gethostname())
    print(f"Server IP: {SERVER}")

    # configure the server address
    while True:
        response = input("Is the server on this machine? (yes/no) ")
        if response.lower() == 'yes':
            break
        elif response.lower() == 'no':
            if len(sys.argv) != 2:
                print(sys.argv)
                print("Usage: python3 client.py <host>")
                return
            SERVER = sys.argv[1]
            break

    # returns client socket on success
    client = connect(PORT, SERVER)
    if client is None:
        return 
    
    # handle ctrl-z
    signal.signal(signal.SIGTSTP, lambda x, y: forced_disconnect(client))
    # start another listening thread for server messages
    threading.Thread(target=listening_thread, args=(client, )).start()

    try:
        register_user(client)
        time.sleep(0.5)
        successful = login_user(client)
        # deliver message whenever user first logs in
        if successful:
            send(client, "", UNREAD)
        # input thread for user messages
        disconnected = False
        while not disconnected:
            message = input().lower()
            if message:
                if message == "./help":
                    print_help()
                elif message[:6] == "./list":
                    # TODO: MAGIC WORD
                    magic_word = message[7:].strip().lower()
                    send(client, magic_word, LIST)
                elif message == "./register":
                    successful = register_user(client)
                    time.sleep(0.5)
                    if not successful:
                        register_user(client)
                    elif not logged_in[0] and successful:
                        login_user(client)
                elif message == "./login":
                    login_user(client)
                    if successful:
                        send(client, "", UNREAD)
                elif message == "./delete":
                    if not logged_in[0]:
                        print("You are not logged in.")
                        continue
                    delete_user(client)
                    if not logged_in[0]:
                        register_user(client)
                        login_user(client)
                elif message == "./disconnect":
                    if not logged_in[0]:
                        print("You are not logged in.")
                        continue
                    send(client, "", DISCONNECT)
                    break
                else:
                    send(client, message, SEND)
    # handle ctrl-c quit 
    except KeyboardInterrupt:
        print("Disconnecting from server...")
        forced_disconnect(client)
    except Exception as e:
        print(e)
        forced_disconnect(client)


# 1. connect client to server
def connect(PORT, SERVER):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER, PORT))
        print(f"Connected to {SERVER} on port {PORT}.")
        return client
    except ConnectionRefusedError:
        print('Connection refused. Check if server is running.')
        return None



if __name__ == "__main__":
    start()