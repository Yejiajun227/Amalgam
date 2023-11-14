import random
import gmpy2
import pyunit_prime as py_prime

POWMOD_GMP_SIZE = pow(2, 64)


def powmod(a, b, c):
    """
    return int: (a ** b) % c
    """
    if a == 1:
        return 1
    if max(a, b, c) < POWMOD_GMP_SIZE:
        return pow(a, b, c)
    else:
        return int(gmpy2.powmod(a, b, c))
    

def gcd(a, b):
    return int(gmpy2.gcd(a, b))


def get_prime(n):
    """return a random n-bit prime number
    """
    return py_prime.get_large_prime_bit_size(n)


def next_prime(n):
    return int(gmpy2.next_prime(n))


def is_prime(n):
    """
    true if n is a prime, false otherwise
    :param n:
    :return: bool
    """
    return gmpy2.is_prime(int(n))


def generate_primitive_root(p):
    # 生成大素数p的原根
    # 有几个特例算不对，不清楚原因，素数7681的原根是17，带入公式算出来的是13
    g = 2
    while pow(g, (p-1)//2, p) == 1 or pow(g, (p-1)//3, p) == 1:
        g += 1
    return g


def crt_coefficient(p, q):
    """
    return crt coefficient
    """
    tq = gmpy2.invert(p, q)
    tp = gmpy2.invert(q, p)
    return tp * q, tq * p


def mpz(n):
    return gmpy2.mpz(n)


def invert(a, b):
    """return int: x, where a * x == 1 mod b"""
    x = int(gmpy2.invert(a, b))

    if x == 0:
        raise ZeroDivisionError("invert(a, b) no inverse exists")

    return x