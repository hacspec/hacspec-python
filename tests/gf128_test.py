from specs.gf128 import *
from sys import exit
import json

def main(x: int) -> None:
    file = open('tests/test_vectors/gf128_test_vectors.json')
    gf128_test_vectors = json.load(file)
    for i in range(len(gf128_test_vectors)):
        msg = bytes.from_hex(gf128_test_vectors[i]['input'])
        k   = bytes.from_hex(gf128_test_vectors[i]['key'])
        expected = bytes.from_hex(gf128_test_vectors[i]['output'])
        computed = gmac(msg,k)
        if (computed == expected):
            print("GF128 Test ",i," passed.")
        else:
            print("GF128 Test ",i," failed:")
            print("expected mac:",expected)
            print("computed mac:",computed)
            exit(1)


if __name__ == "__main__":
    main(0)

