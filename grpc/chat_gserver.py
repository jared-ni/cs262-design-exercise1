from concurrent import futures

import grpc
import time

import chat_pb2 as chat
import chat_pb2_grpc as rpc


class ChatServer(rpc.ChatServerServicer):

    def __init__(self):
        # List with all the chat history
        self.chats = []
        self.users = {}
        self.clients = {}

    # The stream which will be used to send new messages to clients
    # context.peer() is the unique id for the client
    def ChatStream(self, request_iterator, context):
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.chats) > lastindex:
                print(context.peer())
                n = self.chats[lastindex]
                lastindex += 1
                yield n

    def SendNote(self, request: chat.Note, context):
        # Print the message
        # print("Send: " + request.version + " " + request.sender + " " + request.receiver + " " + request.message)
        print("??")
        print(context)
        print(context.peer())
        self.chats.append(request)

        return chat.Empty()
    
if __name__ == '__main__':
    port = 43210
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) 
    rpc.add_ChatServerServicer_to_server(ChatServer(), server) 
    print('Starting server. Listening...')
    server.add_insecure_port('localhost:' + str(port))
    server.start()

    server.wait_for_termination()