# cs262-design-exercise1

## Running on Local
Clone the repository
```bash
git clone https://github.com/jared-ni/cs262-design-exercise1.git
```
Then, cd into the repository, and run either the socket or the gRPC server
```
python server.py
```
```
python grpc/chat_gserver.py
```
Then, run the corresponding client:
```
python client.py
```
```
python grpc/chat_gclient.py
```
Give the host server address as the command line argument (or leave blank to run on localhost).

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


## Setting up Server and Client(s) (Part 2: Python gRPC)
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
python chat_gclient.py <host>
```
where \<host\> is the address of the machine the server is currently running on.

If multiple clients want to connect, repeat the above step in another terminal.


## Navigating the Chat App
For both sockets and GRPC implementations, once the client connects to the server, 
the chat app prompts you to register for a user. If the client already is a 
registered user, then it can simply type "no". Then, chat app then prompts you 
to log in. Once logged in, the user receives any unseen messages sent to them while
they were logged out.

Now, the user has access to various functionalities by typing:

**\<username\>: \<message\>**: sends \<message\> to \<username\> if \<username\> exists; sends immediately if \<username\> is logged on, else queues the message on the server.

**./register**: registers another user

**./login**: logs in another user

__./list *__: lists all users registered in the server; * is the text wildcard

**./delete \<username\>**: deletes \<username\> from server (prompts for \<username\> password)

**./disconnect**: logs user out (if logged in) and disconnects client, ending session

**./help**: lists these above commands in case user forgets

If the user receives a message from another user, it will show up on the user's 
terminal in the format **([\<username\>] \<message\>)**.


## Running Unit Tests
For testing socket implementation (part 1), open up a terminal and nagivate to the 
directory containing server.py and client.py. Start the server by typing
```bash
python server.py
```

Now, open up another terminal and nagivate to the same directory and type
```bash
python -m unittest test_client.py
```
This will run all unit tests, testing individual functions of client.py and making
sure that messages are sent correctly from client to server to client.

For testing grpc implementation (part 2), open up a terminal and nagivate to the 
directory containing chat_gserver.py and chat_gclient.py. Start the server by typing
```bash
python chat_gserver.py
```

Now, open up another terminal and nagivate to the same directory and type
```bash
python -m unittest test_chat_gclient.py
```
This will run all unit tests, testing individual functions of chat_gclient.py and making
sure that messages are sent correctly from client to server to client.