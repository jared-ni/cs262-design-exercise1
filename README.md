# cs262-design-exercise1

Team: Jared Ni, Bryan Han

This is a distributed chat application that runs on Python Sockets. 


python3 -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/gchat.proto



- login(): login reply types. If you call login, it returns to the correct client. 

- communicate between client: 
    Two threads

    one thread: get message from server

    one thread: send message. 

    to send, send to database. Whenever 