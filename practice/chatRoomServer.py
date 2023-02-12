import threading
import socket 
import select

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# allows for reconnections
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()
print(f"[START SERVER] Listening for connections on {IP}:{PORT}...")

sockets_list = [server_socket]

# clients' sockets will be key, user data will be value
clients = {}


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        # if no header, close connection 
        if not len(message_header):
            return False
        # decode the message header
        message_length = int(message_header.decode('utf-8').strip())
        
        # TODO: handle oversized language

        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False
    
while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # if server, accept new connections
        if notified_socket == server_socket:


            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue
                
            sockets_list.append(client_socket)

            clients[client_socket] = user

            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")

        # if not server, receive message
        else:
            message = receive_message(notified_socket)
            if not message:
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            
            user = clients[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            # send to target
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]