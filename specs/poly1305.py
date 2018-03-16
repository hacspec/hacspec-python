#!/usr/bin/python3

from speclib import *

blocksize = 16

#for fstar: use the following
block_t = bytes_t(16)
key_t = bytes_t(32)
tag_t = bytes_t(16)

#to pass mypy: use the following
#block_t = array[uint8] 
#key_t = array[uint8]
#tag_t = array[uint8]

p130m5 = (2 ** 130) - 5 # type: int

#p130m5_felem = refine(pfelem,lambda x: pfelem.get_prime(x) == p130m5) #Refinement type
# to pass mypy: use the following
p130m5_felem = pfelem #mypy compatible type

def to_felem(a:int) -> p130m5_felem:
    return pfelem(a,p130m5)

def encode(block:block_t) -> p130m5_felem:
    b = array.create(16,uint8(0))
    b[0:array.length(block)] = block
    welem = to_felem(int(bytes.to_uint128_le(b)))
    lelem = to_felem(2 ** (8 * len(block)))
    return (lelem + welem)

def encode_r(r:block_t) -> p130m5_felem:
    ruint = bytes.to_uint128_le(r)
    ruint = uint128(ruint & uint128(0x0ffffffc0ffffffc0ffffffc0fffffff))
    return  to_felem(int(ruint))

# There are many ways of writing the polynomial evaluation function
# This version: use a loop to accumulate the result
def poly(text:vlbytes_t,r:p130m5_felem) -> p130m5_felem:
    blocks,last = array.split_blocks(text,blocksize)
    acc = to_felem(0)
    for i in range(array.length(blocks)):
        acc = (acc + encode(blocks[i])) * r
    if (array.length(last) > 0):
        acc = (acc + encode(last)) * r
    return acc

def poly1305_mac(text:vlbytes_t,k:key_t) -> tag_t :
    r = k[0:blocksize]
    s = k[blocksize:2*blocksize]
    relem = encode_r(r)
    selem = bytes.to_uint128_le(s)
    a = poly(text,relem)
    n = uint128(uint128(int(a)) + selem)
    return bytes.from_uint128_le(n)
