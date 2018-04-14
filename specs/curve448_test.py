from curve448 import *
import json
from test_vectors.curve448_test_vectors import curve448_test_vectors
from sys import exit

def main (x: int) -> None :
    for i in range(len(curve448_test_vectors)):
        s = bytes.from_hex(curve448_test_vectors[i]['private'])
        p = bytes.from_hex(curve448_test_vectors[i]['public'])
        expected = bytes.from_hex(curve448_test_vectors[i]['result'])
        valid = curve448_test_vectors[i]['valid']
        computed = scalarmult(s, p)
        if (computed == expected and valid):
            print("Curve448 Test ", i, " passed.")
        elif (not(computed == expected) and not valid):
            print("Curve448 Test ", i, " passed.")
        else:
            print("Curve448 Test ", i, " failed:")
            print("expected: ", expected)
            print("computed: ", computed)
            exit(1)

main(0)
