#!/usr/bin/python3

from hacspec.speclib import *
from sys import exit

# Tests for speclib


def test_bytes():
    x: bytes_t = bytes.from_ints([0x01, 0x02, 0x03, 0x04, 0x05])
    y: bytes_t = bytes.from_ints([0x01, 0x02, 0x03, 0x04, 0x05])
    if x != y:
        print("got      " + str(x))
        print("expected " + str(y))
        exit(1)
    print("test_bytes success!")

def test_2d_arrays():
    my_array_t = vlarray_t(bytes)
    x = my_array_t([])
    x = array.concat(x, bytes.from_ints([0x01, 0x02, 0x03]))
    x = array.concat(x, bytes.from_ints([0x04, 0x05]))
    y: vlarray_t(bytes_t) = vlarray([bytes.from_ints([0x01, 0x02, 0x03]), bytes.from_ints([0x04, 0x05])], bytes)
    z = my_array_t([])
    z = array.concat(z, bytes.from_ints([0x01, 0x02, 0x03]))
    z = array.concat(z, bytes.from_ints([0x04, 0x05]))
    if x != y:
        print("got      " + str(x))
        print("expected " + str(y))
        exit(1)
    if x != z:
        print("got      " + str(x))
        print("expected " + str(z))
        exit(1)
    print("test_2d_arrays success!")

def main(x: int) -> None:
    test_bytes()
    test_2d_arrays()


if __name__ == "__main__":
    main(0)
