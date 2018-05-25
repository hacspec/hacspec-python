from specs.ed25519 import *
import json
#from test_vectors.ed25519_test_vectors import ed25519_test_vectors
from sys import exit

def main (x: int) -> None :
    # RFC 7539 Test Vectors
    pk0 = bytes.from_hex('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')
    sk0 = bytes.from_hex('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60')
    msg0 = bytes.from_hex('')
    sig_expected = bytes.from_hex('e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b')
    sig_computed = sign(sk0,msg0)
    verified = verify(pk0,msg0,sig_computed)
    if (sig_expected == sig_computed):
        print('Ed25518 Test 0 signature succeeded')
    else:
        print('Ed25518 Test 0 signature failed')
        print('expected: '+str(sig_expected))
        print('computed: '+str(sig_computed))
    if (verified):
        print('Ed25518 Test 0 verification succeeded')
    else:
        print('Ed25518 Test 0 verification failed')
    verified = verify(pk0,msg0,sig_expected)
    if (verified):
        print('Ed25518 Test 0 verification_expected succeeded')
    else:
        print('Ed25518 Test 0 verification_expected failed')
        
main(0)


