#!/usr/bin/python3

from lib.speclib import *

blocksize:nat_t = 64
index_t  = range_t(0,16)
rotval_t = range_t(1,32)
state_t  = array_t(uint32_t,16)
key_t    = bytes_t(32)
nonce_t  = bytes_t(12)
block_t  = bytes_t(64)
subblock_t = refine_t(vlbytes_t, lambda x: array.length(x) <= blocksize)
constants_t = array_t(uint32_t,4)


@typechecked
def line(a: index_t, b: index_t, d: index_t, s: rotval_t, m: state_t) -> state_t:
    m    = array.copy(m)
    m[a] = m[a] + m[b]
    m[d] = m[d] ^ m[a]
    m[d] = uintn.rotate_left(m[d],s)
    return m

@typechecked
def quarter_round(a: index_t, b: index_t, c:index_t, d: index_t, m: state_t) -> state_t :
    m: state_t = line(a, b, d, 16, m)
    m = line(c, d, b, 12, m)
    m = line(a, b, d,  8, m)
    m = line(c, d, b,  7, m)
    return m

@typechecked
def column_round (m: state_t) -> state_t: 
    m: state_t = quarter_round(0, 4,  8, 12, m)
    m = quarter_round(1, 5,  9, 13, m)
    m = quarter_round(2, 6, 10, 14, m)
    m = quarter_round(3, 7, 11, 15, m)
    return m

@typechecked
def diagonal_round (m: state_t) -> state_t: 
    m: state_t = quarter_round(0, 5, 10, 15, m)
    m = quarter_round(1, 6, 11, 12, m)
    m = quarter_round(2, 7,  8, 13, m)
    m = quarter_round(3, 4,  9, 14, m)
    return m

@typechecked
def double_round(m: state_t) -> state_t :
    m: state_t = column_round(m)
    m = diagonal_round(m)
    return m


@typechecked
def chacha20_core(st:state_t) -> state_t:
    # working_state : state_t
    working_state : state_t = array.copy(st)
    for x in range(10):
        working_state = double_round(working_state)
    for i in range(16):
        working_state[i] += st[i]
    return working_state

c0 : uint32_t = uint32(0x61707865)
c1 : uint32_t = uint32(0x3320646e)
c2 : uint32_t = uint32(0x79622d32)
c3 : uint32_t = uint32(0x6b206574)

@typechecked
def chacha20_set_counter(st: state_t, c: uint32_t) -> state_t:
    st[12] = c
    return st

@typechecked
def setup(k: key_t, nonce: nonce_t, st: state_t) -> state_t:
    st[0] = c0
    st[1] = c1
    st[2] = c2 
    st[3] = c3
    st[4:12] = bytes.to_uint32s_le(k)
    st[13:16] = bytes.to_uint32s_le(nonce)
    return st

@typechecked
def chacha20_init(k: key_t, nonce: nonce_t) -> state_t:
    st : state_t
    st : state_t = array.create(16,uint32(0))
    st = setup(k,  nonce, st)
    return st

@typechecked
def chacha20(k: key_t, counter: uint32_t, nonce: nonce_t) -> state_t:
    st: state_t
    st = chacha20_init(k, nonce)
    st = chacha20_set_counter(st, counter)
    return chacha20_core(st)

@typechecked
def chacha20_key_block(st: state_t) -> block_t:
    st : state_t
    block : block_t
    st = chacha20_core(st)
    block = bytes.from_uint32s_le(st)
    return block

@typechecked
def chacha20_key_block0(k: key_t, counter: uint32_t, nonce: nonce_t) -> block_t:
    st: state_t 
    block : block_t
    st = chacha20_init(k,nonce)
    st = chacha20_set_counter(st, counter)
    block =  chacha20_key_block(st)
    return block


# Many ways of extending this to CTR
# This version: use first-order CTR function specific to Chacha20 with a loop

@typechecked
def xor_block(block:block_t, keyblock:block_t) -> block_t:
    out : block_t = bytes.copy(block)
    for i in range(blocksize):
        out[i] ^= keyblock[i]
    return out

@typechecked
def chacha_encrypt_block(st0: state_t, c: uint32_t, b: block_t) -> block_t:
    st:state_t = chacha20_set_counter(st0, c)
    kb: block_t = chacha20_key_block(st) 
    return xor_block(b, kb)

# @typechecked
# def chacha_encrypt_last(st0: state_t, ctr0: uint32_t, incr: uint32_t, msg: vlbytes_t) -> vlbytes_t:
#     plain:block_t  = array.create(blocksize, uint8(0))
#     keyblock = chacha20_key_block0(key, ctr, nonce)

# def chacha_encrypt_last(key, ctr, nonce, last):
#     keyblock: block_t  = array.create(blocksize, uint8(0))

#     keyblock = chacha20_key_block0(key, ctr, nonce)
#     last_block[0:array.length(last)] = last
#     last_block = xor_block(last_block, keyblock)
#     last = last_block[0:array.length(last)]
#     return array.concat_blocks(blocks, last)

@typechecked
def chacha_encrypt_last(key: key_t, ctr : uint32_t, nonce : nonce_t, last : subblock_t) -> vlbytes_t:
    keyblock: block_t  = array.create(blocksize, uint8(0))
    last_block : block_t  = array.create(blocksize, uint8(0))

    keyblock = chacha20_key_block0(key, ctr, nonce)
    last_block[0:array.length(last)] = last
    last_block = xor_block(last_block, keyblock)
    last: block_t = last_block[0:array.length(last)]
    return last

@typechecked
def chacha20_counter_mode(key: key_t, counter: uint32_t, nonce: nonce_t, msg:vlbytes_t) -> vlbytes_t:
    blocks   : vlarray_t(block_t)
    last     : subblock_t
    blocks, last = array.split_blocks(msg, blocksize)
    keyblock   : block_t  = array.create(blocksize, uint8(0))
    last_block : block_t  = array.create(blocksize, uint8(0))
    ctr        : uint32_t = counter

    st: state_t 
    st = chacha20_init(key, nonce)
    
    for i in range(array.length(blocks)):
        blocks[i] = chacha_encrypt_block(st, ctr, blocks[i])
        ctr += counter
  
    keyblock = chacha20_key_block0(key, ctr, nonce)
    last_block[0:array.length(last)] = last
    last_block = xor_block(last_block, keyblock)
    last = last_block[0:array.length(last)]
    return array.concat_blocks(blocks, last)

@typechecked
def chacha20_encrypt_bytes(key: key_t, counter: uint32_t, nonce: nonce_t, msg:vlbytes_t) -> vlbytes_t:
    return chacha20_counter_mode(key,counter,nonce,msg)

@typechecked
def chacha20_decrypt(key: key_t, counter: uint32_t, nonce: nonce_t, msg:vlbytes_t) -> vlbytes_t:
    return chacha20_counter_mode(key,counter,nonce,msg)
