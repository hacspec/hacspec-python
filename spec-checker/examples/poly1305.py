#!/usr/bin/python3

# To run and check this file, you need Python 3 + mypy
# See install instructions at: http://mypy.readthedocs.io/en/latest/getting_started.html
# To typecheck this file: mypy poly1305.py
# To run this file: python3 poly1305.py

from speclib import *
from typing import List, NewType

p130m5 = (2 ** 130) - 5 # type: int
felem = NewType('felem',int)

def fadd(a:felem,b:felem) -> felem:
    return felem((a + b) % p130m5)
def fmul(a:felem,b:felem) -> felem:
    return felem((a * b) % p130m5)

def encode(block:bytes) -> felem:
    welem = felem(uint128.int_value(uint128.from_bytes_le(block)))
    lelem = felem(2 ** (8 * len(block)))
    return fadd(lelem,welem)

def encode_r(r:bytes) -> felem:
    ruint = uint128.from_bytes_le(r)
    ruint &= uint128(0x0ffffffc0ffffffc0ffffffc0fffffff)
    return  felem(uint128.int_value(ruint))

# There are many ways of writing the polynomial evaluation function
# First version: use a loop to accumulate the result
blocksize = 16
def poly(text:bytes,r:felem) -> felem:
    blocks = split_blocks(text,blocksize)
    acc = felem(0)
    for i in range(len(blocks)):
        blen = len(blocks[i])
        acc = fmul(fadd(acc,encode(blocks[i])),r)
    return acc

# Second version: use higher-order reduce
from functools import reduce
def poly_reduce(tlen:int,text:bytes,r:felem) -> felem:
    def accumulate(acc:felem,block:bytes) -> felem:
        return (fmul(fadd(acc,encode(block)),r))
    blocks = split_blocks(text,blocksize)
    acc = reduce(accumulate, blocks, felem(0))
    return acc

def poly1305_mac(text:bytes,k:bytes) -> bytes :
    r = k[0:blocksize]
    s = k[blocksize:2*blocksize]
    relem = encode_r(r)
    selem = uint128.from_bytes_le(s)
    a = poly(text,relem)
    n = uint128(a) + selem
    return uint128.to_bytes_le(n)


def main (x: int) :
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
    print("expected mac:",expected)
    print("computed mac:",computed)
    assert(computed == expected)

main(0)
