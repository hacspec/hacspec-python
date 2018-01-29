#!/usr/bin/python3

# Run mypy chacha20.py to type check.

from typing import List

state = List[int]
keyType = List[int] # length: 32
nonceType = List[int] # length: 12

def rotate(x: int, n: int) -> int:
    x &= 0xffffffff
    return ((x << n) | (x >> (32 - n))) & 0xffffffff

def line(a: int, b: int, d: int, s: int, m: state):
    m[a] = (m[a] + m[b]) % (2**32)
    m[d] = rotate(m[d] ^ m[a], s)

def quarter_round(a: int, b: int, c:int, d: int, m: state):
    line(a, b, d, 16, m)
    line(c, d, b, 12, m)
    line(a, b, d,  8, m)
    line(c, d, b,  7, m)

def inner_block(m: state):
    quarter_round(0, 4,  8, 12, m)
    quarter_round(1, 5,  9, 13, m)
    quarter_round(2, 6, 10, 14, m)
    quarter_round(3, 7, 11, 15, m)

    quarter_round(0, 5, 10, 15, m)
    quarter_round(1, 6, 11, 12, m)
    quarter_round(2, 7,  8, 13, m)
    quarter_round(3, 4,  9, 14, m)


def chacha20(k: keyType, counter: int, nonce: nonceType) -> state:
    my_state: state = [
        0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
        k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7],
        counter, nonce[0], nonce[1], nonce[2]
    ]
    working_state = my_state[:]
    for x in range(1,11):
        inner_block(working_state)
    for i in range(0, len(my_state)):
        my_state[i] = (my_state[i] + working_state[i]) % (2**32)
    return my_state

def main():
    # Quarter round test vectors from RFC 7539
    a: int = 0x11111111
    b: int = 0x01020304
    c: int = 0x9b8d6f43
    d: int = 0x01234567
    my_state: state = [a, b, c, d]
    quarter_round(0, 1, 2, 3, my_state)
    assert(my_state[0] == 0xea2a92f4)
    assert(my_state[1] == 0xcb1cf8ce)
    assert(my_state[2] == 0x4581472e)
    assert(my_state[3] == 0x5881c4bb)

    # Test vector from RFX 7539 section 2.3.2
    key: keyType = [0x03020100, 0x07060504, 0x0b0a0908, 0x0f0e0d0c,
                    0x13121110, 0x17161514, 0x1b1a1918, 0x1f1e1d1c]
    counter: int = 1
    nonce: nonceType = [0x09000000, 0x4a000000, 0x00000000]
    result = chacha20(key, counter, nonce)
    expected_state: state = [
        0xe4e7f110, 0x15593bd1, 0x1fdd0f50, 0xc47120a3,
        0xc7f4d1c7, 0x0368c033, 0x9aaa2204, 0x4e6cd4c3,
        0x466482d2, 0x09aa9f07, 0x05d7c214, 0xa2028bd9,
        0xd19c12b5, 0xb94e16de, 0xe883d0cb, 0x4e3c50a2
    ]
    assert(result == expected_state)

if __name__ == "__main__":
    main()
