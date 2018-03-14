#!/usr/bin/python3

# Run mypy chacha20.py to type check.

from speclib import *

index = int           # range: (0,16)
shiftval = int        # range: (0,32)
state = array[uint32] # length : 32
key_t = array[uint8]  # length: 32
nonce_t = array[uint8]# length: 12
bytes_t = array[uint8]# length arbitrary

def line(a: index, b: index, d: index, s: shiftval, m: state) -> state:
    m = array.copy(m)
    m = m.set(a, m[a] + m[b])
    m = m.set(d, uint32.rotate_left(m[d] ^ m[a],s))
    return m

def quarter_round(a: index, b: index, c:index, d: index, m: state) -> state :
    m = line(a, b, d, 16, m)
    m = line(c, d, b, 12, m)
    m = line(a, b, d,  8, m)
    m = line(c, d, b,  7, m)
    return m

def double_round(m: state) -> state :
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

def chacha20_init(k: key_t, counter: uint32, nonce: nonce_t) -> state:
    st = array.create(uint32(0),16)
    st = st.set((0, 4), constants)
    st = st.set((4, 12), bytes.to_uint32s_le(k))
    st = st.set(12, counter)
    st = st.set((13, 16), bytes.to_uint32s_le(nonce))
    return st

def chacha20_core(st:state) -> state:
    working_state = array.copy(st)
    for x in range(10):
        working_state = double_round(working_state)
    for i in range(16):
        working_state = working_state.set(i, working_state[i] + st[i])
    return working_state

def chacha20(k: key_t, counter: uint32, nonce: nonce_t) -> state:
    return chacha20_core(chacha20_init(k,counter,nonce))

def chacha20_block(k: key_t, counter:int, nonce: nonce_t) -> bytes_t:
    st = chacha20(k,uint32(counter),nonce)
    block = bytes.from_uint32s_le(st)
    return block

# Many ways of extending this to CTR
# First version: use generic higher-order ctr library
from ctr import counter_mode
def chacha20_encrypt_(key: key_t, counter: int, nonce: nonce_t, msg:bytes_t) -> bytes_t:
    return counter_mode(64,chacha20_block,
                        key,counter,nonce,msg)

def chacha20_decrypt_(key: key_t, counter: int, nonce: nonce_t, msg:bytes_t) -> bytes_t:
    return counter_mode(64,chacha20_block,
                        key,counter,nonce,msg)


# Second version: use first-order CTR function specific to Chacha20 with a loop

blocksize = 64
def xor_block(block:bytes_t, keyblock:bytes_t) -> bytes_t:
    out = array(list(block))
    for i in range(len(out)):
        out = out.set(i, out[i] ^ keyblock[i])
    return out

def chacha20_counter_mode(key: key_t, counter: int, nonce: nonce_t, msg:bytes_t) -> bytes_t:
    blocks = array.split_blocks(msg,blocksize)
    for i in range(0,len(blocks)):
        keyblock = chacha20_block(key,counter + i,nonce)
        blocks = blocks.set(i, xor_block(blocks[i],keyblock))
    return array.concat_blocks(blocks)

def chacha20_encrypt(key: key_t, counter: int, nonce: nonce_t,msg:bytes_t) -> bytes_t:
    return chacha20_counter_mode(key,counter,nonce,msg)

def chacha20_decrypt(key: key_t, counter: int, nonce: nonce_t,msg:bytes_t) -> bytes_t:
    return chacha20_counter_mode(key,counter,nonce,msg)
