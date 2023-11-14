import sys
sys.path.append("/home/yejj")
from amalgam.core.psi.dh.dh_2pc import DH_PSI_2PC
from amalgam.communication.communicator import GrpcCommunicator
from multiprocessing import  Process


_parties = {
    'alice': {'address': '127.0.0.1', 'port':23041},
    'bob': {'address': '127.0.0.1', 'port':23042},
}


pipe_json = {
    'alice' : {'is_starter':True, 'other_party': 'bob', "id_list": ["1","2","3","4","5","6","7"], 'role':'host'},
    'bob' : {'is_starter':False, 'other_party': 'alice', "id_list": ["5","6","7","8","9"], 'role':'guest'}, 
}


def func(local_name, cluster:dict):
    com = GrpcCommunicator(cluster, local_name)
    other_party = []
    for k in cluster.keys():
        if k != local_name:
            other_party.append(k)
    # init algorithm
    cur_pipe = pipe_json.get(local_name)
    dh = DH_PSI_2PC(com, local_name, False, **cur_pipe)
    res = dh.start()
    print(local_name, "get intersection ", res)


if __name__ == "__main__":
    party_name = ['alice', 'bob']
    process_list = []
    for i in party_name:
        p = Process(target=func,args=(i, _parties))
        p.start() 
        process_list.append(p)

    for p in process_list:
        p.join()


