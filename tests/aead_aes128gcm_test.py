from specs.aead_aes128gcm import *

from test_vectors.aead_aes128gcm_test_vectors import *
from sys import exit

def main(x: int) -> None :
    for i in range(len(aead_aes128gcm_test_vectors)):
        msg = bytes.from_hex(aead_aes128gcm_test_vectors[i]['input'])
        k   = bytes.from_hex(aead_aes128gcm_test_vectors[i]['key'])
        n =   bytes.from_hex(aead_aes128gcm_test_vectors[i]['nonce'])
        aad  = bytes.from_hex(aead_aes128gcm_test_vectors[i]['aad'])
        exp_cipher = bytes.from_hex(aead_aes128gcm_test_vectors[i]['output'])
        exp_mac = bytes.from_hex(aead_aes128gcm_test_vectors[i]['tag'])
        cipher, mac = aead_aes128gcm_encrypt(k,n,aad,msg)
        decrypted_msg = aead_aes128gcm_decrypt(k,n,aad,cipher,mac)
        if (exp_cipher == cipher and exp_mac == mac and decrypted_msg == msg):
            print("AEAD-AES128-GCM Test ",i+1," passed.")
        else:
            print("AEAD-AES128-GCM Test ",i+1," failed:")
            print("expected cipher: ", exp_cipher)
            print("computed cipher: ", cipher)
            print("expected mac: ", exp_mac)
            print("computed mac: ", mac)
            exit(1)

if __name__ == "__main__":
    main(0)
