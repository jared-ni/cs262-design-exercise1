# Engineering Notebook

## Part 1 (Sockets)
2/05
- Today I watched extensive video tutorials about the use of sockets. The first major challenge of this project is getting started with socket programming, since neither my partner and I have much experience. I learned about using Sockets in Python, networking using TCP protocol, and client-server connection on the local area network (LAN). I realized that the first step of our design is to separate the server code from the client code. Server code establishes the server socket, and it continues to listen to new client connections in a while loop. the server socket object (called "server") will block until a new connection is discovered, in which case it handles the client in a new thread, as to not interfere with the discovery of other new connections. 
- On the new thread, the handle_client function must decode first the wired protocol header, then the message itself. It shall use a try block in case of fatal or recoverable failures. Eventually, each client will be disconnected and their connection removed from the current logged in. In the try block, messages can be decoded using the standard format, and the intended client shall receive the message. 


2/11
- Today I pondered on two different approach I can take to implement the client-to-client messaging functionality. If we were to do this in a singular command prompt, that means if I want a client to be both send and receive message, I must start a new thread for the new client and more threads within the new thread to receive messages from other clients. Or, I can start another client for every pair of clients that has the sole purpose of reading their mutual messages. Which approach is better? I don't yet know, but I will find out soon. 
- For encoding the header components of the wired protocol, how do I calculate by bytes in Python? Or, can I simply separate each of the protocol components with a special symbol?

2/11
- While drawing the initial design for the chat app and following closely with the specifications, we initially thought to have "chatroom" where a user can chat solely with another user they specified. However, we ran into a problem scenario: if another third user sends the first user a message while the first user is in the "chatroom" with the second user, the message should be sent right away. This will result in the teardown of the "chatroom" abstraction, which is supposed to be exclusive to the two users. If we wait until the first user exits the chatroom for the third user's message to send, this violates the 3rd requirement of "if the recipient is logged in, deliver immediately". Thus, we thought of a new design: have the client terminal be a place where any user can send our user a message. However, this will require the client having to specify the receiving user for all messages sent. Now, how does the user specify a user to send their message to? We specify to all users that if they want to send a message to a specific user, the first word should be the intended recipients name followed by a colon. For example, if foo wanted to send to bar "Hello World!", their inputted message should be "bar: Hello World!".


2/12 
- I realized a design flaw: we must separate client socket from the storing of user information. I decided to have another dictionary to map client_sockets to the respective accounts that they logged in. 
- I am improving the wired protocol and standardizing the server code for now. Soon, everything will be standardized. 
TODOS: 
    - wrap more try catch blocks in error-prone functions
    - finish abstracting server functions
    - finalize how users and client sockets are associated
    - Lock the two dictionaries while they are being edited
    - Should we make it so that a user cannot login on two different clients? Must think about it
    - Push messages not directly to socket but to the queue list if client is not logged in. 
    - should we have a buffer in front of each actual message, so we know for sure that we are parsing the actual message? 

- How should I abstract the code for registering and logging in? Should they be part of the while loop that handles incoming wired protocol messages? 
- My thoughts on client side structure: 
    - After connecting, asks user whether they want to register. Then, ask them to log in. Whenever they want to register or login another account, they may do so with commands. 
    - After register/login, user enters while loop, where it follows the structure for server side socket.

- We need a response message, in case the message failed to deliver. 

- Fixed a huge design flaw. For context, we have two different threads, one for listening and one for user input. The listening thread and the input threads are not supposed to interact, so it doesn't matter what the results of functions are. We simply send the message, and if they fail, we throw fail message on the listening thread. It's okay if they fail, because the client can simply call them again. It doesn't have to repeatedly ask the server for response when creating a new account, because we can simply call the register_user function on demand. Every loop, we check whether the user is logged in, and if they are not, we ask them to sign in, and if they refuse, we deny them any user-level commands like sending messages. 

2/13
- Handled edge cases. 
- First, if the client deletes its user its logged in as, it prompts the client to register another account.
- Second, if the client says "no" to registration, the client is prompted to log in to an account.
- Third, if the client says "no" to logging in, the client is prompted to register another account.
- Added a new option for users to immediately disconnect from the register and login prompts.

2/17: 
- Deliver unread messages on login by implementing a queue inside each user struct for unread messages
- Locked all dictionaries with mutex such that only one user can access and change the client and user dictionaries at a given moment.
- Add constraints to username (can't contain :, as that would inferere with the client protocol to send messages)
- Added better, more helpful error messages
- Do we want a trie in order to make text wildcard efficient when searching for user accounts?


2/19: 
- Error handling with wrong key inputs
- Handle client disconnection from forced control + z and control + c


2/19: 
- Still need to add multiple-people features. 
- Need to encrypt messages. 

- Delete doesn't actually log poeople out!!!!!

- log one client out when another client is logged in


2/21: 
- Need to: check error handling, handle version number checking, handle everything else