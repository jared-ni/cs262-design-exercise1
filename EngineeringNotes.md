Jared Ni, Bryan Han

2/05
- Today I watched extensive video tutorials about the use of sockets. The first major challenge of this project is getting started with socket programming, since neither my partner and I have much experience. I learned about using Sockets in Python, networking using TCP protocol, and client-server connection on the local area network (LAN). I realized that the first step of our design is to separate the server code from the client code. Server code establishes the server socket, and it continues to listen to new client connections in a while loop. the server socket object (called "server") will block until a new connection is discovered, in which case it handles the client in a new thread, as to not interfere with the discovery of other new connections. 
- On the new thread, the handle_client function must decode first the wired protocol header, then the message itself. It shall use a Try block in case of fatal or recoverable failures. Eventually, each client will be disconnected and their connection removed from the current logged in. In the Try block, messages can be decoded using the standard format, and the intended client shall receive the message. 


2/11
- Today I pondered on two different approach I can take to implement the client-to-client messaging functionality. If we were to do this in a singular command prompt, that means if I want a client to be both send and receive message, I must start a new thread for the new client and more threads within the new thread to receive messages from other clients. Or, I can start another client for every pair of clients that has the sole purpose of reading their mutual messages. Which approach is better? I don't yet know, but I will find out soon. 


- For encoding the header components of the wired protocol, how do I calculate by bytes in Python? Or, can I simply separate each of the protocol components with a special symbol? 