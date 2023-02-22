# cs262-design-exercise1

"gives a set of instructions on setting up the client and server so that the system can be run"

## Installation
```bash
pip install -r requirements.txt 
```

## Setting up Server and Client(s) (Part 1: Python Sockets)
Open a terminal, nagivate to the directory with server.py and client.py, and run the server by typing 
```bash
python server.py
```

Then, open another terminal in the same directory. If the server is running on the same machine, type
```bash
python client.py
```
Else, if the server is running on a different machine as the client, run
```bash
python client.py <host>
```
where <host> is the address of the machine the server is currently running on.

If multiple clients want to connect, repeat the above step in another terminal.

## Setting up Server and Client(s) (Part 2: Python GRPC)
Open a terminal, nagivate to the grpc directory with chat_gserver.py and chat_gclient.py, and run the server by typing 
```bash
python chat_gserver.py
```

Then, open another terminal in the same directory. If the server is running on the same machine, type
```bash
python chat_gclient.py
```
Else, if the server is running on a different machine as the client, run
```bash
python chat_gclient.py {host}
```
where {host} is the address of the machine the server is currently running on.

If multiple clients want to connect, repeat the above step in another terminal.

## Navigating the Chat App
For both sockets and GRPC implementations, once the client connects to the server, 
the chat app prompts you to register for a user. If the client already is a 
registered user, then it can simply type "no". Then, chat app then prompts you 
to log in. Once logged in, the user receives any unseen messages sent to them while
they were logged out.

Now, the user has access to various functionalities by typing:
**<username>: <message>**: sends <message> to <username> if <username> exists; sends immediately if <username> is logged on, else queues the message on the server.
**./register**: registers another user
**./login**: logs in another user
__./list *__: lists all users registered in the server; * is the text wildcard
**./delete <username>**: deletes <username> from server (prompts for <username> password)
**./disconnect**: logs user out (if logged in) and disconnects client, ending session
**./help**: lists these above commands in case user forgets

## Running Unit Tests
For 

python3 -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/gchat.proto



- login(): login reply types. If you call login, it returns to the correct client. 

- communicate between client: 
    Two threads

    one thread: get message from server

    one thread: send message. 

    to send, send to database. Whenever 