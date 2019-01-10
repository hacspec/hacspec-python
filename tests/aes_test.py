from specs.aes import *
from sys import exit
import json

# mypy only checks functions that have types. So add an argument :)
def main(x: int) -> None:
    file = open('tests/test_vectors/aes128_test_vectors.json')
    aes128_test_vectors = json.load(file)
    for i in range(len(aes128_test_vectors)):
        msg = bytes.from_hex(aes128_test_vectors[i]['input'])
        k   = bytes.from_hex(aes128_test_vectors[i]['key'])
        n   = bytes.from_hex(aes128_test_vectors[i]['nonce'])
        ctr = int(aes128_test_vectors[i]['counter'],16)
        expected = bytes.from_hex(aes128_test_vectors[i]['output'])
        computed = aes128_encrypt_bytes(k,n,ctr,msg)
        if (computed == expected):
            print("Aes128 Test ",i," passed.")
        else:
            print("Aes128 Test ",i," failed:")
            print("expected ciphertext:",expected)
            print("computed ciphertext:",computed)
            exit(1)
    # rng = open("/dev/urandom","rb")
    # msgs = bytes.from_hex(rng.read(16 * 1024).hex())
    # key = bytes.from_hex(rng.read(16).hex())
    # nonce = bytes.from_hex(rng.read(12).hex())
    # ctr = uint32(1)
    # res = uint8(0)
    # for i in range(16):
    #     msg = msgs[i*1024:i*1024+1024]
    #     computed = aes128_encrypt(key,nonce,ctr,msg)
    #     res ^= computed[0]
    # print(res)


if __name__ == "__main__":
    main(0)
