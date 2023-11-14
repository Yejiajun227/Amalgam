
import sys
from multiprocessing import  Process
sys.path.append('/home/yejj')
from amalgam.communication.communicator import GrpcCommunicator as Com
from amalgam.communication.message import MessageType


_parties = {
    'alice': {'address': '127.0.0.1', 'port':23041},
    'bob': {'address': '127.0.0.1', 'port':23042},
    'carol': {'address': '127.0.0.1', 'port':23043},
}


def func(local_name, cluster):
    lc = Com(cluster, local_name)
    for k, v in cluster.items():
        if k != local_name:
            lc.send(k, MessageType.TEST_DATA, local_name+'->'+k)

    # check message queue
    print(local_name, lc.server.svc.msg_buffer)

    # test server.get_message
    print("-"*100)
    for k in cluster.keys():
        if k != local_name:
            print(lc.server.get_message(k, local_name, 'None', 10))
    print("-"*50, f"{local_name}", "-"*50)



if __name__ == "__main__":
    party_name = ['alice', 'bob', 'carol']
    process_list = []
    for i in party_name:
        p = Process(target=func,args=(i, _parties))
        p.start() 
        process_list.append(p)

    for p in process_list:
        p.join()
    