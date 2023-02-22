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
wired protocol header definitions: 
1. version (1 bytes)
2. operation code (1 bytes)
3. header length (1 byte)
4. message length (2 bytes)
4. message data (message length bytes)
"""
# 1. version number
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
# wired protocol header sizes
p_sizes = {
    "ver": 1,
    "op": 1,
    "h_len": 1,
    "m_len": 2
}
CLIENT_KEY = b'cs262IsFunAndWaldoIsCool'
logged_in = [False]


# sends client message as per standards defined by the wired protocol
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


# continually listens to messages from server on another thread
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


# listens to messages from server on separate thread per the wired protocol.
# returns True on success, False on failure
def listen_from_server(client, logged_in):
    # unpacks header data of the message from server
    version = int.from_bytes(client.recv(p_sizes["ver"]), BYTE_ORDER)
    if not version: 
        print(f"Server/Client connection might be lost.")
        forced_disconnect(client)
    if version != VERSION:
        print(f"Server version {version} is not compatible with client version {VERSION}.")
        forced_disconnect(client)
    # 2. operation code
    operation = int.from_bytes(client.recv(p_sizes["op"]), BYTE_ORDER)
    if operation not in defined_operations:
        print(f"Operation {operation} not supported!")
        forced_disconnect(client)
    # 3. header length
    header_length = int.from_bytes(client.recv(p_sizes["h_len"]), BYTE_ORDER)
    if header_length != 5:
        print(f"Header length {header_length} not supported!")
        forced_disconnect(client)
    # 4. message length
    message_length = int.from_bytes(client.recv(p_sizes["m_len"]), BYTE_ORDER)
    # 5. message data
    message_data = client.recv(message_length).decode(FORMAT)

    # case matching based on operation code
    if operation == RECEIVE:
        username, content = message_data.split("~:>")
        print(f"([{username}] {content})")
        return True
    # if receiving from server, print differently
    elif operation == SERVER_MESSAGE or operation == REGISTER:
        print("[SERVER] " + message_data)
        return True
    elif operation == LIST:
        print(message_data)
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
    elif operation == DISCONNECT:
        logged_in[0] = False
        print("[SERVER] " + message_data)
        return False


# get hashed password
def get_hashed_password(password):
    h = blake2b(key=CLIENT_KEY, digest_size=16)
    h.update(password.encode(FORMAT))
    return h.hexdigest()


# prompts user to register an account, and returns whether or not it was successful
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
            password = get_hashed_password(password)
            send(client, f"{username}~:>{password}", REGISTER)
            return True
        elif register.lower() == 'no':
            print_commands()
            return False


# prompts user to login, and return whether or not it was successful
def login_user(client):
    while True:
        login = input("Would you like to log in? (yes/no) ")
        if login.lower() == 'yes':
            # logs in the user
            username = input("Username: ")
            if not username:
                print("Username cannot be empty.")
                continue
            password = input("Password: ")
            password = get_hashed_password(password)
            send(client, f"{username}~:>{password}", LOGIN)
            return True
        elif login.lower() == 'no':
            print_commands()
            return False


# delete the current user, and returns whether or not account is deleted
def delete_user(client, account):
    if not account and not logged_in[0]:
        print("Please login or specify the account to delete.")
        return False 

    while True:
        response = input(f"Are you sure you want to delete this account? (yes/no) ")
        if response.lower() == 'yes':
            password = input(f"Enter password: ")
            password = get_hashed_password(password)
            send(client, account + "~:>" + password, DELETE)
            time.sleep(0.5)
            return True
        elif response.lower() == 'no':
            print_commands()
            return False
        

# force disconnect from server
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
    print("\t./delete <user>: delete account <user> (<user> = current user by default),")
    print("\t./disconnect: disconnect from the server,")
    print("\t<user>: <message>: send a message to a user.")


def print_commands():
    print("Commands: <user>: <message>, ./list, ./register, ./login, ./delete, ./disconnect. Type ./help for more info.")


# attempts to connects client to server
def connect(PORT, SERVER):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER, PORT))
        print(f"Connected to {SERVER} on port {PORT}.")
        return client
    except ConnectionRefusedError:
        print('Connection refused. Check if server is running.')
        return None


# disconnects client when called
def disconnect_client(client):
    if not logged_in[0]:
        print("\n[DISCONNECTED]")
        client.close()
        time.sleep(0.5)
        exit(0)
    else:
        send(client, "", DISCONNECT)


# main function
def start():
    
    # configure the server address
    PORT = 48789
    SERVER = socket.gethostbyname(socket.gethostname())
    try:
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
    except KeyboardInterrupt:
        print("\n[DISCONNECTED]")
        exit(0)

    # returns client socket on success
    client = connect(PORT, SERVER)
    if client is None:
        return 
    # handle ctrl-z and ctrl-c
    signal.signal(signal.SIGTSTP, lambda x, y: forced_disconnect(client))
    signal.signal(signal.SIGINT, lambda x, y: forced_disconnect(client))

    # start another listening thread for server messages
    threading.Thread(target=listening_thread, args=(client, )).start()

    register_user(client)
    time.sleep(0.5)
    successful = login_user(client)
    # deliver message whenever user first logs in
    if successful:
        send(client, "", UNREAD)

    # input thread for user messages that handles different commands
    while True:
        try: 
            message = input()
            message_lower = message.lower()
            if not message:
                continue
            elif message_lower == "./help":
                print_help()
            elif message[:6] == "./list":
                # TODO: MAGIC WORD
                magic_word = message[7:].strip().lower()
                send(client, magic_word, LIST)
            elif message_lower == "./register":
                successful = register_user(client)
                time.sleep(0.5)
                if not successful:
                    register_user(client)
                elif not logged_in[0] and successful:
                    login_user(client)
            elif message_lower == "./login":
                login_user(client)
                if successful:
                    send(client, "", UNREAD)
            elif message_lower[:8] == "./delete":
                delete_user(client, message[8:].strip().lower())
            elif message_lower == "./disconnect":
                disconnect_client(client)
                break
            else:
                send(client, message, SEND)
        
        except IOError as e:
            # ignore recoverable EAGAIN and EWOULDBLOCK error
            if e.errno == errno.EAGAIN and e.errno == errno.EWOULDBLOCK:
                continue
            print('Reading error', str(e))
            forced_disconnect(client)
        except Exception as e:
            print(e)
            forced_disconnect(client)
    

if __name__ == "__main__":
    start()