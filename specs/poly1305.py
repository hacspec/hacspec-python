#!/usr/bin/python3

# To run and check this file, you need Python 3 + mypy
# See install instructions at: http://mypy.readthedocs.io/en/latest/getting_started.html
# To typecheck this file: mypy poly1305.py
# To run this file: python3 poly1305.py

from speclib import *
import json

p130m5 = (2 ** 130) - 5 # type: int

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

def foo0(bla="blub", blub="bladefault"):
    if bla == "blub":
        print("a")
    elif blub == "a":
        print("b")
    else:
        print("c")
    print(bla)

# There are many ways of writing the polynomial evaluation function
# First version: use a loop to accumulate the result
blocksize = 16
def poly(text:bytes,r:felem) -> felem:
    blocks = array.split_bytes(text,blocksize)
    acc = felem(0)
    for i in range(len(blocks)):
        acc = fmul(fadd(acc,encode(blocks[i])),r)
    return acc

# Second version: use higher-order reduce
from functools import reduce
def poly_reduce(tlen:int,text:bytes,r:felem) -> felem:
    def accumulate(acc:felem,block:bytes) -> felem:
        return (fmul(fadd(acc,encode(block)),r))
    blocks = array.split_bytes(text,blocksize)
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
