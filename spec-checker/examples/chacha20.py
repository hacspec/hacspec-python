#!/usr/bin/python3

# Run mypy chacha20.py to type check.

from speclib import *
from typing import List

state = List[uint32] # length : 32
index = int
shiftval = int
keyType = bytes # length: 32
nonceType = bytes # length: 12

def line(a: index, b: index, d: index, s: shiftval, m: state) -> state:
    r = m[:]
    r[a] = (r[a] + r[b])
    r[d] = (r[d] ^ r[a]).rotate_left(s)
    return r

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


constants = [uint32(0x61707865), uint32(0x3320646e),
             uint32(0x79622d32), uint32(0x6b206574)]

def chacha20(k: keyType, counter: uint32, nonce: nonceType) -> state:
    my_state = [
        constants[0],
        constants[1],
        constants[2],
        constants[3],
        uint32.from_bytes_le(k[0:4]),
        uint32.from_bytes_le(k[4:8]),
        uint32.from_bytes_le(k[8:12]),
        uint32.from_bytes_le(k[12:16]),
        uint32.from_bytes_le(k[16:20]),
        uint32.from_bytes_le(k[20:24]),
        uint32.from_bytes_le(k[24:28]),
        uint32.from_bytes_le(k[28:32]),
        counter,
        uint32.from_bytes_le(nonce[0:4]),
        uint32.from_bytes_le(nonce[4:8]),
        uint32.from_bytes_le(nonce[8:12]),
    ]
    working_state = my_state[:]
    for x in range(1,11):
        working_state = inner_block(working_state)
    for i in range(16):
        my_state[i] += working_state[i]
    return my_state

# mypy only checks functions that have types. So add an argument :)
def main(x: int):
    # Quarter round test vectors from RFC 7539
    a = uint32(0x11111111)
    b = uint32(0x01020304)
    c = uint32(0x9b8d6f43)
    d = uint32(0x01234567)
    my_state = [a, b, c, d]
    my_state = quarter_round(0, 1, 2, 3, my_state)
    exp_state = [uint32(0xea2a92f4), uint32(0xcb1cf8ce), uint32(0x4581472e), uint32(0x5881c4bb)]
    print("computed qround = ",my_state[0:4])
    print("expected qround = ",exp_state)
    assert(my_state == exp_state)

    # Test vector from RFX 7539 section 2.3.2
    key = bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f])
    nonce = bytes([0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x00, 0x4a, 0x00, 0x00, 0x00, 0x00])
    counter = uint32(1)
    result = chacha20(key, counter, nonce)
    expected_state = [
        uint32(0xe4e7f110), uint32(0x15593bd1), uint32(0x1fdd0f50), uint32(0xc47120a3),
        uint32(0xc7f4d1c7), uint32(0x0368c033), uint32(0x9aaa2204), uint32(0x4e6cd4c3),
        uint32(0x466482d2), uint32(0x09aa9f07), uint32(0x05d7c214), uint32(0xa2028bd9),
        uint32(0xd19c12b5), uint32(0xb94e16de), uint32(0xe883d0cb), uint32(0x4e3c50a2)
    ]
    print("expected state:",expected_state)
    print("computed state:",result)
    assert(result == expected_state)

if __name__ == "__main__":
    main(0)
