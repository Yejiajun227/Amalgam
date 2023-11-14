from typing import List
import random
import numpy as np
import sys
sys.path.append("/home/yejj")
from amalgam.core.ml.base_model import Base_Model
from amalgam.communication.message import MessageType
from amalgam.communication.communicator import GrpcCommunicator
from amalgam.util.logger import getLogger, trace
from amalgam.core.data.dataframe import Dataloader
from amalgam.core.ml.activation_func import sigmoid
from amalgam.core.ml.metrics import metrics_classification
from phe import paillier
from functools import reduce


class Vertical_LR_Host(Base_Model):
    def __init__(self, com: GrpcCommunicator, local_party, **kwargs) -> None:
        super().__init__(com, **kwargs)
        self.dscr = "Vertical_LR"
        self.log = getLogger(local_party, self.dscr)
        self.party_name = local_party

    def _sync_paillier_key(self):
        self.public_key = self.com.recv(self.server, MessageType.PAILLIER_PUBLIC_KEY, timeout=20)

    @trace
    def _load_data(self, file_path):
        data_loader = Dataloader(self.log, self.role)
        self.id_list, raw_data = data_loader.read_csv(file_path, self.param.get('id'))
        self.columns = raw_data.columns
        self._train_test_split(raw_data)
        # TODO sample alignment and filter

        # self.log.info(f"self.x_test {self.x_test}")
    
    @trace
    def _init_weight(self):
        self.weight = np.random.randn(len(self.columns))
        self.log.info(f"After weight initialization, weight is {self.weight}")

    @trace
    def _compute_wx(self, X: np.array, W):
        host_wx = 0.25 * np.dot(X, W)
        enc_wx = list(map(lambda x: self.public_key.encrypt(x), host_wx))
        self.com.send(self.other_client, MessageType.PARTIAL_WX, enc_wx)
    
    @trace
    def _compute_gradient_loss(self, batch_x):
        d = self.com.recv(self.other_client, MessageType.FORWARD_GRADIENT, timeout=1000)
        # weight_grad = list(map(lambda x, y: x * y, d, self.x_train))
        # self.log.info(f"recv guest d, {d}, type is {type(d)}")
        weight_grad = list(map(lambda x, y: [x * x_i for x_i in y], d, batch_x)) 

        def grad_sum(r1, r2):
            for i in range(len(r1)):
                r2[i] += r1[i]
            return r2
        weight_grad = np.array(reduce(grad_sum, weight_grad))

        self.com.send(self.server, MessageType.LOCAL_GRADIENT, weight_grad)
        decrypt_grad = self.com.recv(self.server, MessageType.LOCAL_GRADIENT)
        # self.log.info(f"decrypt grad  {self.decrypt_grad}")
        train_size = batch_x.shape[0]
        decrypt_grad = [g / train_size for g in decrypt_grad]
        self.log.info(f"after average grad {decrypt_grad}")
        return decrypt_grad

    def _update_model(self, decrypt_grad):
        self.weight -= self.learning_rate * np.array(decrypt_grad)
    
    @trace
    def predict(self, x_test, weight):
        self.log.info(f"type of x_test is {type(x_test)}")
        host_wx = np.dot(x_test, weight)
        self.com.send(self.other_client, MessageType.PARTIAL_WX, host_wx)

    def fit(self, epochs=10):        
        self._sync_paillier_key()
        self._load_data(self.param.get("file_path"))
        self._init_weight()
        for epoch in range(epochs):
            self.log.info(f"start train epoch [{epoch+1}/{epochs}]")
            for batch_x in self._generate_batch_data():
                self.log.info(f"host batch_x is {batch_x}")
                self._compute_wx(batch_x, self.weight)
                grad = self._compute_gradient_loss(batch_x)
                self._update_model(grad)
        self.log.info("host finish train model.")
        self.predict(np.array(self.x_test), self.weight)
        self.com._stop_server()
        self.log.info("stop grpc server")


class Vertical_LR_Guest(Base_Model):
    def __init__(self, com: GrpcCommunicator, local_party, **kwargs) -> None:
        super().__init__(com, **kwargs)
        self.dscr = "Vertical_LR"
        self.party_name = local_party
        self.log = getLogger(local_party, self.dscr)

    def _sync_paillier_key(self):
        self.public_key = self.com.recv(self.server, MessageType.PAILLIER_PUBLIC_KEY, timeout=20)

    def _load_data(self, file_path, train_size=0.75):
        data_loader = Dataloader(self.log, self.role)
        self.id_list, raw_data, y = data_loader.read_csv(file_path, self.param.get("id"), self.param.get('label'))
        self.columns = raw_data.columns
        self._train_test_split(raw_data, y, train_size)

        # set negative label to -1
        self.y_train = self.y_train.map(lambda x: 1 if x ==1 else -1)  
        self.log.info("finish load data!")

    @trace
    def _init_weight(self):
        self.weight = np.random.randn(len(self.columns))
        self.bias = 0
        self.log.info(f"After weight initialization, weight is {self.weight}")

    @trace
    def _gather_wx(self, X: np.array, W):
        local_wx = 0.25 * (np.dot(X, W) + self.bias)
        # local_enc_wx = list(map(lambda x: self.public_key.encrypt(x), local_wx))
        host_wx = self.com.recv(self.other_client, MessageType.PARTIAL_WX, timeout=1000)
        global_wx = list(map(lambda x, y: x+y, local_wx, host_wx))
        # self.log.info(f"self.global_wx is \n {self.global_wx}\n global_wx type is {type(self.global_wx)}")
        return global_wx

    @trace
    def _compute_gradient_loss(self, wx: np.array, y: np.array, batch_x):
        """
        loss = log2 - 1/2*y*W^T*X + 1/8*(W^T*X)^2
        gradient = (1/4*W^T*X - 1/2 * y)*X
        """
        # self.loss = np.log(2) - 0.5 * 1
        
        d = wx - 0.5 * y
        # self.log.info(f"self.d is \n {d}\n type is {type(d)}")
        self.com.send(self.other_client, MessageType.FORWARD_GRADIENT, d)

        weight_grad = list(map(lambda x, y: [x * x_i for x_i in y], d, batch_x)) 
        # self.log.info(f"grad : {weight_grad} \n type of grad is {type(weight_grad)}")

        def grad_sum(r1, r2):
            for i in range(len(r1)):
                r2[i] += r1[i]
            return r2

        weight_grad = np.array(reduce(grad_sum, weight_grad))
        # self.log.info(f"after reduce grad is: {weight_grad} \n type of grad is {type(weight_grad)}")
        bias_grad = d.sum()

        total_grad = np.append(weight_grad, bias_grad)
        self.com.send(self.server, MessageType.LOCAL_GRADIENT, total_grad)
        decrypt_grad = self.com.recv(self.server, MessageType.LOCAL_GRADIENT, timeout=50)

        train_size = batch_x.shape[0]
        decrypt_grad = [g / train_size for g in decrypt_grad]
        # self.log.info(f"after average grad {self.decrypt_grad}")
        return decrypt_grad

    def _update_model(self, decrypt_grad: List):
        weight_grad = decrypt_grad[:-1]
        bias_grad = decrypt_grad[-1]
        self.log.info(f"weight grad is {weight_grad}, bias grad is {bias_grad}")
        self.weight -= self.learning_rate * np.array(weight_grad)
        self.bias -= bias_grad * self.learning_rate
    
    @trace
    def predict(self, x_test, weight):
        local_wx = np.dot(x_test, weight) + self.bias
        host_wx = self.com.recv(self.other_client, MessageType.PARTIAL_WX)
        # wx = list(map(lambda x, y: x+y, local_wx, host_wx))
        wx = np.vectorize(lambda x, y: x + y)(local_wx, host_wx)
        # pred_prob = list(map(lambda x: sigmoid(x), wx))
        pred_prob = np.vectorize(lambda x: sigmoid(x))(wx)
        return pred_prob
        # def prob_to_output(prob):
        #     if prob >= 0.5:
        #         return 1
        #     return 0
        # pred_label = np.vectorize(prob_to_output)(pred_prob)
    
    def _evaluate(self, y, y_score):
        model_report = metrics_classification(y, y_score)
        return model_report

    def fit(self, epochs=10):
        # import math
        self._sync_paillier_key()
        self._load_data(self.param.get("file_path"))
        self._init_weight()
        for epoch in range(epochs):
            self.log.info(f"start train epoch [{epoch+1}/{epochs}]")
            # generate mini batch data
            for batch_x, batch_y in self._generate_batch_data():
                # self.log.info(f"guest batch_y is {batch_y}")
                global_wx = self._gather_wx(batch_x, self.weight)
                grad = self._compute_gradient_loss(global_wx, batch_y, batch_x)
                self._update_model(grad)
        self.log.info(f"weights are {self.weight}")
        y_score = self.predict(np.array(self.x_test), self.weight)
        # 增加评估
        report = self._evaluate(self.y_test, y_score)
        self.log.info(report)
        self.com._stop_server()
        self.log.info("stop grpc server")



class Vertical_LR_Arbiter(Base_Model):
    def __init__(self, com: GrpcCommunicator, local_party, **kwargs) -> None:
        super().__init__(com, **kwargs)
        self.dscr = "Vertical_LR"
        self.log = getLogger(local_party, self.dscr)
        self.party_name = local_party
        self.host = kwargs.get('host')
        self.guest = kwargs.get('guest')
        self.clients = [self.host, self.guest]

    @trace
    def _sync_paillier_key(self, key_length=1024):
        self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=key_length)
        self.com.broadcast(self.clients, MessageType.PAILLIER_PUBLIC_KEY, self.public_key)
        self.log.info("finish broadcast paillier pk to host and guest")

    @trace
    def _decrypt_gradient(self):
        # 开两个线程监听
        host_grad = self.com.recv(self.host, MessageType.LOCAL_GRADIENT)
        # self.log.info(f'recv host enc gradient, {host_grad}')
        dec_host_grad = [self.private_key.decrypt(_) for _ in host_grad]
        # self.log.info(f"host dec grad is {dec_host_grad}")
        self.com.send(self.host, MessageType.LOCAL_GRADIENT, dec_host_grad)

        guest_grad = self.com.recv(self.guest, MessageType.LOCAL_GRADIENT)
        # self.log.info('recv guest enc gradient')
        dec_guest_grad = [self.private_key.decrypt(_) for _ in guest_grad]
        self.com.send(self.guest, MessageType.LOCAL_GRADIENT, dec_guest_grad)

    def predict(self):
        pass

    def fit(self, epochs=10):
        self._sync_paillier_key()
        for epoch in range(epochs):
            self.log.info(f"start train epoch [{epoch+1}/{epochs}]")
            for batch_idx in self._generate_batch_data():
                self._decrypt_gradient()
        self.log.info("finish train model.")
        self.com._stop_server()
        self.log.info("stop grpc server")


if __name__ == "__main__":
    import pandas
    import time
    import pickle
    public_key, private_key = paillier.generate_paillier_keypair(n_length=1024)
    w1 = np.random.randn(2)
    raw_data = pandas.DataFrame({'x1':[1,2,3], 'x2':[2.12, 5.22, -1.43]})
    columns = raw_data.columns
    print(raw_data)
    host_x = np.array(raw_data)
    host_wx = np.dot(host_x, w1)
    print(host_wx)
    # 测试 np.vectorize 和 map哪个更快
    # np.verctorize cost 0.0104   map cost 0.0074
    t1 = np.array([1.42,2.123,-3.14])
    t2 = np.array([1.1, 2])
    print("*"*100)
    print(0.25*np.dot(np.array(raw_data), t2))
    start = time.time()
    enc_host_wx = list(map(lambda x: public_key.encrypt(x), t1))
    print("map cost time:", time.time()-start)
    enc_t2 = list(map(lambda x: public_key.encrypt(x), t2))

    total = list(map(lambda x,y: x+y, enc_host_wx, enc_t2))
    total = [private_key.decrypt(_) for _ in total]
    print(total)
    # print(pickle.dumps(enc_host_wx))