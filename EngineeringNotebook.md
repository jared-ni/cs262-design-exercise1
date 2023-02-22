# Engineering Notebook

## Part 1 (Sockets)
2/05
- Today I watched extensive video tutorials about the use of sockets. The first major challenge of this project is getting started with socket programming, since neither my partner and I have much experience. I learned about using Sockets in Python, networking using TCP protocol, and client-server connection on the local area network (LAN). I realized that the first step of our design is to separate the server code from the client code. Server code establishes the server socket, and it continues to listen to new client connections in a while loop. The server socket object (called "server") will block until a new connection is discovered, in which case it handles the client in a new thread, as to not interfere with the discovery of other new connections. 

- On the new thread, the handle_client function must decode first the wired protocol header, then the message itself. It will use a try block in case of fatal or recoverable failures, a good practice especially for asynchronous remote communication. Eventually, each client is disconnected and their connection removed from the current list of logged in users. In the try block, messages are decoded using the standard format, and the intended client receives the message.


2/11
- Today I pondered on two different approach I can take to implement the client-to-client messaging functionality. If we were to do this in a singular command prompt, that means if I want a client to be both send and receive message, I must start a new thread for the new client and more threads within the new thread to receive messages from other clients. Or, I can start another client for every pair of clients that has the sole purpose of reading their mutual messages. I think the method of having multiple threads is much more efficient as it feels much more like a chat app for the users.

- For encoding the header components of the wired protocol, I calculate by bytes in Python, which then are passed back and forth. I avoided sending wired protocols as strings since then it would take a lot of time to parse for both server and client for each rpc.

2/11
- While drawing the initial design for the chat app and following closely with the specifications, we initially thought to have "chatroom" where a user can chat solely with another user they specified. However, we ran into a problem scenario: if another third user sends the first user a message while the first user is in the "chatroom" with the second user, the message should be sent right away. This will result in the teardown of the "chatroom" abstraction, which is supposed to be exclusive to the two users. If we wait until the first user exits the chatroom for the third user's message to send, this violates the 3rd requirement of "if the recipient is logged in, deliver immediately". 

- Thus, we thought of a new design: have the client terminal be a place where any user can send our user a message. However, this will require the client having to specify the receiving user for all messages sent. Now, how does the user specify a user to send their message to? We specify to all users that if they want to send a message to a specific user, the first word should be the intended recipients name followed by a colon. For example, if foo wanted to send to bar "Hello World!", their inputted message should be "bar: Hello World!". We agreed that this was a much better option that creating separate chatroom for each pair of users. It also fit better into the specification of having to list users, so the client can immediately choose a user to text and message them right away.


2/12 
- I realized a design flaw: we must separate client socket from the storing of user information. This is such that a client can potentially log in as multiple users (one at a time), and a user can access the chat app from multiple clients. I decided to have another dictionary to map client_sockets to the respective accounts that they logged in.

- I've improved the wired protocol and standardized the server code for now. Soon, everything will be standardized. 
TODOS: 
    - wrap more try catch blocks in error-prone functions
    - finish abstracting server functions
    - finalize how users and client sockets are associated
    - Lock the two dictionaries while they are being edited
    - Should we make it so that a user cannot login on two different clients? Must think about it
    - Push messages not directly to socket but to the queue list if client is not logged in. 
    - should we have a buffer in front of each actual message, so we know for sure that we are parsing the actual message? 

- How should I abstract the code for registering and logging in? Should they be part of the while loop that handles incoming wired protocol messages? 
- For the client side structur, after connecting, it asks user whether they want to register. Then, it asks them to log in. Whenever they want to register or login another account, they may do so with commands. This is the natural sequence for registering for any chat app. After register/login, user enters while loop, where it follows the structure for server side socket.

- We implemented a response message from server to client, in case the message failed to deliver. 

- We fixed a huge design flaw. For context, we have two different threads, one for listening and one for user input. The listening thread and the input threads are not supposed to interact, so it doesn't matter what the results of functions are. We simply send the message, and if they fail, we throw fail message on the listening thread. It's okay if they fail, because the client can simply call them again. It doesn't have to repeatedly ask the server for response when creating a new account, because we can simply call the register_user function on demand. Every loop, we check whether the user is logged in, and if they are not, we ask them to sign in, and if they refuse, we deny them any user-level commands like sending messages. From what we had before, our client was entering more and more infinite loops which was causing later functions to fail.

2/13
- Handled edge cases:
    - First, if the client deletes its user its logged in as, it prompts the client to register another account.
    - Second, if the client says "no" to registration, the client is prompted to log in to an account.
    - Third, if the client says "no" to logging in, the client is prompted to register another account.
    - Added a new option for users to immediately disconnect from the register and login prompts.

2/17: 
- Deliver unread messages on login by implementing a queue inside each user struct for unread messages that are sent when users log in.
- Locked all dictionaries with mutex such that only one user can access and change the client and user dictionaries at a given moment.
- Add constraints to username (can't contain :, as that would inferere with the client protocol to send messages)
- Added better, more helpful error messages for clients to understand
- Do we want a trie in order to make text wildcard efficient when searching for user accounts?

2/19: 
- Error handling with wrong key inputs
- Handle client disconnection from forced control + z and control + c

2/19: 
- Double encrypted passwords from client to server and from server to dictionary storing user info. 
- Fixed bug where delete doesn't actually log poeople out.
- Logged one client out when another client is logged in as a user

2/21: 
- Checked error handling and handle version number checking.

## Part 2 (gRPC)
2/21:
- For the gRPC portion of the assignment, most of the code and functionality from part 1 was carried over with grpc protocols instead of our own defined wire protocols. 

- In terms of the complexity of our code, the gRPC abstracted away major parts of the implementation, such as the use of threads, streaming, and asychronous call and response. Thus, the gRPC implementation was much simpler (especially for the programmer).

- For performance differernces, it'm important to note that for the socket implementation, call and responses from client to server was slow because any message sent from client to server (such as registering and logging in) had to have their reponse picked up by the client's listening thread. So the response was not immediate. Because gRPC handles birdirectional streaming, in instances where a server sends a response back to the client, these were much more faster compared to our socket/wire protocol implementation. For sending messages from a client to another client, we did not notice any big differences in performance.

- For the size of the buffers, based on our implementation, the size for grpc buffers are at least the size of the buffers from our own wire protocol.
