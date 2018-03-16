#!/usr/bin/python3

from speclib import *

blocksize = 16

#for fstar: use the following
block_t = bytes_t(16)
key_t = bytes_t(32)
tag_t = bytes_t(16)
subblock_t = refine(vlbytes_t,lambda x: vlbytes.length(x) <= 16)

#to pass mypy: use the following
#block_t = array[uint8] 
#key_t = array[uint8]
#tag_t = array[uint8]

p130m5 = (2 ** 130) - 5 # type: int
felem_t = refine(nat,lambda x: x < p130m5)
def felem(x:nat) -> felem_t:
    return (x % p130m5)
def fadd(x:felem_t,y:felem_t) -> felem_t:
    return felem(x + y)
def fmul(x:felem_t,y:felem_t) -> felem_t:
    return felem(x * y)

# to pass mypy: use the following
#felem_t = pfelem_t
#felem = pfelem

def encode(block:subblock_t) -> felem_t:
    b = array.create(16,uint8(0))
    b[0:array.length(block)] = block
    welem = felem(uint128.to_int(bytes.to_uint128_le(b)))
    lelem = felem(2 ** (8 * array.length(block)))
    return fadd(lelem,welem)

def encode_r(r:block_t) -> felem_t:
    ruint = bytes.to_uint128_le(r)
    ruint = ruint & uint128(0x0ffffffc0ffffffc0ffffffc0fffffff)
    return  felem(uint128.to_int(ruint))

# There are many ways of writing the polynomial evaluation function
# This version: use a loop to accumulate the result
def poly(text:vlbytes_t,r:felem_t) -> felem_t:
    blocks,last = array.split_blocks(text,blocksize)
    acc = felem(0)
    for i in range(array.length(blocks)):
        acc = fmul(fadd(acc,encode(blocks[i])),r)
    if (array.length(last) > 0):
        acc = fmul(fadd(acc,encode(last)),r)
    return acc

def poly1305_mac(text:vlbytes_t,k:key_t) -> tag_t :
    r = k[0:blocksize]
    s = k[blocksize:2*blocksize]
    relem = encode_r(r)
    selem = bytes.to_uint128_le(s)
    a = poly(text,relem)
    n = uint128(uint128(a) + selem)
    return bytes.from_uint128_le(n)
