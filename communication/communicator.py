import random
from threading import Thread, current_thread
from amalgam.communication.grpc_server import ServerManager
from amalgam.communication.grpc_client import RPCStub
from amalgam.communication.message import MessageType
import time


def get_exponential_backoff_interval(factor, retries, maximum=5, jitter="equal"):
    """Calculate the exponential backoff wait time.

    Args:
        factor (_type_): the backoff factor
        retries (_type_): retry times
        maximum (_type_): max backoff times
        jitter (str, optional): trying to improve the performance of a system by 
        adding randomness. Defaults to full.

    """
    # sleep = min(cap, base*2**attempt)
    # full jitter random_between(0, sleep)
    # equal jitter   random_between(0, sleep/2)+ sleep/2
    # decorrelated jitter  min(cap, random_between(base, sleep*3))

    countdown = min(maximum, factor * (2 ** retries))

    if jitter == "full":
        countdown = random.uniform(0, countdown)
    elif jitter == "equal":
        countdown = countdown/2 + random.uniform(0, countdown/2)
    elif jitter == "decorrelated":
        countdown = min(maximum, random.uniform(factor, countdown*3))
    
    return round(countdown, 6)


class GrpcCommunicator(object):
    def __init__(self, cluster, local, ) -> None:
        endpoints = []
        self.party = local
        self.rpc_stubs = {}
        for party_name, val in cluster.items():
            if party_name == local:
                # endpoints.append((party_name, "0.0.0.0:"+str(val['port'])))
                self._init_server("0.0.0.0:"+str(val['port']))
            else:
                endpoints.append((party_name, val['address']+":"+str(val['port'])))
        
        for name, address in endpoints:
            self.rpc_stubs[name] = RPCStub(address, self.party)
        
        self.other_party = list(self.rpc_stubs.keys())

    def _init_server(self, address):
        try:
            self.server = ServerManager(address)
            t = Thread(target=self.server.start)
            t.start()
        except Exception as e:
            raise RuntimeError("init server failed")
        
    def _stop_server(self):
        """refer to https://juejin.cn/s/python%20grpc%20server%20graceful%20shutdown
        """
        try:
            t = Thread(target=self.server.stop)
            t.start()
            # self.server.server.wait_for_termination()
        except Exception as e:
            raise RuntimeError("stop server failed")

    def send(self, dst:str, type:MessageType, data, key='None'):
        cur_stub = self.rpc_stubs[dst]
        resp = cur_stub._send(dst, type, key, data)
        # make sure that data has sent to dst
        retry_times = 0
        while resp != 'Success' and retry_times < 10:
            time.sleep(get_exponential_backoff_interval(0.5, retry_times))
            retry_times += 1
            resp = cur_stub._send(dst, type, key, data)
        if retry_times == 10:
            raise ConnectionError("Can not connect to server! Please check your internet.")
        
    def recv(self, src:str, type:MessageType, key='None', timeout=100.0):
        cur_type, data = self.server.get_message(src, self.party, key, timeout)
        if cur_type != type.value:
            raise ValueError(f"Message typy error, expected type {type}, but get type {cur_type}")
        return data

    def broadcast(self, dsts:list, type:MessageType, data, key='None'):
        threads = []
        def send_in_thread(dst, type, key, data):
            try:
                self.send(dst, type, data, key)
                # print(f"Success broadcast in thread, name is {current_thread().getName()}")
            except Exception as e:
                raise RuntimeError(f"failed send_in_thread, thread name is {current_thread().getName()}")
        
        for dst in dsts:
            t = Thread(target=send_in_thread, args=(dst, type, key, data), name=f"Broadcast-to-{dst}")
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def gather(self, srcs:list, type:MessageType, key='None', timeout=100.0):
        threads = []
        result = dict()
        def recv_in_thread(src, type, key, timeout):
            try:
                result[src] = self.recv(src, type, key, timeout)
                # print(f"Success gather in thread, name is {current_thread().getName()}")
            except Exception as e:
                raise RuntimeError(f"failed recv_in_thread,thread name is {current_thread().getName()}")
            
        for src in srcs:
            t = Thread(target=recv_in_thread, args=(src, type, key, timeout), name=f"gather-from-{src}")
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        return result


if __name__ == "__main__":

    server = ServerManager('0.0.0.0:4444')
    server.start()