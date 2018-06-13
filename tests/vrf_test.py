from specs.vrf import *
from sys import exit

def main (x: int) -> None :
    sk0 = bytes.from_hex('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60')
    pk0 = ECP2OS(point_mul(sk0, g_ed25519))
    msg0 = bytes.from_hex('')
    k = felem(nat(896921))
    proofComputed = ECVRF_prove(msg0, pk0, sk0, k)
    verified = ECVRF_verify (pk0, proofComputed, msg0)
    if verified:
        print('VRF Test verification succeeded')
    else:
        print('VRF Test verification failed')
        exit(1)

        
main(0)


