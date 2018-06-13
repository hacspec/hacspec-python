from curve25519 import *
from speclib import *
from sha2 import sha256

a25519 = felem(486662)
b25519 = felem(1)
u25519 = felem(2)

def f_25519(x:felem_t) -> felem_t:
    return fadd(fmul(x,fsqr(x)),fadd(fmul(a25519,fsqr(x)),x))
        
def hash2curve25519(alpha:vlbytes) -> point_t :
    r = felem(bytes.to_nat_be(sha256(alpha)))
    d = felem(p25519 - fmul(a25519,finv(fadd(1,fmul(u25519,fsqr(r))))))
    e = fexp(f_25519(d),((p25519 - 1)//2))
    if e != 1:
        return fsub(d,a25519)
    else:
        return d
    
        
    
