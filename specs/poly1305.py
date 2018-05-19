#!/usr/bin/python3

from hacspec.speclib import *

blocksize = 16
block_t = bytes_t(16)
key_t = bytes_t(32)
tag_t = bytes_t(16)
subblock_t = refine(vlbytes, lambda x: vlbytes.length(x) <= 16)
subblock = subblock_t


# Define prime field

p130m5 = nat((2 ** 130) - 5)
felem_t = refine(nat, lambda x: x < p130m5)
felem = felem_t


@typechecked
def to_felem(x: nat_t) -> felem_t:
    return felem(nat(x % p130m5))


@typechecked
def fadd(x: felem_t, y: felem_t) -> felem_t:
    return to_felem(x + y)


@typechecked
def fmul(x: felem_t, y: felem_t) -> felem_t:
    return to_felem(nat(x * y))


@typechecked
def encode(block: subblock_t) -> felem_t:
    b = block_t.create(16, uint8(0))
    b[0:array.length(block)] = block
    welem = to_felem(uint128.to_nat(bytes.to_uint128_le(b)))
    lelem = to_felem(nat(2 ** (8 * array.length(block))))
    return fadd(lelem, welem)


@typechecked
def encode_r(r: block_t) -> felem_t:
    ruint = bytes.to_uint128_le(r)
    ruint = ruint & uint128(0x0ffffffc0ffffffc0ffffffc0fffffff)
    r_nat = uint128.to_nat(ruint)
    return to_felem(r_nat)

# There are many ways of writing the polynomial evaluation function
# This version: use a loop to accumulate the result
@typechecked
def poly(text: vlbytes_t, r: felem_t) -> felem_t:
    blocks, last = vlarray.split_blocks(text, blocksize)
    acc = felem(nat(0))
    for i in range(array.length(blocks)):
        acc = fmul(fadd(acc, encode(subblock(blocks[i]))), r)
    if (array.length(last) > 0):
        acc = fmul(fadd(acc, encode(subblock(bytes(last)))), r)
    return acc


@typechecked
def poly1305_mac(text: vlbytes_t, k: key_t) -> tag_t:
    r = k[0:blocksize]
    s = k[blocksize:2*blocksize]
    relem = encode_r(r)
    selem = bytes.to_uint128_le(s)
    a = poly(text, relem)
    n = uint128(uint128(a) + selem)
    return tag_t(bytes.from_uint128_le(n))
