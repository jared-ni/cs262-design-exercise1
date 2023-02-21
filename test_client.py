from unittest import TestCase
from unittest import mock
import unittest
import client
import socket

# 1. version
VERSION = 1
# 2. operation_codes
REGISTER = 1
LOGIN = 2
LIST = 3
DELETE = 4
SEND = 5
RECEIVE = 6
SERVER_MESSAGE = 7
UNREAD = 8
DISCONNECT = 9
defined_operations = set([REGISTER, LOGIN, LIST, DELETE, SEND, RECEIVE, SERVER_MESSAGE, UNREAD, DISCONNECT])
p_sizes = {
    "ver": 1,
    "op": 1,
    "h_len": 1,
    "m_len": 2
}
CLIENT_KEY = b'cs262IsFunAndWaldoIsCool'

class TestClient(TestCase):

    # @mock.patch('client.input', create=True)
    # def test_client(self, mocked_input):
    #     mocked_input.side_effect = ["yes", "yes", "user1", "1", "1", "yes", "user1", "1", "./list", "./disconnect"]
    #     result = client.start()
    #     print("test")

    # there are two accounts for testing purposes: user1 has password 1, user2 has password 2

    @mock.patch('client.input', create=True)
    def test_register1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1", "1"]
        result = client.register_user(client_test)
        client_test.close()
        self.assertEqual(result, True)

    @mock.patch('client.input', create=True)
    def test_register2(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user2", "1", "2", "no"]
        result = client.register_user(client_test)
        client_test.close()
        self.assertEqual(result, False)

    @mock.patch('client.input', create=True)
    def test_login1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1"]
        result = client.login_user(client_test)
        client_test.close()
        self.assertEqual(result, True)

    @mock.patch('client.input', create=True)
    def test_login2(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1", "no"]
        result = client.login_user(client_test)
        result = client.login_user(client_test)
        client_test.close()
        self.assertEqual(result, False)

    # @mock.patch('client.input', create=True)
    # def test_login3(self, mocked_input):
    #     client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

    #     hashed = client.get_hashed_password("1")
    #     # mocked_input.side_effect = ["no"]
    #     result = client.send(client_test, hashed, LOGIN)
    #     client_test.close()
    #     self.assertEqual(result, True)

    @mock.patch('client.input', create=True)
    def test_delete1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1", "yes", "1"]
        client.login_user(client_test)
        client.delete_user(client_test)
        result = client.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, True)

    @mock.patch('client.input', create=True)
    def test_delete2(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1", "yes", "2", "no"]
        client.login_user(client_test)
        client.delete_user(client_test)
        client.delete_user(client_test)
        result = client.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, True)

    @mock.patch('client.input', create=True)
    def test_disconnect1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes"]
        client.disconnect_client(client_test)
        result = client.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, False)

    @mock.patch('client.input', create=True)
    def test_disconnect2(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["no"]
        result = client.disconnect_client(client_test)
        client_test.close()
        self.assertEqual(result, False)

    @mock.patch('client.input', create=True)
    def test_forced_disconnect1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        client.forced_disconnect(client_test)
        result = client.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, False)

if __name__ == '__main__':
    unittest.main()





# import subprocess
# import time
# import os

# exec(open('client.py').read()); print("yes")
# time.sleep(1)
# print("yes")


# import unittest
# import socket
# import client

# class testClient(unittest.TestCase):

#     def setUp(self):
#         client.start()
#         # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         # client_socket.connect((socket.gethostbyname(socket.gethostname()), 48789))
#         # client_socket.send('message1'.encode())
#         # print(client_socket)
#         # self.assertEqual(client_socket.recv(1024).decode(), 'message1')
#         # client_socket.close()
		
# if __name__ == '__main__':
#     unittest.main()