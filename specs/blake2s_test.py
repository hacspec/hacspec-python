from blake2s import *

from test_vectors.blake2s_test_vectors import *
from sys import exit

def main(x:int) -> None:
    for i, vec in enumerate(blake2s_test_vectors):
        data = bytes.from_hex(vec['data'])
        key = bytes.from_hex(vec['key'])
        nn = out_size_t(vec['nn'])
        expected = bytes.from_hex(vec['output'])
        computed = blake2s(data,key,nn)
        if computed == expected:
            print("Blake2s Test {} passed.".format(i+1))
        else:
            print("Blake2s Test {} failed.".format(i+1))
            print("expected ciphertext:",bytes.to_hex(expected))
            print("computed ciphertext:",bytes.to_hex(computed))
            exit(1)


if __name__ == "__main__":
    main(0)
