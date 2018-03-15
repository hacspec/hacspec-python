#!/usr/bin/python3

# To run and check this file, you need Python 3 + mypy
# See install instructions at: http://mypy.readthedocs.io/en/latest/getting_started.html
# To typecheck this file: mypy poly1305.py
# To run this file: python3 poly1305.py

from speclib import *
import json

blocksize = 16
#block_t = refine(array[uint8],lambda a: len(a) == 16)
# to pass mypy: use the following
block_t = array[uint8] #length: blocksize

bytes_t = array[uint8] #length: arbitrary

p130m5 = (2 ** 130) - 5 # type: int

#p130m5_felem = refine(pfelem,lambda x: pfelem.get_prime(x) == p130m5) #Refinement type
# to pass mypy: use the following
p130m5_felem = pfelem #mypy compatible type

def to_felem(a:int) -> p130m5_felem:
    return pfelem(a,p130m5)

def encode(block:block_t) -> p130m5_felem:
    b = array.create(16,uint8(0))
    b[0:len(block)] = block
    welem = to_felem(int(bytes.to_uint128_le(b)))
    lelem = to_felem(2 ** (8 * len(block)))
    return (lelem + welem)

def encode_r(r:block_t) -> p130m5_felem:
    ruint = bytes.to_uint128_le(r)
    ruint = uint128(ruint & uint128(0x0ffffffc0ffffffc0ffffffc0fffffff))
    return  to_felem(int(ruint))

# There are many ways of writing the polynomial evaluation function
# This version: use a loop to accumulate the result
def poly(text:bytes_t,r:p130m5_felem) -> p130m5_felem:
    blocks,last = array.split_blocks(text,blocksize)
    acc = to_felem(0)
    for i in range(array.len(blocks)):
        acc = (acc + encode(blocks[i])) * r
    if (array.len(last) > 0):
        acc = (acc + encode(last)) * r
    return acc

def poly1305_mac(text:bytes_t,k:bytes_t) -> bytes_t :
    r = k[0:blocksize]
    s = k[blocksize:2*blocksize]
    relem = encode_r(r)
    selem = bytes.to_uint128_le(s)
    a = poly(text,relem)
    n = uint128(uint128(int(a)) + selem)
    return bytes.from_uint128_le(n)
