import gchat_pb2_grpc
import gchat_pb2
import time
import grpc

def get_client_stream_requests():
    while True:
        name = input("Please enter a name (or nothing to stop chatting): ")

        if name == "":
            break

        hello_request = gchat_pb2.HelloRequest(greeting = "Hello", name = name)
        yield hello_request
        time.sleep(1)

def run():
    with grpc.insecure_channel('localhost:50000') as channel:
        # stub calls grpc calls
        stub = gchat_pb2_grpc.ChatStub(channel)
        # call the SingleCall method
        print("1. SingleCall")
        print("2. StreamToClient")
        print("3. StreamToServer")
        print("4. MutualStream")
        rpc_call = input("Which call to make? ")
        if rpc_call == "1":
            print("SingleCall")
            hello_request = gchat_pb2.ChatRequest(greeting = "Hello from client", name = "Client")
            hello_reply = stub.SingleCall(hello_request)
            print("Received: ") 
            print(hello_reply)
        elif rpc_call == "2":
            print("StreamToClient")
            hello_request = gchat_pb2.ChatRequest(greeting = "Hello from client", name = "Client")
            hello_replies = stub.StreamToClient(hello_request)

            for reply in hello_replies:
                print("Received: ") 
                print(reply)

        elif rpc_call == "3":
            print("StreamToServer")
            delayed_reply = stub.StreamToServer(get_client_stream_requests())

            print("Received: ")
            print(delayed_reply)

        elif rpc_call == "4":
            print("MutualStream")

if __name__ == '__main__':
    run()