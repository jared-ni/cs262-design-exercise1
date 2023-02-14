2/11/2023

While drawing the initial design for the chat app and following closely with the specifications, we initially thought to have "chatroom" where a user can chat solely with another user they specified. However, we ran into a problem scenario: if another third user sends the first user a message while the first user is in the "chatroom" with the second user, the message should be sent right away. This will result in the teardown of the "chatroom", which is supposed to be exclusive to the two users. If we wait until the first user exits the chatroom for the third user's message to send, this violates the 3rd requirement of "if the recipient is logged in, deliver immediately". Thus, we thought of a new design: have the client terminal be a place where any user can send the client a message. However, this will require the client having to specify the receiving user for all messages sent.

Now, how does the user specify a user to send their message to? We specify to all users that if they want to send a message to a specific user, the first word should be the intended recipients name followed by a colon. For example, if foo wanted to send to bar "Hello World!", their inputted message should be "bar: Hello World!".

2/13/2023
Handled edge cases. 
First, if the client deletes its user its logged in as, it prompts the client to register another account.
Second, if the client says "no" to registration, the client is prompted to log in to an account.
Third, if the client says "no" to logging in, the client is prompted to register another account.
Added a new option for users to immediately disconnect from the register and login prompts.