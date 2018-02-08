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
    assert(len(working_state) == 16)
    return working_state

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


from test_vectors.chacha20_test_vectors import *

# mypy only checks functions that have types. So add an argument :)
def main(x: int) -> None:
    # Quarter round test vectors from RFC 7539
    a = uint32(0x11111111)
    b = uint32(0x01020304)
    c = uint32(0x9b8d6f43)
    d = uint32(0x01234567)
    my_state = array([a, b, c, d])
    my_state = quarter_round(0, 1, 2, 3, my_state)
    exp_state = array([uint32(0xea2a92f4), uint32(0xcb1cf8ce), uint32(0x4581472e), uint32(0x5881c4bb)])
    print("computed qround = ",str(my_state[0:4]))
    print("expected qround = ",str(exp_state))
    assert(my_state == exp_state)

    # Test vector from RFX 7539 section 2.3.2
    key = bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f])
    nonce = bytes([0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x00, 0x4a, 0x00, 0x00, 0x00, 0x00])
    counter = uint32(1)
    result = chacha20(key, counter, nonce)
    expected_state = array([
        uint32(0xe4e7f110), uint32(0x15593bd1), uint32(0x1fdd0f50), uint32(0xc47120a3),
        uint32(0xc7f4d1c7), uint32(0x0368c033), uint32(0x9aaa2204), uint32(0x4e6cd4c3),
        uint32(0x466482d2), uint32(0x09aa9f07), uint32(0x05d7c214), uint32(0xa2028bd9),
        uint32(0xd19c12b5), uint32(0xb94e16de), uint32(0xe883d0cb), uint32(0x4e3c50a2)
    ])
    print("expected state:",expected_state)
    print("computed state:",result)
    assert(result == expected_state)

    plaintext = bytes([0x4c, 0x61, 0x64, 0x69, 0x65, 0x73, 0x20, 0x61,
                       0x6e, 0x64, 0x20, 0x47, 0x65, 0x6e, 0x74, 0x6c,
                       0x65, 0x6d, 0x65, 0x6e, 0x20, 0x6f, 0x66, 0x20,
                       0x74, 0x68, 0x65, 0x20, 0x63, 0x6c, 0x61, 0x73,
                       0x73, 0x20, 0x6f, 0x66, 0x20, 0x27, 0x39, 0x39,
                       0x3a, 0x20, 0x49, 0x66, 0x20, 0x49, 0x20, 0x63,
                       0x6f, 0x75, 0x6c, 0x64, 0x20, 0x6f, 0x66, 0x66,
                       0x65, 0x72, 0x20, 0x79, 0x6f, 0x75, 0x20, 0x6f,
                       0x6e, 0x6c, 0x79, 0x20, 0x6f, 0x6e, 0x65, 0x20,
                       0x74, 0x69, 0x70, 0x20, 0x66, 0x6f, 0x72, 0x20,
                       0x74, 0x68, 0x65, 0x20, 0x66, 0x75, 0x74, 0x75,
                       0x72, 0x65, 0x2c, 0x20, 0x73, 0x75, 0x6e, 0x73,
                       0x63, 0x72, 0x65, 0x65, 0x6e, 0x20, 0x77, 0x6f,
                       0x75, 0x6c, 0x64, 0x20, 0x62, 0x65, 0x20, 0x69,
                       0x74, 0x2e])
    key = bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11,
                 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a,
                 0x1b, 0x1c, 0x1d, 0x1e, 0x1f])
    nonce = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4a,
                   0x00, 0x00, 0x00, 0x00])
    expected = bytes([0x6e, 0x2e, 0x35, 0x9a, 0x25, 0x68, 0xf9, 0x80,
                      0x41, 0xba, 0x07, 0x28, 0xdd, 0x0d, 0x69, 0x81,
                      0xe9, 0x7e, 0x7a, 0xec, 0x1d, 0x43, 0x60, 0xc2,
                      0x0a, 0x27, 0xaf, 0xcc, 0xfd, 0x9f, 0xae, 0x0b,
                      0xf9, 0x1b, 0x65, 0xc5, 0x52, 0x47, 0x33, 0xab,
                      0x8f, 0x59, 0x3d, 0xab, 0xcd, 0x62, 0xb3, 0x57,
                      0x16, 0x39, 0xd6, 0x24, 0xe6, 0x51, 0x52, 0xab,
                      0x8f, 0x53, 0x0c, 0x35, 0x9f, 0x08, 0x61, 0xd8,
                      0x07, 0xca, 0x0d, 0xbf, 0x50, 0x0d, 0x6a, 0x61,
                      0x56, 0xa3, 0x8e, 0x08, 0x8a, 0x22, 0xb6, 0x5e,
                      0x52, 0xbc, 0x51, 0x4d, 0x16, 0xcc, 0xf8, 0x06,
                      0x81, 0x8c, 0xe9, 0x1a, 0xb7, 0x79, 0x37, 0x36,
                      0x5a, 0xf9, 0x0b, 0xbf, 0x74, 0xa3, 0x5b, 0xe6,
                      0xb4, 0x0b, 0x8e, 0xed, 0xf2, 0x78, 0x5e, 0x42,
                      0x87, 0x4d])
    computed = chacha20_encrypt(key,1,nonce,plaintext)
    if (computed == expected):
        print("Test  0 passed.")
    else:
        print("Test  0 failed:")
        print("expected ciphertext:",expected)
        print("computed ciphertext:",computed)
    for i in range(len(chacha20_test_vectors)):
        msg = bytes.fromhex(chacha20_test_vectors[i]['input'])
        k   = bytes.fromhex(chacha20_test_vectors[i]['key'])
        n   = bytes.fromhex(chacha20_test_vectors[i]['nonce'])
        ctr = chacha20_test_vectors[i]['counter']
        expected = bytes.fromhex(chacha20_test_vectors[i]['output'])
        computed = chacha20_encrypt(key,ctr,n,msg)
        if (computed == expected):
            print("Test ",i+1," passed.")
        else:
            print("Test ",i+1," failed:")
            print("expected ciphertext:",expected)
            print("computed ciphertext:",computed)


if __name__ == "__main__":
    main(0)
