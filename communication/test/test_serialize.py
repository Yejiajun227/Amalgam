import pickle
import sys
# print(sys.path)
sys.path.append("/home/yejj/")
from amalgam.communication.proto import message_pb2
 
def serialize(src, dst, type=1, key='None', python_bytes=pickle.dumps('SS')) -> bytes:
    data = message_pb2.RequestBody(
                src=src,
                dst=dst,
                type=type,
                key=key,
                python_bytes=python_bytes,
            )
    return data.SerializeToString()


def unserialize(comm_data:bytes) -> message_pb2.RequestBody:
    unserialize_res = message_pb2.RequestBody()
    unserialize_res.ParseFromString(comm_data)
    return unserialize_res


if __name__ == "__main__":
    name = 'this is a test message'
    serialize_data = serialize('alice','bob',1,'None', pickle.dumps(name))
    print(serialize_data)
    print('serialize_data memory use :', sys.getsizeof(serialize_data))
    
    unserialize_data = unserialize(serialize_data)
    print(unserialize_data)
    print('unserialize_data memory use :',sys.getsizeof(unserialize_data))
