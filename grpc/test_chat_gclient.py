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
    def setUpClass(cls):
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
        success = self.client.send_message("user2", "Test message 2")
        self.assertEqual(success, False)

    # test send message
    # @mock.patch('chat_gclient.input', create=True)




if __name__ == '__main__':
    unittest.main()