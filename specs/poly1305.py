#!/usr/bin/python3

from lib.speclib import *

blocksize:nat_t  = 16
block_t = bytes_t(16)
key_t = bytes_t(32)
tag_t = bytes_t(16)
subblock_t = refine_t(vlbytes_t, lambda x: array.length(x) <= 16)

# Define prime field
p130m5 : int = op_Subtraction(pow2 (130), 5)
felem_t = natmod_t(p130m5)

@typechecked
def felem(n:nat_t) -> felem_t:
    return natmod(n,p130m5)

@typechecked
def from_elem(x: felem_t) -> nat_t:
    return x  

@typechecked
def update1 (block: subblock_t, acc: felem_t, r:felem_t) -> felem_t:
    b : block_t = array.create(16, uint8(0))
    b[0:bytes.length(block)] = block
    n : felem_t = felem(pow2(8 * array.length(block))) + felem(bytes.to_nat_le(b))
    acc: felem_t = (n + acc) * r
    return acc

@typechecked
def encode(block: subblock_t) -> felem_t:
    b : block_t = array.create(16, uint8(0))
    b[0:bytes.length(block)] = block
    n : felem_t = felem(pow2(8 * array.length(block))) + felem(bytes.to_nat_le(b))
    return n


# There are many ways of writing the polynomial evaluation function
# This version: use a loop to accumulate the result
@typechecked
def poly(text: vlbytes_t, acc: felem_t, r: felem_t) -> felem_t:
    blocks : vlarray_t(block_t)
    last : subblock_t
    blocks, last = array.split_blocks(text, blocksize)
    for i in range(array.length(blocks)):
        acc:felem_t = update1(blocks[i], acc, r)
    if (array.length(last) > 0):
        acc:felem_t = update1(last, acc, r) 
    return acc

@typechecked
def finish(acc: felem_t , selem: uint128_t) -> vlbytes_t:
    n : uint128_t = uint128(natmod.to_nat(acc)) + selem
    return bytes.from_uint128_le(n)

@typechecked
def encode_r(r: block_t) -> felem_t:
    r[3] = r[3] & uint8(15)
    r[7] = r[7] & uint8(15)
    r[11] = r[11] & uint8(15)
    r[15] = r[15] & uint8(15)
    r[4] = r[4] & uint8(252)
    r[8] = r[8] & uint8(252)
    r[12] = r[12] & uint8(252)
    ruint : uint128_t = bytes.to_uint128_le(r)
    r_nat : nat_t = uintn.to_nat(ruint)
    return felem(r_nat)


@typechecked
def poly1305_init(k: key_t) -> tuple_t(felem_t, uint128_t, felem_t):
    r : block_t = k[0:blocksize]
    s : block_t = k[blocksize:op_Multiply(2,blocksize)]
    relem : felem_t = encode_r(r)
    selem : uint128_t = bytes.to_uint128_le(s)
    acc : felem_t = felem(0)
    return (relem, selem, acc)


@typechecked
def poly1305_mac(text: vlbytes_t, k: key_t) -> tag_t:
    relem: felem_t = felem(0)
    selem : uint128_t = uint128(0)
    acc: felem_t = felem(0)
    relem, selem, acc = poly1305_init(k)
    # r : block_t = k[0:blocksize]
    # s : block_t = k[blocksize:op_Multiply(2,blocksize)]
    # relem : felem_t = encode_r(r)
    # selem : uint128_t = bytes.to_uint128_le(s)
    # acc : felem_t = felem(0)
    a : felem_t   = poly(text, acc, relem)
    return finish(a, selem)
