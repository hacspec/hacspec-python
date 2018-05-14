from hacspec.speclib import *
from keccak import shake128, shake256, sha3_224, sha3_256, sha3_384, sha3_512
from test_vectors.keccak_test_vectors import sha3_test_vectors, shake128_test_vectors, shake256_test_vectors
from sys import exit
import json

def sha3_test():
    for i in range(len(sha3_test_vectors)):
        msg = bytes.from_hex(sha3_test_vectors[i]['msg'])
        expected224 = sha3_test_vectors[i]['expected224']
        expected256 = sha3_test_vectors[i]['expected256']
        expected384 = sha3_test_vectors[i]['expected384']
        expected512 = sha3_test_vectors[i]['expected512']

        d224 = bytes.to_hex(sha3_224(array.length(msg), msg))
        d256 = bytes.to_hex(sha3_256(array.length(msg), msg))
        d384 = bytes.to_hex(sha3_384(array.length(msg), msg))
        d512 = bytes.to_hex(sha3_512(array.length(msg), msg))

        if (expected224 == d224 and expected256 == d256 and expected384 == d384 and expected512 == d512):
            print("SHA-3 (224/256/384/512) Test " + str(i) + " successful!")
        else:
            print("SHA3 Test failed!")
            print("Computed: "+d224)
            print("Expected: "+expected224)
            print("Computed: "+d256)
            print("Expected: "+expected256)
            print("Computed: "+d384)
            print("Expected: "+expected384)
            print("Computed: "+d512)
            print("Expected: "+expected512)
            exit(1)

def shake128_test():
    for i in range(len(shake128_test_vectors)):
        msg = bytes.from_hex(shake128_test_vectors[i]['msg'])
        output = shake128_test_vectors[i]['output']

        res = bytes.to_hex(shake128(array.length(msg), msg, 16))

        if (output == res):
            print("SHAKE128 Test " + str(i) + " successful!")
        else:
            print("SHAKE128 Test failed!")
            print("Computed: "+res)
            print("Expected: "+output)
            exit(1)

def shake256_test():
    for i in range(len(shake256_test_vectors)):
        msg = bytes.from_hex(shake256_test_vectors[i]['msg'])
        output = shake256_test_vectors[i]['output']

        res = bytes.to_hex(shake256(array.length(msg), msg, 32))

        if (output == res):
            print("SHAKE256 Test " + str(i) + " successful!")
        else:
            print("SHAKE256 Test failed!")
            print("Computed: "+res)
            print("Expected: "+output)
            exit(1)

def main (x: int) -> None :
    sha3_test()
    shake128_test()
    shake256_test()

main(0)
