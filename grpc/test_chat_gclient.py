import unittest
from unittest import mock
from unittest import TestCase
import grpc
import chat_pb2 as chat
import chat_pb2_grpc as rpc
import chat_gclient
import time

class ChatServerTest(unittest.TestCase):
    @classmethod
    @mock.patch('chat_gclient.input', create=True)
    def setUpClass(cls, mock_input):
        mock_input.side_effect = ["yes"]
        cls.channel = grpc.insecure_channel('localhost:43210')
        cls.conn = rpc.ChatServerStub(cls.channel)
        cls.client = chat_gclient.Client()

    # logout user
    @mock.patch('chat_gclient.input', create=True)
    def test_logout(self, mocked_input):
        self.client.logout()
        self.assertEqual(self.client.username, "")
    
    # delete user1 for testing purposes
    @mock.patch('chat_gclient.input', create=True)
    def test_delete_account(self, mocked_input):
        mocked_input.side_effect = ["password1"]
        self.client.delete_account("user1")

    # test sending message without logging in
    @mock.patch('chat_gclient.input', create=True)
    def test_send_message(self, mocked_input):
        mocked_input.side_effect = ["user1", "Test message 1"]

        self.client.logout()
        success = self.client.send_message("user1", "Test message 1")
        self.assertEqual(success, False)

    # test register and login and send message
    @mock.patch('chat_gclient.input', create=True)
    def test_register_user(self, mocked_input):
        mocked_input.side_effect = ["password1",
                                    "yes", "user1", "password1", "password1", 
                                    "yes", "user1", "password1", "password1",
                                    "yes", "user1", "password1", 
                                    "yes", "user1", "password1", 
                                    "yes", "user1", "wrongpassword"]
        # first delete account
        self.client.delete_account("user1")
        # then register
        result = self.client.register_user()
        self.assertEqual(result, True)
        # then register again using the same username
        result = self.client.register_user()
        print("result: " + str(result))
        self.assertEqual(result, False)

        # then login
        result = self.client.login_user()
        self.assertEqual(result, True)

        # then login again using the same username
        result = self.client.login_user()
        self.assertEqual(result, True)

        # then login with wrong password
        result = self.client.login_user()
        self.assertEqual(result, False)

        # test send message
        success = self.client.send_message("user1", "Test message 1")
        self.assertEqual(success, True)

        # test send message to non-existent user
        success = self.client.send_message("monkey", "Test message 2")
        self.assertEqual(success, False)

    # test send message
    @mock.patch('chat_gclient.input', create=True)
    def test_send_message(self, mocked_input):
        mocked_input.side_effect = ["user1", "Test message 1",
                                    "p2", 
                                    "yes",
                                    "user2", "password2", "password2",
                                    "random",
                                    "password2"]
        success = self.client.send_message("user1", "Test message 1")
        self.assertEqual(success, True)

        # delete user2
        success = self.client.delete_account("user2")

        # create user2
        self.client.register_user()

        # test send message to user2
        success = self.client.send_message("user2", "Test message 2")
        self.assertEqual(success, True)

        # test send to user2
        success = self.client.send_message("user2", "Test message 3")
        self.assertEqual(success, True)

        # test send to user2
        success = self.client.send_message("user2", "Test message 4")
        
        # delete user2
        success = self.client.delete_account("user2")

        success = self.client.delete_account("user2")
        self.assertEqual(success, True)

    
    # test logout 
    @mock.patch('chat_gclient.input', create=True)
    def test_logout(self, mocked_input):
        mocked_input.side_effect = ["yes", "user4", "password4", "password4", 
                                    "yes", "user4", "password4", 
                                    ]
        self.client.register_user()
        self.client.login_user()

        # test sending messsage to self
        success = self.client.send_message("user4", "Test message 1")
        self.assertEqual(success, True)

        # test self.username
        self.assertEqual(self.client.username, "user4")

        self.client.logout()
        self.assertEqual(self.client.username, "")

    # test list accounts
    @mock.patch('chat_gclient.input', create=True)
    def test_list_accounts(self, mocked_input):
        result = self.client.list_accounts("")
        self.assertEqual(result, None)

    # # test main input thread
    # @mock.patch('chat_gclient.input', create=True)
    # def test_communicate_with_server(self, mocked_input):




if __name__ == '__main__':
    unittest.main()