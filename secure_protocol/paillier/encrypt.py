import functools
from amalgam.secure_protocol.paillier.paillier import PaillierKeypair, PaillierEncryptedNumber


class PaillierEncrypt(object):
    def __init__(self):
        self.public_key = None
        self.privacy_key = None

    def generate_key(self, n_length=1024):
        self.public_key, self.privacy_key = PaillierKeypair.generate_keypair(
            n_length=n_length
        )

    def get_key_pair(self):
        return self.public_key, self.privacy_key

    def set_public_key(self, public_key):
        self.public_key = public_key

    def get_public_key(self):
        return self.public_key

    def set_privacy_key(self, privacy_key):
        self.privacy_key = privacy_key

    def get_privacy_key(self):
        return self.privacy_key

    def encrypt(self, value):
        if self.public_key is not None:
            return self.public_key.encrypt(value)
        else:
            return None

    def decrypt(self, value):
        if self.privacy_key is not None:
            return self.privacy_key.decrypt(value)
        else:
            return None

    def raw_encrypt(self, plaintext, exponent=0):
        cipher_int = self.public_key.raw_encrypt(plaintext)
        paillier_num = PaillierEncryptedNumber(public_key=self.public_key, ciphertext=cipher_int, exponent=exponent)
        return paillier_num

    def raw_decrypt(self, ciphertext):
        return self.privacy_key.raw_decrypt(ciphertext.ciphertext())

    def recursive_raw_encrypt(self, X, exponent=0):
        raw_en_func = functools.partial(self.raw_encrypt, exponent=exponent)
        return self._recursive_func(X, raw_en_func)
    


if __name__  == "__main__":
    # 测试phe和fate实现的哪个更快
    # 结果表明，两者性能上的差距很小
    from phe import paillier
    import time
    public_key, private_key = paillier.generate_paillier_keypair(n_length=1024)
    message_list = [3.1415926, 100, -4.6e-12]
    # 加密操作
    time_start_enc = time.time()
    encrypted_message_list1 = [public_key.encrypt(m) for m in message_list]
    print("加密耗时s:", time.time()-time_start_enc)
    # 解密操作
    time_start_dec = time.time()
    decrypted_message_list1 = [private_key.decrypt(c) for c in encrypted_message_list1]
    print("解密耗时s:", time.time()-time_start_dec)
    # print(encrypted_message_list[0])
    print("原始数据:", decrypted_message_list1)

    print("-"*100)
    # 加密操作
    cipher = PaillierEncrypt()
    cipher.generate_key(1024)
    time_start_enc = time.time()
    encrypted_message_list2 = [cipher.encrypt(m) for m in message_list]
    print("加密耗时s:", time.time()-time_start_enc)
    # 解密操作
    time_start_dec = time.time()
    decrypted_message_list2 = [cipher.decrypt(c) for c in encrypted_message_list2] 
    print("解密耗时s:", time.time()-time_start_dec)
    print("原始数据:", decrypted_message_list2)

    a, b, c = encrypted_message_list2
    time_start_dec = time.time()
    res = [a+b, a+c, c*10000]
    print(res)
    print("密文上计算耗时：", time.time()-time_start_dec)

    a, b, c = encrypted_message_list1
    time_start_dec = time.time()
    res = [a+b, a+c, c*10000]
    print(res)
    print("密文上计算耗时：", time.time()-time_start_dec)  

