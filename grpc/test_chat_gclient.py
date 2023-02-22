import unittest
from unittest import mock
from unittest import TestCase
import grpc
import chat_pb2 as chat
import chat_pb2_grpc as rpc

class ChatServerTest(unittest.TestCase):
    @mock.patch('chat_gclient.input', create=True)
    def start(self):
        channel = grpc.insecure_channel('localhost:43210')
        self.stub = rpc.ChatServerStub(channel)
        self.username = ""

    # @mock.patch('chat_gclient.input', create=True)
    # def test_RegisterUser(self):



    @mock.patch('chat_gclient.input', create=True)
    def test_ChatStream(self, mocked_input):
        channel = grpc.insecure_channel('localhost:43210')
        self.stub = rpc.ChatServerStub(channel)
        self.username = ""
        mocked_input.side_effect = ["user1", "Test message 1"]
        n = chat.Note()
        n.version = 1
        n.operation_code = 0
        n.sender = "user1"
        n.receiver = "user1"
        n.message = "Test Message 1"
        response = self.stub.SendNote(n)
        print(response)
        # self.assertEqual(response.success, False)
        # self.assertEqual(response.message, "[SERVER] You are not logged in")


if __name__ == '__main__':
    unittest.main()