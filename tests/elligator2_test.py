from elligator2 import *
import json
#from test_vectors.elligator2_test_vectors import elligator2_test_vectors
from sys import exit

def main (x: int) -> None :
    alpha0 = bytes.from_nat_be(1)
    x0 = bytes.from_nat_be(38597363079105398474523661669562635951089994888546854679819194669304376384412)
    y0 = bytes.from_nat_be(26903495929791911980624662688598047587608282445491562122320889756226532494818)
    (cx0,xy0) = hash2curve25519(alpha0)

    print(x0)
    print(y0)
    print(cx0)
    print(cy0)

    
    # if (cx0 == expected == computed):
    #     print("Curve25519 Test 0 passed.")
    # else:
    #     print("Curve25519  0 failed:")
    #     print("expected:",expected)
    #     print("computed:",computed)

    # for i in range(len(curve25519_test_vectors)):
    #     s = bytes.from_hex(curve25519_test_vectors[i]['private'])
    #     p = bytes.from_hex(curve25519_test_vectors[i]['public'])
    #     expected = bytes.from_hex(curve25519_test_vectors[i]['result'])
    #     valid = curve25519_test_vectors[i]['valid']
    #     computed = scalarmult(s,p)
    #     if (computed == expected and valid):
    #         print("Curve25519 Test ",i+1," passed.")
    #     elif (not(computed == expected) and not valid):
    #         print("Curve25519 Test ",i+1," passed.")
    #     else:
    #         print("Curve25519 Test ",i+1," failed:")
    #         print("expected mac:",expected)
    #         print("computed mac:",computed)
    #         exit(1)

main(0)
