from collections import deque
from concurrent import futures
import time
import grpc
import pickle
from amalgam.communication.proto import message_pb2, message_pb2_grpc
from amalgam.communication.message import MessageType


class ServerSercives(message_pb2_grpc.ServerServiceServicer):
    QUEUE_MAX_SIZE = 2000

    def __init__(self) -> None:
        self.msg_buffer = dict()

    def SayHi(self, request, context) -> message_pb2.Response:
        response = message_pb2.Response(status='Success')
        try:
            type = request.type
            data = pickle.loads(request.python_bytes)
            if type != 0 or data != "Hi! YeJJ":
                response.status = "Message error"
        except Exception as e:
            response.status = "Unknown error"
        return response
    
    def PushData(self, request, context)-> message_pb2.Response:
        response = message_pb2.Response(status='Success')
        try:
            type = request.type
            data = pickle.loads(request.python_bytes)
            # print(f"{request.dst} receive msg '{data}' from {request.src}")
            q = self._check_cache_header(request)
            q.append((type, data))
        except Exception as e:
            response.status = "Unknown error"
        return response
    
    def _check_cache_header(self, request) -> deque:
        src = request.src
        dst = request.dst
        key = request.key
        buffer_key = "{}:{}:{}".format(src, dst, key)
        if not buffer_key in self.msg_buffer:
            self._init_buffer(src, dst, key)
            return self.msg_buffer[buffer_key]
        # judge queue max length
        if len(self.msg_buffer[buffer_key]) == ServerSercives.QUEUE_MAX_SIZE:
            raise MemoryError('current message queue has exceeded the max_size, reject request')
        return self.msg_buffer[buffer_key]

    def _init_buffer(self, src, dst, key):
        self.msg_buffer["{}:{}:{}".format(src, dst, key)] = deque()


class ServerManager(object):
    max_recv_message_length = 1024 * 1024 * 1024 * 2 - 100
    grpc_options = [
        ("grpc.max_receive_message_length", max_recv_message_length),
        ("grpc.http2.max_ping_strikes", 0),
    ]
    try_interval = 0.5

    def __init__(self, address, max_workers=3) -> None:
        super(ServerManager, self).__init__()
        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=max_workers),
            options=ServerManager.grpc_options,
        )
        self.svc = ServerSercives()
        message_pb2_grpc.add_ServerServiceServicer_to_server(self.svc, self.server)
        # self.msg_buffer = dict()
        self.server.add_insecure_port(address)

    def get_message(self, src, dst, key, timeout=100.0) -> None:
        start_time = time.time()
        flag_type = MessageType.NULL
        data = None
        buffer_key = "{}:{}:{}".format(src, dst, key)
        # TODO 从队头中将type匹配的所有数据取出  
        while True:
            # 
            if time.time() - start_time > timeout:
                break
            try:
                if buffer_key in self.svc.msg_buffer:
                    flag_type, data = self.svc.msg_buffer[buffer_key].popleft()
                    break
            except Exception as e:
                # print(e)
                pass
            time.sleep(self.try_interval)
        return flag_type, data

    def start(self) -> None:
        self.server.start()
        self.server.wait_for_termination()
    
    def stop(self) -> None:
        self.server.stop(5)


if __name__ == "__main__":

    server = ServerManager('0.0.0.0:4444')
    server.start()