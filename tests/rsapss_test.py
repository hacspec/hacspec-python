from lib.speclib import *
from specs.rsapss import rsapss_sign, rsapss_verify, os2ip
from sys import exit
from tests.testlib import print_dot, exit
import json

def main (x: int) -> None :
    file = open('tests/test_vectors/rsapss_test_vectors.json')
    rsapss_test_vectors = json.load(file)
    print_dot()
    for i in range(len(rsapss_test_vectors)):
        modBits = nat(rsapss_test_vectors[i]['modBits'])
        nBytes = bytes.from_hex(rsapss_test_vectors[i]['n'])
        eBytes = bytes.from_hex(rsapss_test_vectors[i]['e'])
        dBytes = bytes.from_hex(rsapss_test_vectors[i]['d'])
        salt = bytes.from_hex(rsapss_test_vectors[i]['salt'])
        msg = bytes.from_hex(rsapss_test_vectors[i]['msg'])
        sgnt_expected = bytes.from_hex(rsapss_test_vectors[i]['sgnt'])
        valid = rsapss_test_vectors[i]['valid']

        pkey = (os2ip(nBytes), os2ip(eBytes))
        skey = (pkey, os2ip(dBytes))

        sLen = nat(array.length(salt))
        sgnt_computed = rsapss_sign(modBits, skey, salt, msg)
        vrfy = rsapss_verify(modBits, pkey, sLen, msg, sgnt_computed)

        if (sgnt_computed == sgnt_expected and valid and vrfy):
            print("RSA-PSS Test ", i, " passed.")
        elif (not(sgnt_computed == sgnt_expected) and not valid and not vrfy):
            print("RSA-PSS Test ", i, " passed.")
        else:
            print("RSA-PSS Test ", i, " failed:")
            print("expected: ", sgnt_expected)
            print("computed: ", sgnt_computed)
            exit(1)
    exit(0)

main(0)
