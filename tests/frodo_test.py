from lib.speclib import *
from specs.frodo import crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec
from sys import exit

def test(keypaircoins, enccoins, ss_expected, num):
    pk, sk = crypto_kem_keypair(keypaircoins)
    ct, ss1 = crypto_kem_enc(enccoins, pk)
    ss2 = crypto_kem_dec(ct, sk)

    if (ss1 == ss2 and ss1 == ss_expected):
        print("Frodo Test "+str(num)+" successful!")
    else:
        print("Frodo Test failed!")
        print("Computed shared secret 1: " + str(ss1))
        print("Computed shared secret 2: " + str(ss2))
        print("Expected shared secret: " + str(ss_expected))
        exit(1)

def main(x: int) -> None:
    keypaircoins = bytes.from_hex('4b622de1350119c45a9f2e2ef3dc5df50a759d138cdfbd64c81cc7cc2f513345d5a45a4ced06403c5557e87113cb30ea')
    enccoins = bytes.from_hex('08e25538484cd7f1613248fe6c9f6b4e')
    ss_expected = bytes.from_hex('DAA9B22C55AF73A3EAA06D081E1A5606')
    test(keypaircoins, enccoins, ss_expected, 0)

if __name__ == "__main__":
    main(0)
