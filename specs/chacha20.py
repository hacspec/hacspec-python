#!/usr/bin/python3

# Run mypy chacha20.py to type check.

from speclib import *

index = int           # range: (0,16)
shiftval = int        # range: (0,32)
state = array[uint32] # length : 32
keyType = bytes       # length: 32
nonceType = bytes     # length: 12

def line(a: index, b: index, d: index, s: shiftval, m: state) -> state:
    m = array.copy(m)
    m[a] = (m[a] + m[b])
    m[d] = uint32.rotate_left(m[d] ^ m[a],s)
    return m

def quarter_round(a: index, b: index, c:index, d: index, m: state) -> state :
    m = line(a, b, d, 16, m)
    m = line(c, d, b, 12, m)
    m = line(a, b, d,  8, m)
    m = line(c, d, b,  7, m)
    return m

def inner_block(m: state) -> state :
    m = quarter_round(0, 4,  8, 12, m)
    m = quarter_round(1, 5,  9, 13, m)
    m = quarter_round(2, 6, 10, 14, m)
    m = quarter_round(3, 7, 11, 15, m)

    m = quarter_round(0, 5, 10, 15, m)
    m = quarter_round(1, 6, 11, 12, m)
    m = quarter_round(2, 7,  8, 13, m)
    m = quarter_round(3, 4,  9, 14, m)
    return m


constants = array([uint32(0x61707865), uint32(0x3320646e),
                   uint32(0x79622d32), uint32(0x6b206574)])

def chacha20_init(k: keyType, counter: uint32, nonce: nonceType) -> state:
    st = array.create(uint32(0),16)
    st[0:4] = constants
    st[4:12] = array.uint32s_from_bytes_le(k)
    st[12] = counter
    st[13:16] = array.uint32s_from_bytes_le(nonce)
    return st

def chacha20_core(st:state) -> state:
    working_state = array.copy(st)
    for x in range(1,11):
        working_state = inner_block(working_state)
    for i in range(16):
        working_state[i] += st[i]
    if (len(working_state) != 16):
        return array([uint32(0), uint32(0), uint32(0), uint32(0)])
    return working_state

@precondition(keyType, "> 0", nonceType)
def chacha20(k: keyType, counter: uint32, nonce: nonceType) -> state:
    return chacha20_core(chacha20_init(k,counter,nonce))

def chacha20_block(k: keyType, counter:int, nonce: nonceType) -> bytes:
    st = chacha20(k,uint32(counter),nonce)
    block = array.uint32s_to_bytes_le(st)
    return block

# Many ways of extending this to CTR
# First version: use generic higher-order ctr library
from ctr import counter_mode
def chacha20_encrypt(key: keyType, counter: int, nonce: nonceType, msg:bytes) -> bytes:
    return counter_mode(64,chacha20_block,
                        key,counter,nonce,msg)

def chacha20_decrypt(key: keyType, counter: int, nonce: nonceType, msg:bytes) -> bytes:
    return counter_mode(64,chacha20_block,
                        key,counter,nonce,msg)


# Second version: use first-order CTR function specific to Chacha20 with a loop

blocksize = 64
def xor_block(block:bytes, keyblock:bytes) -> bytes:
    out = array(list(block))
    for i in range(len(out)):
        out[i] ^= keyblock[i]
    return bytes(out)

def chacha20_counter_mode(key: keyType, counter: int, nonce: nonceType, msg:bytes) -> bytes:
    blocks = array.split_bytes(msg,blocksize)
    for i in range(0,len(blocks)):
        keyblock = chacha20_block(key,counter + i,nonce)
        blocks[i] = xor_block(blocks[i],keyblock)
    return array.concat_bytes(blocks)

def chacha20_encrypt_(key: keyType, counter: int, nonce: nonceType,msg:bytes) -> bytes:
    return chacha20_counter_mode(key,counter,nonce,msg)

def chacha20_decrypt_(key: keyType, counter: int, nonce: nonceType,msg:bytes) -> bytes:
    return chacha20_counter_mode(key,counter,nonce,msg)
