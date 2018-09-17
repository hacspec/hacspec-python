#!/usr/bin/python3

from lib.speclib import *

blocksize : int = 16
block_t = bytes_t(16)
key_t = bytes_t(16)
tag_t = bytes_t(16)
subblock_t,subblock = refine(vlbytes_t, lambda x: array.length(x) <= 16)
elem_t = uint128_t

# Define galois field
@typechecked
def elem(x:nat_t) -> elem_t:
    return uint128(x)

irred : elem_t = elem(0xE1000000000000000000000000000000)

@typechecked
def elem_from_bytes(b:bytes_t(16)) -> elem_t:
    return bytes.to_uint128_be(b)
@typechecked
def elem_to_bytes(e:elem_t) -> bytes_t(16):
    return bytes.from_uint128_be(e)
@typechecked
def fadd(x:elem_t,y:elem_t) -> elem_t:
    return x ^ y
@typechecked
def fmul(x:elem_t,y:elem_t) -> elem_t:
    res : elem_t = elem(0)
    sh : elem_t = x
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
    b : block_t = bytes(array.create(16,uint8(0)))
    b[0:array.length(block)] = block
    return elem_from_bytes(b)

@typechecked
def decode(e:elem_t) -> block_t:
    return elem_to_bytes(e)

@typechecked
def update(r:elem_t,block:subblock_t,acc:elem_t) -> elem_t:
    return fmul(fadd(encode(block),acc),r)

@typechecked
def poly(text:vlbytes_t,r:elem_t) -> elem_t:
    blocks : vlarray_t(vlbytes_t)
    last : vlbytes_t
    blocks,last = array.split_blocks(text,blocksize)
    acc : elem_t = elem(0)
    for i in range(array.length(blocks)):
        acc = update(r,blocks[i],acc)
    if (array.length(last) > 0):
        acc = update(r,bytes(last),acc)
    return acc

@typechecked
def gmac(text:vlbytes_t,k:key_t) -> tag_t :
    s : block_t = bytes(array.create(blocksize,uint8(0)))
    r : elem_t = encode(k)
    a : elem_t = poly(text,r)
    m : block_t = decode(fadd(a,encode(s)))
    return m
