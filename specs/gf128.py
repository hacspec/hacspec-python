#!/usr/bin/python3

from lib.speclib import *

blocksize = 16
block_t = bytes_t(16)
key_t = bytes_t(16)
tag_t = bytes_t(16)
subblock_t,subblock = refine(vlbytes_t, lambda x: bytes.length(x) <= 16)
elem_t = bitvector_t(128)
elem = elem_t

# Define galois field
@typechecked
def elem(x:nat_t) -> elem_t:
    return bitvector(x, 128)

irred = elem(0xE1000000000000000000000000000000)

@typechecked
def elem_from_bytes(b:bytes_t(16)) -> elem_t:
    return elem(uintn.to_int(bytes.to_uint128_be(b)))
@typechecked
def elem_to_bytes(e:elem_t) -> bytes_t(16):
    return bytes.from_uint128_be(uint128(uintn.to_int(e)))
@typechecked
def fadd(x:elem_t,y:elem_t) -> elem_t:
    return x ^ y
@typechecked
def fmul(x:elem_t,y:elem_t) -> elem_t:
    res = elem(0)
    sh = x
    for i in range(128):
        if y[127-i] != bit(0):
            res ^= sh
        if sh[0] != bit(0):
            sh = (sh >> 1) ^ irred
        else:
            sh = sh >> 1
    return res

# Define GMAC
@typechecked
def encode(block:subblock_t) -> elem_t:
    b = bytes(array.create(16,uint8(0)))
    b[0:array.length(block)] = block
    return elem_from_bytes(b)

@typechecked
def decode(e:elem_t) -> block_t:
    return elem_to_bytes(e)

@typechecked
def update(r:elem_t,block:subblock_t,acc:elem_t) -> elem_t:
    return fmul(fadd(encode(subblock(block)),acc),r)

@typechecked
def poly(text:vlbytes_t,r:elem_t) -> elem_t:
    blocks,last = array.split_blocks(text,blocksize)
    acc = elem(0)
    for i in range(array.length(blocks)):
        acc = update(r,subblock(blocks[i]),acc)
    if (array.length(last) > 0):
        acc = update(r,subblock(bytes(last)),acc)
    return acc

@typechecked
def gmac(text:vlbytes_t,k:key_t) -> tag_t :
    s = subblock(bytes(array.create(blocksize,uint8(0))))
    r = encode(k)
    a = poly(text,r)
    m = decode(fadd(a,encode(s)))
    return m
