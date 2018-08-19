#!/usr/bin/python3

from hacspec.speclib import *
from sys import exit

# Tests for speclib

def test_bytes_from_hex():
    b: bytes_t = bytes.from_hex("b8cdb147973dea2ec7")
    b2: bytes_t = array.copy(b)
    b3: bytes_t = bytes.from_ints([0xb8, 0xcd, 0xb1, 0x47, 0x97, 0x3d, 0xea, 0x2e, 0xc7])
    if b != b2 or b != b3:
        print("got      " + str(b2))
        print("expected " + str(b))
        print("expected " + str(3))
        exit(1)
    print("test_bytes_from_hex success!")

def test_concat():
    x: bytes_t = bytes.from_ints([0x01, 0x02, 0x03, 0x04, 0x05])
    y: bytes_t = bytes.from_ints([0x06, 0x07, 0x08, 0x09, 0x0A])
    e: bytes_t = bytes.from_ints([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A])
    z: bytes_t = array.concat(x, y)
    if z != e:
        print("got      " + str(z))
        print("expected " + str(e))
        exit(1)
    print("test_concat success!")

def test_bytes():
    x: bytes_t = bytes.from_ints([0x01, 0x02, 0x03, 0x04, 0x05])
    y: bytes_t = bytes.from_ints([0x01, 0x02, 0x03, 0x04, 0x05])
    if x != y:
        print("got      " + str(x))
        print("expected " + str(y))
        exit(1)
    print("test_bytes success!")

def test_2d_arrays():
    my_array_t = vlvector_t(bytes)
    x = my_array_t.create(2, bytes([]))
    x[0] = bytes.from_ints([0x01, 0x02, 0x03])
    x[1] = bytes.from_ints([0x04, 0x05])
    y = my_array_t([bytes.from_ints([0x01, 0x02, 0x03]), bytes.from_ints([0x04, 0x05])])
    z = my_array_t.create(2, bytes([]))
    z[0] = bytes.from_ints([0x01, 0x02, 0x03])
    z[1] = bytes.from_ints([0x04, 0x05])
    if x != y:
        print("got      " + str(x))
        print("expected " + str(y))
        exit(1)
    if x != z:
        print("got      " + str(x))
        print("expected " + str(z))
        exit(1)
    print("test_2d_arrays success!")

def main():
    test_bytes()
    test_2d_arrays()
    test_concat()
    test_bytes_from_hex()


if __name__ == "__main__":
    main()
