from vrf import *
from sys import exit

def main (x: int) -> None :
    # RFC 7539 Test Vectors
    
    #pk0 = bytes.from_hex('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')
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




    # sig_expected = bytes.from_hex('e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b')
    # sig_computed = sign(sk0,msg0)
    # verified = verify(pk0,msg0,sig_computed)
    # if (sig_expected == sig_computed):
    #     print('Ed25518 Test 0 signature succeeded')
    # else:
    #     print('Ed25518 Test 0 signature failed')
    #     print('expected: '+str(sig_expected))
    #     print('computed: '+str(sig_computed))
    # if (verified):
    #     print('Ed25518 Test 0 verification succeeded')
    # else:
    #     print('Ed25518 Test 0 verification failed')
    # verified = verify(pk0,msg0,sig_expected)
    # if (verified):
    #     print('Ed25518 Test 0 verification_expected succeeded')
    # else:
    #     print('Ed25518 Test 0 verification_expected failed')
        
main(0)


