# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chat_pb2 as chat__pb2


class ChatServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ChatStream = channel.unary_stream(
                '/grpc.ChatServer/ChatStream',
                request_serializer=chat__pb2.Empty.SerializeToString,
                response_deserializer=chat__pb2.Note.FromString,
                )
        self.SendNote = channel.unary_unary(
                '/grpc.ChatServer/SendNote',
                request_serializer=chat__pb2.Note.SerializeToString,
                response_deserializer=chat__pb2.ServerResponse.FromString,
                )
        self.CreateAccount = channel.unary_unary(
                '/grpc.ChatServer/CreateAccount',
                request_serializer=chat__pb2.AccountInfo.SerializeToString,
                response_deserializer=chat__pb2.ServerResponse.FromString,
                )
        self.Login = channel.unary_unary(
                '/grpc.ChatServer/Login',
                request_serializer=chat__pb2.AccountInfo.SerializeToString,
                response_deserializer=chat__pb2.ServerResponse.FromString,
                )
        self.Logout = channel.unary_unary(
                '/grpc.ChatServer/Logout',
                request_serializer=chat__pb2.Empty.SerializeToString,
                response_deserializer=chat__pb2.ServerResponse.FromString,
                )
        self.ListAccounts = channel.unary_stream(
                '/grpc.ChatServer/ListAccounts',
                request_serializer=chat__pb2.AccountInfo.SerializeToString,
                response_deserializer=chat__pb2.ServerResponse.FromString,
                )
        self.DeleteAccount = channel.unary_stream(
                '/grpc.ChatServer/DeleteAccount',
                request_serializer=chat__pb2.AccountInfo.SerializeToString,
                response_deserializer=chat__pb2.ServerResponse.FromString,
                )


class ChatServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ChatStream(self, request, context):
        """This bi-directional stream makes it possible to send and receive Notes between 2 persons
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendNote(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateAccount(self, request, context):
        """account creation
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Login(self, request, context):
        """account login
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Logout(self, request, context):
        """get unread
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListAccounts(self, request, context):
        """list accounts
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAccount(self, request, context):
        """delete account
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ChatStream': grpc.unary_stream_rpc_method_handler(
                    servicer.ChatStream,
                    request_deserializer=chat__pb2.Empty.FromString,
                    response_serializer=chat__pb2.Note.SerializeToString,
            ),
            'SendNote': grpc.unary_unary_rpc_method_handler(
                    servicer.SendNote,
                    request_deserializer=chat__pb2.Note.FromString,
                    response_serializer=chat__pb2.ServerResponse.SerializeToString,
            ),
            'CreateAccount': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateAccount,
                    request_deserializer=chat__pb2.AccountInfo.FromString,
                    response_serializer=chat__pb2.ServerResponse.SerializeToString,
            ),
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=chat__pb2.AccountInfo.FromString,
                    response_serializer=chat__pb2.ServerResponse.SerializeToString,
            ),
            'Logout': grpc.unary_unary_rpc_method_handler(
                    servicer.Logout,
                    request_deserializer=chat__pb2.Empty.FromString,
                    response_serializer=chat__pb2.ServerResponse.SerializeToString,
            ),
            'ListAccounts': grpc.unary_stream_rpc_method_handler(
                    servicer.ListAccounts,
                    request_deserializer=chat__pb2.AccountInfo.FromString,
                    response_serializer=chat__pb2.ServerResponse.SerializeToString,
            ),
            'DeleteAccount': grpc.unary_stream_rpc_method_handler(
                    servicer.DeleteAccount,
                    request_deserializer=chat__pb2.AccountInfo.FromString,
                    response_serializer=chat__pb2.ServerResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grpc.ChatServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatServer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ChatStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/grpc.ChatServer/ChatStream',
            chat__pb2.Empty.SerializeToString,
            chat__pb2.Note.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendNote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/SendNote',
            chat__pb2.Note.SerializeToString,
            chat__pb2.ServerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateAccount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/CreateAccount',
            chat__pb2.AccountInfo.SerializeToString,
            chat__pb2.ServerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/Login',
            chat__pb2.AccountInfo.SerializeToString,
            chat__pb2.ServerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Logout(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/Logout',
            chat__pb2.Empty.SerializeToString,
            chat__pb2.ServerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListAccounts(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/grpc.ChatServer/ListAccounts',
            chat__pb2.AccountInfo.SerializeToString,
            chat__pb2.ServerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteAccount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/grpc.ChatServer/DeleteAccount',
            chat__pb2.AccountInfo.SerializeToString,
            chat__pb2.ServerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
