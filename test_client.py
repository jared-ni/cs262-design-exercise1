from unittest import TestCase
from unittest import mock
import unittest
import client
import socket

class TestClient(TestCase):

    # @mock.patch('client.input', create=True)
    # def test_client(self, mocked_input):
    #     mocked_input.side_effect = ["yes", "yes", "user1", "1", "1", "yes", "user1", "1", "./list", "./disconnect"]
    #     result = client.start()
    #     print("test")

    @mock.patch('client.input', create=True)
    def test_register(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1", "1"]
        result = client.register_user(client_test)
        client_test.close()
        self.assertEqual(result, True)
        print("test")

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