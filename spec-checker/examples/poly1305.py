# To run and check this file, you need Python 3 + mypy
# See install instructions at: http://mypy.readthedocs.io/en/latest/getting_started.html
# To typecheck this file: mypy poly1305.py
# To run this file: python3 poly1305.py

p130m5 = (2 ** 130) - 5 #type: int
blocksize = 16

def fadd(a:int,b:int) -> int:
    return (a + b) % p130m5

def fmul(a:int,b:int) -> int:
    return (a * b) % p130m5

def encode(len:int, word:bytes) -> int:
    welem = int.from_bytes(word, byteorder='little')
    lelem = 2 ** (8 * len)
    return fadd(lelem,welem)

def encode_r(r:bytes) -> int:
    relem = int.from_bytes(r, byteorder='little')
    clamp = 0x0ffffffc0ffffffc0ffffffc0fffffff
    return  relem & clamp

def poly(len:int,text:bytes,r:int) -> int:
    acc = 0
    nblocks = len // blocksize
    last = len % blocksize
    for i in range(nblocks):
        block = text[i*blocksize : i*blocksize + blocksize]
        acc = fmul(fadd(acc,encode(blocksize,block)),r)
    if last > 0:
        block = text[len-last:len]
        acc = fmul(fadd(acc,encode(last,block)),r)
    return acc


def poly1305_mac(len:int,text:bytes,k:bytes) -> bytes :
    r = k[0:blocksize]
    s = k[blocksize:2*blocksize]
    relem = encode_r(r)
    selem = int.from_bytes(s, byteorder='little')
    a = poly(len,text,relem)
    n = (a + selem) & 0xffffffffffffffffffffffffffffffff
    return n.to_bytes(blocksize,byteorder='little')


def main () :
    # RFC 7539 Test Vectors
    msg = bytes([
        0x43, 0x72, 0x79, 0x70, 0x74, 0x6f, 0x67, 0x72,
        0x61, 0x70, 0x68, 0x69, 0x63, 0x20, 0x46, 0x6f,
        0x72, 0x75, 0x6d, 0x20, 0x52, 0x65, 0x73, 0x65,
        0x61, 0x72, 0x63, 0x68, 0x20, 0x47, 0x72, 0x6f,
        0x75, 0x70])
    k = bytes([
        0x85, 0xd6, 0xbe, 0x78, 0x57, 0x55, 0x6d, 0x33,
        0x7f, 0x44, 0x52, 0xfe, 0x42, 0xd5, 0x06, 0xa8,
        0x01, 0x03, 0x80, 0x8a, 0xfb, 0x0d, 0xb2, 0xfd,
        0x4a, 0xbf, 0xf6, 0xaf, 0x41, 0x49, 0xf5, 0x1b])
    expected = bytes([
        0xa8, 0x06, 0x1d, 0xc1, 0x30, 0x51, 0x36, 0xc6,
        0xc2, 0x2b, 0x8b, 0xaf, 0x0c, 0x01, 0x27, 0xa9 ])
    print("expected mac:",expected)
    print("computed mac:",poly1305_mac(34,msg,k))
        
main()
