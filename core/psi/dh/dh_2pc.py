from typing import List
import random
import hashlib
from amalgam.secure_protocol.pohlig_hellman import PohligHellman
from amalgam.communication.message import MessageType
from amalgam.util.logger import getLogger


class DH_PSI_2PC(object):
    def __init__(self, com, local_party, return_index=True, **kwargs) -> None:
        self.dscr = 'dh_psi_2pc'
        self.log = getLogger(local_party, self.dscr)
        self.com = com
        self.original_ids = kwargs.get('id_list')
        self.role = kwargs.get('role')
        self.return_index = return_index
        self.other_party = kwargs.get('other_party')
        self.is_job_starter = kwargs.get('is_starter')

    def __check_params(self):
        if self.role not in ['host', 'guest']:
            raise ValueError("Unsupported role")
        if len(self.original_ids) == 0:
            raise RuntimeError("current id_list is empty, please check your input")

    def __generate_prime_num(self, key_length):
        # refer to https://github.com/pyunits/pyunit-prime
        import pyunit_prime as py_prime
        return py_prime.get_large_prime_bit_size(key_length)
    
    def __generate_cipher(self, key_length):
        return PohligHellman.generate_key(key_length)
    
    def _sync_prime_primitive_root(self, key_length):
        if self.role == 'guest':
            self.cipher = self.__generate_cipher(key_length)
            self.p = self.cipher.mod_base
            # print('prime num', self.p)
            # self.g = generate_primitive_root(self.p)
            # print("primitive root", self.g)
            self.com.send(self.other_party, MessageType.DH_BASE, self.cipher)
        else:
            self.cipher = self.com.recv(self.other_party, MessageType.DH_BASE, 'None', 100.0)
            self.p = self.cipher.mod_base

    def __generate_private_key(self):
        self.private_key = self.cipher.init_private_key()

    def __hash_id(self):
        self.hashed_ids = [int(hashlib.md5(_.encode('utf-8')).hexdigest(), 16) for _ in self.original_ids]

    def _first_encrypt(self):
        self.__hash_id()
        self.__generate_private_key()
        self.encrypted_hashed_ids = [pow(_, self.private_key, self.p) for _ in self.hashed_ids]
        self.com.send(self.other_party, MessageType.FIRST_ENC_IDS, self.encrypted_hashed_ids)
        self.other_first_enc_ids = self.com.recv(self.other_party, MessageType.FIRST_ENC_IDS, timeout=1000.0)

    def _second_encrypt(self):
        # job starter can get intersection part
        self.second_encrypted_ids = [pow(_, self.private_key, self.p) for _ in self.other_first_enc_ids]
        self.com.send(self.other_party, MessageType.SECOND_ENC_IDS, self.second_encrypted_ids)
        self.other_second_enc_ids = self.com.recv(self.other_party, MessageType.SECOND_ENC_IDS, timeout=1000.0)
    
    def _compute_intersection(self):
        intersect_ids = set(self.second_encrypted_ids) & set(self.other_second_enc_ids)
        intersect_index = [idx for idx, i in enumerate(self.other_second_enc_ids) if i in intersect_ids]
        if self.return_index:
            self.result = intersect_index
        else:
            self.result = [self.original_ids[i] for i in intersect_index]

    def start(self, key_length=512):
        # check init params and input ids
        self.log.info(f"start compute intersection")
        self.__check_params()
        # 
        # TODO add data_loader 后续安排
        self._sync_prime_primitive_root(key_length)
        
        self._first_encrypt()

        self._second_encrypt()

        self._compute_intersection()
        
        return self.result


if __name__ == "__main__":
    # dh._sync_prime_primitive_root()
    pass