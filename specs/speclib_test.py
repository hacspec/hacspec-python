#!/usr/bin/python3

from speclib import array, uint8, uint32

# Tests for speclib


def uint32_to_uint8_array_conversion():
    x = array([uint32(0x5a77d9f4), uint32(0xb90f5e16), uint32(0x3a41ed73)])
    expected = array([uint8(0x5a), uint8(0x77), uint8(0xd9), uint8(0xf4),
                      uint8(0xb9), uint8(0x0f), uint8(0x5e), uint8(0x16),
                      uint8(0x3a), uint8(0x41), uint8(0xed), uint8(0x73)])
    r = array.uint32s_to_uint8s_be(x)
    for (a, b) in zip(expected, r):
        assert(a == b)
    expected = array([uint8(0xf4), uint8(0xd9), uint8(0x77), uint8(0x5a),
                      uint8(0x16), uint8(0x5e), uint8(0x0f), uint8(0xb9),
                      uint8(0x73), uint8(0xed), uint8(0x41), uint8(0x3a)])
    r = array.uint32s_to_uint8s_le(x)
    for (a, b) in zip(expected, r):
        assert(a == b)

def main(x: int) -> None:
    uint32_to_uint8_array_conversion()


if __name__ == "__main__":
    main(0)
