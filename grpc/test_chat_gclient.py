from unittest import TestCase
from unittest import mock
import unittest
import chat_gclient
from chat_gclient import Client
import socket

class TestClient(TestCase):

    @mock.patch('chat_gclient.input', create=True)
    def test_register1(self, mocked_input):
        client_test = Client().__init__()

        mocked_input.side_effect = ["yes", "user1", "1", "1"]
        chat_gclient.register_user(client_test)
        result = chat_gclient.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, True)

    # @mock.patch('chat_gclient.input', create=True)
    # def test_register2(self, mocked_input):
    #     client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_test.connect((socket.gethostbyname(socket.gethostname()), 43210))

    #     mocked_input.side_effect = ["yes", "user2", "1", "2", "no"]
    #     result = chat_gclient.register_user(client_test)
    #     client_test.close()
    #     self.assertEqual(result, False)

    # @mock.patch('chat_gclient.input', create=True)
    # def test_login1(self, mocked_input):
    #     client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_test.connect((socket.gethostbyname(socket.gethostname()), 43210))

    #     mocked_input.side_effect = ["yes", "user1", "1"]
    #     chat_gclient.login_user(client_test)
    #     result = chat_gclient.listen_from_server(client_test, [True])
    #     client_test.close()
    #     self.assertEqual(result, True)

    # @mock.patch('chat_gclient.input', create=True)
    # def test_login2(self, mocked_input):
    #     client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_test.connect((socket.gethostbyname(socket.gethostname()), 43210))

    #     mocked_input.side_effect = ["yes", "user1", "1", "no"]
    #     chat_gclient.login_user(client_test)
    #     chat_gclient.login_user(client_test)
    #     result = chat_gclient.listen_from_server(client_test, [True])
    #     client_test.close()
    #     self.assertEqual(result, True)

    # @mock.patch('chat_gclient.input', create=True)
    # def test_delete1(self, mocked_input):
    #     client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_test.connect((socket.gethostbyname(socket.gethostname()), 43210))

    #     mocked_input.side_effect = ["yes", "user1", "1", "yes", "1"]
    #     chat_gclient.login_user(client_test)
    #     chat_gclient.delete_user(client_test)
    #     result = chat_gclient.listen_from_server(client_test, [True])
    #     client_test.close()
    #     self.assertEqual(result, True)

    # @mock.patch('chat_gclient.input', create=True)
    # def test_delete2(self, mocked_input):
    #     client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_test.connect((socket.gethostbyname(socket.gethostname()), 43210))

    #     mocked_input.side_effect = ["yes", "user1", "1", "yes", "2", "no"]
    #     chat_gclient.login_user(client_test)
    #     chat_gclient.delete_user(client_test)
    #     chat_gclient.delete_user(client_test)
    #     result = chat_gclient.listen_from_server(client_test, [True])
    #     client_test.close()
    #     self.assertEqual(result, True)

    # @mock.patch('chat_gclient.input', create=True)
    # def test_disconnect1(self, mocked_input):
    #     client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_test.connect((socket.gethostbyname(socket.gethostname()), 43210))

    #     mocked_input.side_effect = ["yes"]
    #     chat_gclient.disconnect_client(client_test)
    #     result = chat_gclient.listen_from_server(client_test, [True])
    #     client_test.close()
    #     self.assertEqual(result, False)

    # @mock.patch('chat_gclient.input', create=True)
    # def test_disconnect2(self, mocked_input):
    #     client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_test.connect((socket.gethostbyname(socket.gethostname()), 43210))

    #     mocked_input.side_effect = ["no"]
    #     result = chat_gclient.disconnect_client(client_test)
    #     client_test.close()
    #     self.assertEqual(result, False)

    # @mock.patch('chat_gclient.input', create=True)
    # def test_forced_disconnect1(self, mocked_input):
    #     client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_test.connect((socket.gethostbyname(socket.gethostname()), 43210))

    #     with self.assertRaises(SystemExit) as cm:
    #         chat_gclient.forced_disconnect(client_test)
    #     client_test.close()
    #     self.assertEqual(cm.exception.code, 0)

if __name__ == '__main__':
    unittest.main()

