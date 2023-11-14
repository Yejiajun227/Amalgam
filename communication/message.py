from enum import Enum, unique


class AutoIndexer:
    def __init__(self):
        self._index = -1

    def auto(self):
        self._index += 1
        return self._index

val = AutoIndexer()


@unique
class MessageType(Enum):
    PING = val.auto()
    NULL = val.auto()
    ERROR = val.auto()
    TEST_DATA = val.auto()
    # data split
    DATA_SPLIT_IDX = val.auto()
    # paillier key
    PAILLIER_PUBLIC_KEY = val.auto()

    # dh psi
    DH_BASE = val.auto()
    FIRST_ENC_IDS = val.auto()
    SECOND_ENC_IDS = val.auto()

    # VFL LR
    PARTIAL_WX = val.auto()
    FORWARD_GRADIENT = val.auto()
    LOCAL_GRADIENT = val.auto()
    

