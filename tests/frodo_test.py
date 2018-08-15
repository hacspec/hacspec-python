from lib.speclib import *
from specs.frodo import Frodo
import json
from tests.testlib import print_dot, exit

def main ():
    file = open('tests/test_vectors/frodo_test_vectors.json')
    frodo_test_vectors = json.load(file)
    print_dot()
    for i in range(len(frodo_test_vectors)):
        frodo_kem = frodo_test_vectors[i]['frodo_kem']
        gen_a = frodo_test_vectors[i]['gen_a']
        keypaircoins = bytes.from_hex(frodo_test_vectors[i]['keypaircoins'])
        enccoins = bytes.from_hex(frodo_test_vectors[i]['enccoins'])
        pk_expected = bytes.from_hex(frodo_test_vectors[i]['pk_expected'])
        ct_expected = bytes.from_hex(frodo_test_vectors[i]['ct_expected'])
        ss_expected = bytes.from_hex(frodo_test_vectors[i]['ss_expected'])

        (crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec) = Frodo(frodo_kem, gen_a)
        pk, sk = crypto_kem_keypair(keypaircoins)
        ct, ss1 = crypto_kem_enc(enccoins, pk)
        ss2 = crypto_kem_dec(ct, sk)
        
        if (ss1 == ss2 and ss1 == ss_expected and pk == pk_expected and ct == ct_expected):
            print("Frodo Test "+str(i)+" successful!")
        else:
            print("Frodo Test failed!")
            if (ss1 != ss_expected or ss1 != ss2):
                print("Computed shared secret 1: " + str(ss1))
                print("Computed shared secret 2: " + str(ss2))
                print("Expected shared secret: " + str(ss_expected))
            if (pk != pk_expected):
                print("Computed public key: " + str(pk))
                print("Expected public key: " + str(pk_expected))
            if (ct != ct_expected):
                print("Computed cipher text: " + str(ct))
                print("Expected cipher text: " + str(ct_expected))
            exit(1)
    exit(0)

main()
