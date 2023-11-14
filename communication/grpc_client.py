import grpc
import pickle
from amalgam.communication.proto import message_pb2, message_pb2_grpc


class RPCStub(object):
    max_recv_message_length = 1024 * 1024 * 1024 * 2 - 100
    grpc_options = [
        ("grpc.max_receive_message_length", max_recv_message_length),
        # ("grpc.service_config", retry_config)
    ]

    def __init__(self, address, local_name, timeout=3600.0) -> None:
        self.timeout = timeout
        self.local_name = local_name
        channel = grpc.insecure_channel(address, options=self.grpc_options)
        self.stub = message_pb2_grpc.ServerServiceStub(channel)
    
    def _send(self, dst, type, key, data):
        resp = self.stub.PushData(RPCStub._transform_data(self.local_name, dst, type, key, data))
        return resp.status

    @staticmethod
    def _transform_data(src, dst, type, key, data) -> message_pb2.RequestBody:
        res = message_pb2.RequestBody(
            src=src,
            dst=dst,
            type=type.value,
            key=key,
            python_bytes=pickle.dumps(data)
        )
        return res


if __name__ == "__main__":
    val = {1:2, 3:6}
    print(list(val.keys()))

    client = RPCStub('127.0.0.1:4444')
    print(client._send('a', 'b', 1, 'None', 'hi bitch'))