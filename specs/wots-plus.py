#!/usr/bin/env python3

from speclib import *
import sha2
import math

# Influences signature length, not security
w_two = uint32(4)
w_sixteen = uint32(16)

# F: SHA2-256(toByte(0, 32) || KEY || M),
# H: SHA2-256(toByte(1, 32) || KEY || M),
# H_msg: SHA2-256(toByte(2, 32) || KEY || M),
# PRF: SHA2-256(toByte(3, 32) || KEY || M).


def hash(prefix: array[uint8], key: array[uint8], m: array[uint8]) -> array[uint32]:
    h_in = array.create(uint8(0), 0)
    h_in.extend(prefix)
    h_in.extend(key)
    h_in.extend(m)
    return sha2.hash(h_in)


def F(key: array[uint8], m: array[uint8]) -> array[uint32]:
    return hash(array.create(uint8(0), 32), key, m)


def H(key: array[uint8], m: array[uint8]) -> array[uint32]:
    return hash(array.create(uint8(1), 32), key, m)


def H_msg(key: array[uint8], m: array[uint8]) -> array[uint32]:
    return hash(array.create(uint8(2), 32), key, m)


def PRF(key: array[uint8], m: array[uint8]) -> array[uint32]:
    return hash(array.create(uint8(3), 32), key, m)


# Parameters
# n := length (message, signature, key), SHA2 output length
n = 32  # type: int
w = w_two

length1 = uint32(int(math.ceil(8*n / math.log(uint32.int_value(w), 2))))
tmp = uint32.int_value(length1) * (uint32.int_value(w) - 1)
length2 = uint32(int(math.log(tmp, 2) // math.log(uint32.int_value(w), 2) + 1))
length = length1 + length2

# Address is a 32-byte array with the following definition
# 4-byte: layer address
# 8-byte: tree address
# 4-byte: type: 0 for OTS, 1 for L-tree, 2 for hash tree
# 4-byte: OTS address, L-tree address, padding (0)
# 4-byte: chain address, tree height, tree height
# 4-byte: hash address, tree index, tree index
# 4-byte: key and mask
address = NewType('address', array[uint8])
def set_hash_address(adr:address, h_adr:uint32) -> address:
    result = adr[:]
    result[192] = uint8((h_adr.as_int() & 0xFF000000) >> 24)
    result[200] = uint8((h_adr.as_int() & 0xFF0000) >> 16)
    result[208] = uint8((h_adr.as_int() & 0xFF00) >> 8)
    result[216] = uint8(h_adr.as_int() & 0xFF)
    return result

def set_key_and_mask(adr:address, kam:uint32) -> address:
    result = adr[:]
    result[224] = uint8((kam.as_int() & 0xFF000000) >> 24)
    result[232] = uint8((kam.as_int() & 0xFF0000) >> 16)
    result[240] = uint8((kam.as_int() & 0xFF00) >> 8)
    result[248] = uint8(kam.as_int() & 0xFF)
    return result

# Input: Input string X, start index i, number of steps s, seed SEED, address ADRS
# Output: value of F iterated s times on X
def wots_chain(x: array[uint32], index: int, steps: int, seed: array[uint8], adr: address) -> array[uint32]:
    if steps == 0:
        return x
    if index + steps > (w.as_int() - 1):
        return array([])
    tmp = wots_chain(x, index, steps - 1, seed, adr)

    adr = set_hash_address(adr,  uint32(index + steps -1))
    adr = set_key_and_mask(adr, uint32(0))
    key = PRF(seed, adr)
    adr = set_key_and_mask(adr, uint32(1))
    bm = PRF(seed, adr)

    tmp2 = array([]) # type: array[uint32]
    for (x, y) in zip(tmp, bm):
        tmp2.append(x ^ y)
    tmp = F(key, tmp2)
    return tmp


def key_gen() -> array[array[uint8]]:
    k = array([])  # type: array[array[uint8]]
    for i in range(0, uint32.int_value(length)):
        k_i = array.create_random_bytes(n)
        k.append(k_i)
    return k


def main(x: int) -> None:
    print("WOTS+ sk")
    sk = key_gen()
    for k in sk:
        print(k)


if __name__ == "__main__":
    main(0)
