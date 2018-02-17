#!/usr/bin/python3

# To run and check this file, you need Python 3 + mypy
# See install instructions at: http://mypy.readthedocs.io/en/latest/getting_started.html
# To typecheck this file: mypy poly1305.py
# To run this file: python3 poly1305.py

from speclib import *
import json

p130m5 = (2 ** 130) - 5 # type: int

class Felem:
    def __init__(self,x:felem) -> None:
        self.v = x
    def __str__(self) -> str:
        return str(self.v)
    def __repr__(self) -> str:
        return repr(self.v)
    def __add__(self,other:'Felem') -> 'Felem':
        return Felem(int(self.v + other.v) % p130m5)
    def __mul__(self,other:'Felem') -> 'Felem':
        return Felem(int(self.v * other.v) % p130m5)
    def __pow__(self,other:int) -> 'Felem':
        return Felem(int(self.v ** other) % p130m5)
    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return self.v == other.v
    def to128(self) -> uint128:
        return uint128(self.v)

def encode(block:bytes) -> Felem:
    welem = Felem(uint128.int_value(uint128.from_bytes_le(block)))
    lelem = Felem(2 ** (8 * len(block)))
    return lelem + welem

def encode_r(r:bytes) -> Felem:
    ruint = uint128.from_bytes_le(r)
    ruint &= uint128(0x0ffffffc0ffffffc0ffffffc0fffffff)
    return Felem(uint128.int_value(ruint))

blocksize = 16

def poly(text:bytes,r:Felem) -> Felem:
    blocks = array.split_bytes(text,blocksize)
    return sum((encode(block) * r**(len(blocks)-i)
                for i, block in enumerate(blocks)),
               Felem(0))

def poly1305_mac(text:bytes,k:bytes) -> bytes :
    r = k[0:blocksize]
    s = k[blocksize:2*blocksize]
    relem = encode_r(r)
    selem = uint128.from_bytes_le(s)
    a = poly(text,relem)
    n = a.to128() + selem
    return uint128.to_bytes_le(n)

from test_vectors.poly1305_test_vectors import poly1305_test_vectors

def main (x: int) -> None :
    # RFC 7539 Test Vectors
    msg = bytes([
        0x43, 0x72, 0x79, 0x70, 0x74, 0x6f, 0x67, 0x72,
        0x61, 0x70, 0x68, 0x69, 0x63, 0x20, 0x46, 0x6f,
        0x72, 0x75, 0x6d, 0x20, 0x52, 0x65, 0x73, 0x65,
        0x61, 0x72, 0x63, 0x68, 0x20, 0x47, 0x72, 0x6f,
        0x75, 0x70])
    k = bytes([
        0x85, 0xd6, 0xbe, 0x78, 0x57, 0x55, 0x6d, 0x33,
        0x7f, 0x44, 0x52, 0xfe, 0x42, 0xd5, 0x06, 0xa8,
        0x01, 0x03, 0x80, 0x8a, 0xfb, 0x0d, 0xb2, 0xfd,
        0x4a, 0xbf, 0xf6, 0xaf, 0x41, 0x49, 0xf5, 0x1b])
    expected = bytes([
        0xa8, 0x06, 0x1d, 0xc1, 0x30, 0x51, 0x36, 0xc6,
        0xc2, 0x2b, 0x8b, 0xaf, 0x0c, 0x01, 0x27, 0xa9 ])
    computed = poly1305_mac(msg,k)
    if (computed == expected):
        print("Poly1305 Test  0 passed.")
    else:
        print("Poly1305 Test  0 failed:")
        print("expected mac:",expected)
        print("computed mac:",computed)
    with open("test_vectors/poly1305_test_vectors.json") as json_data:
        poly1305_test_vectors = json.load(json_data)
        for i in range(len(poly1305_test_vectors)):
            msg = bytes.fromhex(poly1305_test_vectors[i]['input'])
            k   = bytes.fromhex(poly1305_test_vectors[i]['key'])
            expected = bytes.fromhex(poly1305_test_vectors[i]['tag'])
            computed = poly1305_mac(msg,k)
            if (computed == expected):
                print("Poly1305 Test ",i+1," passed.")
            else:
                print("Poly1305 Test ",i+1," failed:")
                print("expected mac:",expected)
                print("computed mac:",computed)



main(0)
