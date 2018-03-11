#!/usr/bin/env python3

from speclib import *
from sha2 import sha256

# mypy only checks functions that have types. So add an argument :)


def main(x: int) -> None:
    digest = sha256(array([uint8(0x68), uint8(0x61), uint8(0x63), uint8(0x73),
                           uint8(0x70), uint8(0x65), uint8(0x63), uint8(0x20),
                           uint8(0x69), uint8(0x73), uint8(0x20), uint8(0x61),
                           uint8(0x20), uint8(0x70), uint8(0x72), uint8(0x6f),
                           uint8(0x70), uint8(0x6f), uint8(0x73), uint8(0x61),
                           uint8(0x6c), uint8(0x20), uint8(0x66), uint8(0x6f),
                           uint8(0x72), uint8(0x20), uint8(0x61), uint8(0x20),
                           uint8(0x6e), uint8(0x65), uint8(0x77), uint8(0x20),
                           uint8(0x73), uint8(0x70), uint8(0x65), uint8(0x63),
                           uint8(0x69), uint8(0x66), uint8(0x69), uint8(0x63),
                           uint8(0x61), uint8(0x74), uint8(0x69), uint8(0x6f),
                           uint8(0x6e), uint8(0x20), uint8(0x6c), uint8(0x61),
                           uint8(0x6e), uint8(0x67), uint8(0x75), uint8(0x61),
                           uint8(0x67), uint8(0x65), uint8(0x20), uint8(0x66),
                           uint8(0x6f), uint8(0x72), uint8(0x20), uint8(0x63),
                           uint8(0x72), uint8(0x79), uint8(0x70), uint8(0x74),
                           uint8(0x6f), uint8(0x20), uint8(0x70), uint8(0x72),
                           uint8(0x69), uint8(0x6d), uint8(0x69), uint8(0x74),
                           uint8(0x69), uint8(0x76), uint8(0x65), uint8(0x73),
                           uint8(0x20), uint8(0x74), uint8(0x68), uint8(0x61),
                           uint8(0x74), uint8(0x20), uint8(0x69), uint8(0x73),
                           uint8(0x20), uint8(0x73), uint8(0x75), uint8(0x63),
                           uint8(0x63), uint8(0x69), uint8(0x6e), uint8(0x63),
                           uint8(0x74), uint8(0x2c), uint8(0x20), uint8(0x74),
                           uint8(0x68), uint8(0x61), uint8(0x74), uint8(0x20),
                           uint8(0x69), uint8(0x73), uint8(0x20), uint8(0x65),
                           uint8(0x61), uint8(0x73), uint8(0x79), uint8(0x20),
                           uint8(0x74), uint8(0x6f), uint8(0x20), uint8(0x72),
                           uint8(0x65), uint8(0x61), uint8(0x64), uint8(0x20),
                           uint8(0x61), uint8(0x6e), uint8(0x64), uint8(0x20),
                           uint8(0x69), uint8(0x6d), uint8(0x70), uint8(0x6c),
                           uint8(0x65), uint8(0x6d), uint8(0x65), uint8(0x6e),
                           uint8(0x74), uint8(0x2c), uint8(0x20), uint8(0x61),
                           uint8(0x6e), uint8(0x64), uint8(0x20), uint8(0x74),
                           uint8(0x68), uint8(0x61), uint8(0x74), uint8(0x20),
                           uint8(0x6c), uint8(0x65), uint8(0x6e), uint8(0x64),
                           uint8(0x73), uint8(0x20), uint8(0x69), uint8(0x74),
                           uint8(0x73), uint8(0x65), uint8(0x6c), uint8(0x66),
                           uint8(0x20), uint8(0x74), uint8(0x6f), uint8(0x20),
                           uint8(0x66), uint8(0x6f), uint8(0x72), uint8(0x6d),
                           uint8(0x61), uint8(0x6c), uint8(0x20), uint8(0x76),
                           uint8(0x65), uint8(0x72), uint8(0x69), uint8(0x66),
                           uint8(0x69), uint8(0x63), uint8(0x61), uint8(0x74),
                           uint8(0x69), uint8(0x6f), uint8(0x6e), uint8(0x2e)]))
    digest_int = array.to_int(digest)
    expected_digest = 0x348ef044446d56e05210361af5a258588ad31765f446bf4cb3b67125a187a64a
    assert(expected_digest == digest_int)
    print(hex(digest_int))


if __name__ == "__main__":
    main(0)
