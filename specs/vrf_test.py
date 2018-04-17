from vrf import *
from sys import exit

def main (x: int) -> None :

    sk0 = bytes.from_hex('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60')
    pk0 = ECP2OS(point_mul(sk0, g_ed25519))
    msg0 = bytes.from_hex('')
    k = 896921
    proofExpected = bytes.from_hex('2a4e4e063418f8c40974bf0be612ba6116f1f2d0636f1686f4eac0f7d6c908e4e72529132eb0d7c921a04d9d78872621bdab94e2a6536f177a856ad63532695cd7eade45efa53310b0a98acdcfb18b')
    proofComputed = ECVRF_prove(msg0, pk0, sk0, k)
    verified = ECVRF_verify (pk0, proofComputed, msg0)
    if (proofExpected == proofComputed): 
        print('VRF Test Signature succeeded')
    else:
        print('VRF Test Signature failed') 
        print('expected: ' + str(proofExpected))
        print('computed: ' + str(proofComputed))
    if verified:
        print('VRF Test verification succeeded')
    else:
        print('VRF Test verification failed')
        exit(1)

        
main(0)


