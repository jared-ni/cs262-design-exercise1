import threading

import grpc

import chat_pb2 as chat
import chat_pb2_grpc as rpc

address = 'localhost'
port = 43210


class Client:
    def __init__(self, username):
        # the frame to put ui components on
        self.username = username
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)
        # create new listening thread for when new message streams come in
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        
        self.communicate_with_server()


    def __listen_for_messages(self):
        for note in self.conn.ChatStream(chat.Empty()):
            print("R[{}] {}".format(note.sender, note.message))


    def send_message(self, user, message):
        n = chat.Note()
        n.version = 1
        n.operation_code = 0
        n.sender = self.username
        n.receiver = user
        n.message = message
        
        self.conn.SendNote(n)


    def communicate_with_server(self):
        while True:
            message = input()
            firstColon = message.find(':')
            if firstColon == -1:
                print("Use: <user>: <message>")
                continue
            user = message[:firstColon]
            message = message[firstColon + 1:]

            self.send_message(user, message)


if __name__ == '__main__':
    username = ""
    while not username:
        username = input("username: ")
    c = Client(username)  # this starts a client and thus a thread which keeps connection to server open