import random
from amalgam.util.math_func import is_prime, gcd, powmod, next_prime


class PohligHellman(object):
    """
    A commutative encryption scheme inspired by Pohlig, Stephen, and Martin Hellman. "An improved algorithm
        for computing logarithms over GF (p) and its cryptographic significance." 1978
    Enc(x) = x^a mod p, with public knowledge p being a prime and satisfying that (p - 1) / 2 is also a prime
    Dec(y) = y^(a^(-1) mod phi(p)) mod p
    """
    def __init__(self, mod_base, exponent=None):
        """
        :param exponent: int
        :param mod_base: int
        """
        self.mod_base = mod_base    # p
        if exponent is not None and gcd(exponent, mod_base - 1) != 1:
            raise ValueError("In Pohlig, exponent and the totient of the modulo base must be coprimes")
        self.exponent = exponent    # a

    @staticmethod
    def generate_key(key_size=1024):
        """
        Generate a self-typed object with public mod_base and vacant exponent
        :param key_size: int
        :return: PohligHellman
        """
        key_size_half = key_size // 2
        while True:
            mod_base_half = PohligHellman.generate_prime(2 ** (key_size_half - 1), 2 ** key_size_half - 1)
            mod_base = mod_base_half * 2 + 1
            if is_prime(mod_base):
                return PohligHellman(mod_base)

    @staticmethod
    def generate_prime(left, right):
        """
        Generate a prime over (left, right]
        :param left:
        :param right:
        :return:
        """
        while True:
            random_integer = random.randint(left, right)
            random_prime = next_prime(random_integer)
            if random_prime <= right:
                return random_prime

    def init_private_key(self):
        """
        Init self.exponent
        :return:
        """
        while True:
            self.exponent = random.randint(2, self.mod_base)
            if gcd(self.exponent, self.mod_base - 1) == 1:
                return self.exponent
