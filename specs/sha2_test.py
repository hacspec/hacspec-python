from speclib import *
from sha2 import sha256

# mypy only checks functions that have types. So add an argument :)


def main(x: int) -> None:
    msg = array([uint8(0x68), uint8(0x61), uint8(0x63), uint8(0x73),
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
                 uint8(0x69), uint8(0x6f), uint8(0x6e), uint8(0x2e)])
    digest = sha256(msg)
    computed = bytes.to_hex(digest)
    expected = "348ef044446d56e05210361af5a258588ad31765f446bf4cb3b67125a187a64a"
    if (expected == computed):
        print("Test successful!")
    else: 
        print("Test failed!")
        print("Computed: "+computed)
        print("Expected: "+expected)


if __name__ == "__main__":
    main(0)
