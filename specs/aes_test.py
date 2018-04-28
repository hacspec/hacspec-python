from aes import *

from test_vectors.aes128_test_vectors import *
from sys import exit

# mypy only checks functions that have types. So add an argument :)
def main(x: int) -> None:
    for i in range(len(aes128_test_vectors)):
        msg = bytes.from_hex(aes128_test_vectors[i]['input'])
        k   = bytes.from_hex(aes128_test_vectors[i]['key'])
        n   = bytes.from_hex(aes128_test_vectors[i]['nonce'])
        ctr = aes128_test_vectors[i]['counter']
        expected = bytes.from_hex(aes128_test_vectors[i]['output'])
        computed = aes128_encrypt(k,n,uint32(ctr),msg)
        if (computed == expected):
            print("Aes128 Test ",i," passed.")
        else:
            print("Aes128 Test ",i," failed:")
            print("expected ciphertext:",expected)
            print("computed ciphertext:",computed)
            exit(1)


if __name__ == "__main__":
    main(0)
