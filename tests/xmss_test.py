#!/usr/bin/env python3

from specs.xmss import *
from lib.speclib import *
from tests.testlib import print_dot, exit

def test_xmss_self():
    adr = array.create_random(nat(8), uint32)
    seed = bytes.create_random_bytes(n)
    msg = bytes.from_ints([0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    msg_h = sha256(msg)

    xmss_sk : SK_t = key_gen_xmss()

def main():
    print_dot()
    test_xmss_self()
    exit(0)


if __name__ == "__main__":
    main()
