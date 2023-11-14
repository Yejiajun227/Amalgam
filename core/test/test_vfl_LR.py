import sys
sys.path.append("/home/yejj")
from amalgam.core.ml.linear.vertical_logistic_regression import Vertical_LR_Arbiter, Vertical_LR_Guest, Vertical_LR_Host
from amalgam.communication.communicator import GrpcCommunicator
from multiprocessing import  Process


_parties = {
    'alice': {'address': '127.0.0.1', 'port':23041},
    'bob': {'address': '127.0.0.1', 'port':23042},
    'trent': {'address': '127.0.0.1', 'port':23043},
}


pipe_json = {
    "alice": {
            "role": 'host',
            "learning_rate": 0.01,
            "server": 'trent',
            "other_client": 'bob',
            "file_path": "/home/yejj/amalgam/core/data/example_data/breast_hetero_host.csv",
            "id": 'id',
    },
    "bob": {
            "role": 'guest',
            "learning_rate": 0.01,
            "server": 'trent',
            "other_client": 'alice',
            "file_path": "/home/yejj/amalgam/core/data/example_data/breast_hetero_guest.csv",
            "id": 'id',
            "label": 'y',
    },
    "trent": {
            "role": 'arbiter',
            "host": 'alice',
            "guest": 'bob',
    }
}


def func(local_name, cluster:dict):
    com = GrpcCommunicator(cluster, local_name)
    other_party = []
    for k in cluster.keys():
        if k != local_name:
            other_party.append(k)
    # init algorithm
    cur_pipe = pipe_json.get(local_name)

    if cur_pipe['role'] == 'host':
        handler = Vertical_LR_Host
    elif cur_pipe['role'] == 'guest':
        handler = Vertical_LR_Guest
    else:
        handler = Vertical_LR_Arbiter
    fun = handler(com, local_name, **cur_pipe)
    # 训练5轮
    fun.fit(5)


if __name__ == "__main__":
    party_name = ['alice', 'bob', 'trent']
    process_list = []
    for i in party_name:
        p = Process(target=func,args=(i, _parties))
        p.start() 
        process_list.append(p)

    for p in process_list:
        p.join()


