from concurrent import futures
import time

import grpc
import gchat_pb2
import gchat_pb2_grpc

class Chat(gchat_pb2_grpc.ChatServicer):
    def SingleCall(self, request, context):
        print("SingleCall Request Made: " + request.greeting + " " + request.name)
        hello_reply = gchat_pb2.ChatReply(message = "Hello from server")

        return hello_reply
    
    def StreamToClient(self, request, context):
        print("StreamToClient Request Made: " + request.greeting + " " + request.name)
        print(request)

        for i in range(3):
            hello_reply = gchat_pb2.ChatReply(message = "Hello from server")
            yield hello_reply
            time.sleep(1)
    
    def StreamToServer(self, request_iterator, context):
        delayed_reply = gchat_pb2.DelayedReply()
        for request in request_iterator:
            print("StreamToServer Request Made: " + request.greeting + " " + request.name)
            print(request)
            delayed_reply.request.append(request)
        
        delayed_reply.message = f"you sent {len(delayed_reply.request)} requests"
        return delayed_reply
    
    
    def MutualStream(self, request_iterator, context):
        for request in request_iterator:
            print("MutualStream Request Made: ")
            print(request)

            hello_reply = gchat_pb2.ChatReply()
            hello_reply.message = f"{request.greeting} {request.name}"
            yield hello_reply
            time.sleep(1)
    
# setup server
def serve():
    # have 10 maximum workers to handle threads
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # add the servicer to the server
    gchat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)

    server.add_insecure_port('localhost:50000')
    server.start()
    print("[SERVER] Server started on port 50000...")

    server.wait_for_termination()


if __name__ == '__main__':
    serve()