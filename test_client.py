from unittest import TestCase
from unittest import mock
import unittest
import client
import socket

# operation_code
SEND = 5

class TestClient(TestCase):

    # tests register_user registers user
    @mock.patch('client.input', create=True)
    def test_register1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1", "1"]
        client.register_user(client_test)
        result = client.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, True)

    # tests register_user correctly behaves for "no"
    @mock.patch('client.input', create=True)
    def test_register2(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user2", "1", "2", "no"]
        result = client.register_user(client_test)
        client_test.close()
        self.assertEqual(result, False)

    # tests login_user logs in already registered user
    @mock.patch('client.input', create=True)
    def test_login1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1"]
        client.login_user(client_test)
        result = client.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, True)

    # tests login_user for works for "no"
    @mock.patch('client.input', create=True)
    def test_login2(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1", "no"]
        client.login_user(client_test)
        client.login_user(client_test)
        result = client.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, True)

    # tests deletet_user correcetly deletes user from list of users
    @mock.patch('client.input', create=True)
    def test_delete1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1", "yes", "1"]
        client.login_user(client_test)
        client.delete_user(client_test, "user1")
        result = client.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, True)

    # tests delete_user does not delete user given wrong password
    @mock.patch('client.input', create=True)
    def test_delete2(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        mocked_input.side_effect = ["yes", "user1", "1", "yes", "2", "no"]
        client.login_user(client_test)
        client.delete_user(client_test, "user1")
        client.delete_user(client_test, "user1")
        result = client.listen_from_server(client_test, [True])
        client_test.close()
        self.assertEqual(result, True)

    # tests disconnect_client corectly raises the SystemExit error
    @mock.patch('client.input', create=True)
    def test_disconnect1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        with self.assertRaises(SystemExit) as cm:
            client.disconnect_client(client_test)
        client_test.close()
        self.assertEqual(cm.exception.code, 0)

    # tests forced_disconnect corectly raises the SystemExit error
    @mock.patch('client.input', create=True)
    def test_forced_disconnect1(self, mocked_input):
        client_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test.connect((socket.gethostbyname(socket.gethostname()), 48789))

        with self.assertRaises(SystemExit) as cm:
            client.forced_disconnect(client_test)
        client_test.close()
        self.assertEqual(cm.exception.code, 0)

    # tests that message is properly received from one client to another
    @mock.patch('client.input', create=True)
    def test_send(self, mocked_input):
        client_test1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test1.connect((socket.gethostbyname(socket.gethostname()), 48789))

        client_test2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_test2.connect((socket.gethostbyname(socket.gethostname()), 48789))
        
        mocked_input.side_effect = ["yes", "user1", "1", "yes", "user2", "2", "2", "yes", "user2", "2"]
        client.login_user(client_test1)
        client.register_user(client_test2)
        client.login_user(client_test2)
        
        client.send(client_test1, "user2: test", SEND)
        result = client.listen_from_server(client_test2, [True])
        client_test1.close()
        client_test2.close()
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()

