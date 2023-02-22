import unittest
from unittest import mock
from unittest import TestCase
import grpc
import chat_pb2 as chat
import chat_pb2_grpc as rpc
import chat_gclient

class ChatServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.channel = grpc.insecure_channel('localhost:43210')
        cls.conn = rpc.ChatServerStub(cls.channel)
        cls.client = chat_gclient.Client()

    # logout user
    @mock.patch('chat_gclient.input', create=True)
    def test_logout_user(self):
        self.client.logout_user()
        self.assertEqual(self.client.username, "")
        print("user: " + self.client.username)
    
    # delete user1 for testing purposes


    # # test sending message without logging in
    # @mock.patch('chat_gclient.input', create=True)
    # def test_send_message(self, mocked_input):
    #     mocked_input.side_effect = ["user1", "Test message 1"]
    #     n = chat.Note()
    #     n.version = 1
    #     n.operation_code = 0
    #     n.sender = "user1"
    #     n.receiver = "user1"
    #     n.message = "Test Message 1"
    #     response = self.conn.SendNote(n)
    #     self.assertEqual(response.success, False)
    #     self.assertEqual(response.message, "[SERVER] You are not logged in")


    # test register
    @mock.patch('chat_gclient.input', create=True)
    def test_register_user(self, mocked_input):
        mocked_input.side_effect = ["yes", "user1", "password1", "password1"]
        self.client.register_user()
        print("???")
        print(self.client.username)
        self.assertEqual(self.client.username, "")
    
    # test register
    @mock.patch('chat_gclient.input', create=True)
    def test_register_user2(self, mocked_input):
        mocked_input.side_effect = ["yes", "user1", "password1", "password1"]
        result = self.client.register_user()
        self.assertEqual(result, False)
    
    # test login
    @mock.patch('chat_gclient.input', create=True)
    def test_login_user(self, mocked_input):
        mocked_input.side_effect = ["yes", "user1", "password1"]
        result = self.client.login_user()
        # self.assertEqual(result, True)
        self.assertEqual(self.client.username, "user1")
    



if __name__ == '__main__':
    unittest.main()