#!/usr/bin/python3

from lib.speclib import *

blocksize : int = 16
# TODO: can't use blocksize as argument here due to compiler bug.
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
def load_elem(b:bytes_t(16)) -> elem_t:
    return bytes.to_uint128_be(b)


@typechecked
def store_elem(e:elem_t) -> bytes_t(16):
    return bytes.from_uint128_be(e)


# Define GMAC
@typechecked
def encode(block:subblock_t) -> elem_t:
    b : block_t = bytes(array.create(16,uint8(0)))
    b[0:array.length(block)] = block
    return load_elem(b)

@typechecked
def decode(e:elem_t) -> block_t:
    return store_elem(e)


@typechecked
def fadd(x:elem_t,y:elem_t) -> elem_t:
    return x ^ y
@typechecked
def fmul(x:elem_t,y:elem_t) -> elem_t:
    res : elem_t = elem(0)
    sh : elem_t = x
    index: int = 0
    for i in range(128):
        index = op_Subtraction(127, i)
        if y[index] != bit(0):
            res ^= sh
        if sh[0] != bit(0):
            sh = (sh >> 1) ^ irred
        else:
            sh = sh >> 1
    return res


@typechecked
def init(h: block_t) -> tuple_t (elem_t, elem_t):
    r: elem_t = encode(h)
    acc: elem_t = elem(0)
    return (r, acc)

@typechecked
def set_acc(st: tuple_t(elem_t, elem_t), acc: elem_t) -> tuple_t(elem_t, elem_t):
    r: elem_t
    accBefore: elem_t
    (r, accBefore) = st
    return (r, acc)

@typechecked
def update(r:elem_t,block:subblock_t,acc:elem_t) -> elem_t:
    accNew: elem_t = fmul(fadd(encode(block),acc),r)
    return accNew

@typechecked
def poly(text:vlbytes_t, acc: elem_t, r:elem_t) -> elem_t:
    blocks : vlarray_t(vlbytes_t)
    last : vlbytes_t
    blocks,last = array.split_blocks(text,blocksize)
    for i in range(array.length(blocks)):
        acc:elem_t = update(r,blocks[i],acc)
    if (array.length(last) > 0):
        acc:elem_t = update(r,bytes(last),acc)
    return acc    

@typechecked 
def finish(acc: elem_t, s: tag_t) -> tag_t:
    return decode(fadd(acc,encode(s)))

@typechecked
def gmul(text: vlbytes_t, h: block_t) -> tag_t:
    r: elem_t
    acc: elem_t
    (r, acc) = init(h)
    acc = poly(text, acc, r)
    return decode(acc)


@typechecked
def gmac(text:vlbytes_t,k:key_t) -> tag_t :
    s : block_t = bytes(array.create(blocksize,uint8(0)))
    r : elem_t  
    acc: elem_t
    (r, acc) = init(k)
    a : elem_t = poly(text,acc, r)
    m : block_t = finish(a, s)
    return m

# 