from hacspec.speclib import *

blocksize = 64
index_t  = range_t(0,16)
rotval_t = range_t(1,32)
state_t  = array_t(uint32_t,16)
key_t    = bytes_t(32)
nonce_t  = bytes_t(12)
block_t  = bytes_t(64)
subblock_t  = refine(vlbytes_t, lambda x: array.length(x) <= blocksize)
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
    m = line(a, b, d, 16, m)
    m = line(c, d, b, 12, m)
    m = line(a, b, d,  8, m)
    m = line(c, d, b,  7, m)
    return m

@typechecked
def double_round(m: state_t) -> state_t :
    m = quarter_round(0, 4,  8, 12, m)
    m = quarter_round(1, 5,  9, 13, m)
    m = quarter_round(2, 6, 10, 14, m)
    m = quarter_round(3, 7, 11, 15, m)

    m = quarter_round(0, 5, 10, 15, m)
    m = quarter_round(1, 6, 11, 12, m)
    m = quarter_round(2, 7,  8, 13, m)
    m = quarter_round(3, 4,  9, 14, m)
    return m


constants = constants_t(
    [uint32(0x61707865), uint32(0x3320646e),
     uint32(0x79622d32), uint32(0x6b206574)])

@typechecked
def chacha20_init(k: key_t, counter: uint32_t, nonce: nonce_t) -> state_t:
    st = array.create(16,uint32(0))
    st[0:4] = constants
    st[4:12] = bytes.to_uint32s_le(k)
    st[12] = counter
    st[13:16] = bytes.to_uint32s_le(nonce)
    return st

@typechecked
def chacha20_core(st:state_t) -> state_t:
    working_state = array.copy(st)
    for x in range(10):
        working_state = double_round(working_state)
    for i in range(16):
        working_state[i] += st[i]
    return working_state

@typechecked
def chacha20(k: key_t, counter: uint32_t, nonce: nonce_t) -> state_t:
    return chacha20_core(chacha20_init(k,counter,nonce))

@typechecked
def chacha20_block(k: key_t, counter:uint32_t, nonce: nonce_t) -> block_t:
    st = chacha20(k,counter,nonce)
    block = bytes.from_uint32s_le(st)
    # If block is not cast to block_t, the type isn't checked!
    return block_t(block)

@typechecked
def xor_block(block:subblock_t, keyblock:block_t) -> subblock_t:
    out = bytes.copy(block)
    for i in range(array.length(block)):
        out[i] ^= keyblock[i]
    return out

@typechecked
def chacha20_counter_mode(key: key_t, counter: uint32_t, nonce: nonce_t, msg:vlbytes_t) -> vlbytes_t:
    blocks, last = array.split_blocks(msg, blocksize)
    keyblock = array.create(blocksize, uint8(0))
    ctr = counter
    for i in range(array.length(blocks)):
        keyblock = chacha20_block(key, ctr, nonce)
        blocks[i] = xor_block(blocks[i], keyblock)
        ctr += uint32(1)
    keyblock = chacha20_block(key, ctr, nonce)
    last = xor_block(last, keyblock)
    return array.concat_blocks(blocks, last)

@typechecked
def chacha20_encrypt(key: key_t, counter: uint32_t, nonce: nonce_t, msg:vlbytes_t) -> vlbytes_t:
    return chacha20_counter_mode(key,counter,nonce,msg)

@typechecked
def chacha20_decrypt(key: key_t, counter: uint32_t, nonce: nonce_t, msg:vlbytes_t) -> vlbytes_t:
    return chacha20_counter_mode(key,counter,nonce,msg)
