#!/usr/bin/python3

from lib.speclib import *

blocksize:int = 16
block_t = bytes_t(16)
key_t = bytes_t(32)
tag_t = bytes_t(16)
subblock_t = refine_t(vlbytes_t, lambda x: bytes.length(x) <= 16)


# Define prime field

p130m5 : nat_t = (2 ** 130) - 5
felem_t = natmod_t(p130m5)
@typechecked
def felem(n:nat_t) -> felem_t:
    return natmod(n,p130m5)

@typechecked
def encode(block: subblock_t) -> felem_t:
    b = array.create(16, uint8(0))
    b[0:bytes.length(block)] = block
    welem = felem(uintn.to_nat(bytes.to_uintn_le(b)))
    lelem = felem(nat(2 ** (8 * array.length(block))))
    return lelem + welem

@typechecked
def encode_r(r: block_t) -> felem_t:
    ruint = bytes.to_uint128_le(r)
    ruint = ruint & uint128(0x0ffffffc0ffffffc0ffffffc0fffffff)
    r_nat = uintn.to_nat(ruint)
    return felem(r_nat)

# There are many ways of writing the polynomial evaluation function
# This version: use a loop to accumulate the result
@typechecked
def poly(text: vlbytes_t, r: felem_t) -> felem_t:
    blocks, last = array.split_blocks(text, blocksize)
    acc = felem(nat(0))
    for i in range(array.length(blocks)):
        acc = (acc + encode(blocks[i])) * r
    if (array.length(last) > 0):
        acc = (acc + encode(last)) * r
    return acc


@typechecked
def poly1305_mac(text: vlbytes_t, k: key_t) -> tag_t:
    r = k[0:blocksize]
    s = k[blocksize:2*blocksize]
    relem = encode_r(r)
    selem = bytes.to_uint128_le(s)
    a = poly(text, relem)
    n = uint128(natmod.to_nat(a)) + selem
    return tag_t(bytes.from_uintn_le(n))
