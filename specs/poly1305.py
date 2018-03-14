#!/usr/bin/python3

# To run and check this file, you need Python 3 + mypy
# See install instructions at: http://mypy.readthedocs.io/en/latest/getting_started.html
# To typecheck this file: mypy poly1305.py
# To run this file: python3 poly1305.py

from speclib import *
import json

block_t = array[uint8] #length <= 16
bytes_t = array[uint8] #length: arbitrary

p130m5 = (2 ** 130) - 5 # type: int

def fadd(a:felem,b:felem) -> felem:
    return felem((a + b) % p130m5)
def fmul(a:felem,b:felem) -> felem:
    return felem((a * b) % p130m5)

def encode(block:block_t) -> felem:
    b = array.create(uint8(0),16)
    b = b.set((0, len(block)), block)
    welem = felem(uint128.int_value(bytes.to_uint128_le(b)))
    lelem = felem(2 ** (8 * len(block)))
    return fadd(lelem,welem)

def encode_r(r:block_t) -> felem:
    ruint = bytes.to_uint128_le(r)
    ruint = uint128(ruint & uint128(0x0ffffffc0ffffffc0ffffffc0fffffff))
    return  felem(uint128.int_value(ruint))

# There are many ways of writing the polynomial evaluation function
# First version: use a loop to accumulate the result
blocksize = 16
def poly(text:bytes_t,r:felem) -> felem:
    blocks = array.split_blocks(text,blocksize)
    acc = felem(0)
    for i in range(len(blocks)):
        acc = fmul(fadd(acc,encode(blocks[i])),r)
    return acc

# Second version: use higher-order reduce
from functools import reduce
def poly_reduce(tlen:int,text:bytes_t,r:felem) -> felem:
    def accumulate(acc:felem,block:block_t) -> felem:
        return (fmul(fadd(acc,encode(block)),r))
    blocks = array.split_blocks(text,blocksize)
    acc = reduce(accumulate, blocks, felem(0))
    return acc

def poly1305_mac(text:bytes_t,k:bytes_t) -> bytes_t :
    r = k[0:blocksize]
    s = k[blocksize:2*blocksize]
    relem = encode_r(r)
    selem = bytes.to_uint128_le(s)
    a = poly(text,relem)
    n = uint128(uint128(a) + selem)
    return bytes.from_uint128_le(n)
