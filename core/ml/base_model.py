import pandas as pd
import numpy as np
from amalgam.communication.communicator import GrpcCommunicator
from amalgam.communication.message import MessageType
from sklearn.model_selection import train_test_split
import random
import math


class Base_Model(object):
    def __init__(self, com: GrpcCommunicator, **kwargs) -> None:
        self.com = com
        self.param = kwargs
        self.server = kwargs.get("server")
        self.role = kwargs.get("role")
        self.other_client = kwargs.get("other_client")
        self.learning_rate = kwargs.get("learning_rate")
        self.batch_size = kwargs.get("batch_size")
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None

    def _train_test_split(self, X: pd.DataFrame, y: pd.Series=None, split_ratio=0.75):
        if self.role == "host":
            train_idx, test_idx = self.com.recv(self.other_client, MessageType.DATA_SPLIT_IDX, timeout=100)
            # self.log.info(f"original host X is {X}")
            # self.log.info(f"host test_idx {test_idx}")
            self.x_train = X.iloc[train_idx]
            self.x_test = X.iloc[test_idx]
            # self.log.info(f"host x_test is {self.x_test}")
        elif self.role == "guest":
            seed = random.randint(1, 100)
            self.log.info(f"data train_test split, seed value is {seed}")
            x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=split_ratio, stratify=y, random_state=seed)
            train_idx = np.array(y_train.index)
            test_idx = np.array(y_test.index)
            # self.log.info(f"guest test_idx : {test_idx}")
            # self.log.info(f"type of x_train is {type(x_train)}, type of y_train is {type(y_train)}")
            self.com.send(self.other_client, MessageType.DATA_SPLIT_IDX, (train_idx, test_idx))

            self.x_train = x_train
            self.x_test = x_test
            self.y_train = y_train
            self.y_test = y_test
            # self.log.info(f"guest x_test is {self.x_test}")
        else:
            pass
        
    def _generate_batch_data(self):
        if self.role in ['host', 'guest']:
            if self.batch_size == -1:
                rounds = 1
                self.batch_size = self.x_train.shape[0]
            else:
                rounds = math.ceil(self.x_train.shape[0] / self.batch_size)
        if self.role == "host":
            for k in range(rounds):
                self.log.info(f"start train batch [{k+1}/{rounds}]")
                batch_idx = self.com.recv(self.other_client, MessageType.BATCH_SPLIT_IDX, timeout=100)
                # self.log.info(f"in generator host batch_x is {self.x_train.loc[batch_idx]}")
                yield np.array(self.x_train.loc[batch_idx])
                # self.batch_X = np.array(self.x_train.iloc[batch_idx])
        elif self.role == "guest":
            self.com.send(self.server, MessageType.BATCH_SPLIT_IDX, rounds)
            shuffled_index = np.random.permutation(self.y_train.index)
            for k in range(rounds):
                self.log.info(f"start train batch [{k+1}/{rounds}]")
                batch_idx = shuffled_index[k * self.batch_size:(k+1) * self.batch_size]
                self.com.send(self.other_client, MessageType.BATCH_SPLIT_IDX, batch_idx)
                # self.log.info(f"in generator guest batch_x is {self.x_train.loc[batch_idx]}")
                # self.log.info(f"in generator guest batch_y is {self.y_train.loc[batch_idx]}")
                yield np.array(self.x_train.loc[batch_idx]), np.array(self.y_train.loc[batch_idx])
            # self.batch_X = np.array(self.x_train.iloc[batch_idx])
            # self.batch_y = np.array(self.y_train.iloc[batch_idx])
        else:
            rounds = self.com.recv(self.guest, MessageType.BATCH_SPLIT_IDX)
            self.log.info(f"arbiter receive rounds {rounds}")
            for k in range(rounds):
                self.log.info(f"start train batch [{k+1}/{rounds}]")
                yield k

