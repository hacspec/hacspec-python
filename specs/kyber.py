#!/usr/bin/python3

# To run and check this file, you need Python 3 + mypy
# See install instructions at: http://mypy.readthedocs.io/en/latest/getting_started.html
# To typecheck this file: mypy kyber.py
# To run this file: python3 kyber.py

from speclib import *
from hashlib import *

zqelem = NewType('zqelem',int)
zqpoly    = NewType('zqpoly',array[zqelem])
zqpolyvec = NewType('zqpolyvec', array[zqpoly])


kyber_q   = 7681
kyber_n   =  256
kyber_dt  =   11
kyber_du  =   11
kyber_dv  =    3

kyber_k   =    3 # How do we want to handle different values?
kyber_eta =    4 # How do we want to handle different values?


omega     = zqelem(3844)
psi       = zqelem(62)
n_inv     = zqelem(7651)
psi_inv   = zqelem(1115)
omega_inv = zqelem(6584)


def zqadd(a:zqelem, b:zqelem) -> zqelem:
    return zqelem(a+b % kyber_q)

def zqsub(a:zqelem, b:zqelem) -> zqelem:
    return zqelem((a+kyber_q-b) % kyber_q)

def zqmul(a:zqelem, b:zqelem) -> zqelem:
    return zqelem(a*b % kyber_q)

def zqexp(a:zqelem, exp:int) -> zqelem:
    return zqelem(pow(a,exp,kyber_q))

def zqpoly_ntt(p:zqpoly) -> zqpoly:
    np = array.create(zqelem(0),256)
    for i in range(256):
        for j in range(256):
            np[i] = zqadd(np[i],zqmul(zqmul(zqexp(psi,j),p[j]),zqexp(omega,(i*j))))
    return np

def zqpoly_invntt(p:zqpoly) -> zqpoly:
    np = array.create(zqelem(0),256)
    for i in range(256):
        for j in range(256):
            np[i] = zqadd(np[i],zqmul(p[j],zqexp(omega_inv,(i*j))))
        np[i] = zqmul(np[i],zqmul(n_inv,zqexp(psi_inv,i)))
    return np

def zqpoly_pointwise(p:zqpoly, q:zqpoly) -> zqpoly:
    np = array.create(zqelem(0),256)
    for i in range(256):
        np[i] = zqmul(p[i],q[i])
    return np


def kyber_cpapke_keypair() -> (bytes, bytes):
    d = randombytes(32)
    rhosigma = bytes(hashlib.sha3_512(d))
    n = uint8(0)
    for i in range(256):
        for j in range(256):
            A[i][j] = genAij(rhosigma[0:32],i,j)
    
    for i in range(kyber_k):
        s[i] = cbd(prf(rhosigma[32:64],n))
        n += 1

    for i in range(kyber_k):
        e[i] = cbd(prf(rhosigma[32:64],n))
        n += 1

    shat = zqpolyvec_ntt(s)

    # init that with zero
    for i in range(kyber_k):
        for j in range(kyber_k):
            that[i] = zqpoly_add(that[i], zqpoly_pointwise(A[i][j],shat[j]))
    
    t = zqpolyvec_invntt(that)
    t = zqpolyvec_add(t, e)

    r1 = concat(zqpolyvec_encode(zqpolyvec_compress(t,dt),dt),rhosigma[0:32])
    r2 = zqpolyvec_encode(s,13)

    return (r1,r2)


def kyber_cpapke_encrypt(pk:bytes, m:bytes, coins:bytes) -> bytes:
    n = 0
    t = decompress(decode(pk[:-32],dt),dt)
    rho = pk[-32:]

    for i in range(256):
        for j in range(256):
            At[i][j] = genAij(rho,j,i)
 
    for i in range(kyber_k):
        r[i] = cbd(prf(coins,n))
        n += 1

    for i in range(kyber_k):
        e1[i] = cbd(prf(coins,n))
        n += 1

    e2 = cbd(prf(coins,n))

    rhat = zqpolyvec_ntt(r)
    
    for i in range(kyber_k):
        for j in range(kyber_k):
            uhat[i] = zqpoly_add(uhat[i], zqpoly_pointwise(At[i][j],rhat[j]))

    u = zqpolyvec_invntt(uhat)
    u = zqpolyvec_add(u, e1)

    vhat = array.create(zqelem(0), 256)
    for i in range(kyber_k):
        vhat = zqpoly_add(v, zqpoly_pointwise(that[i], rhat[i]))
    v = zqpoly_add(zqpoly_add(zqpoly_invntt(vhat), e2), topoly(m))

    c1 =  zqpolyvec_encode(zqpolyvec_compress(u,du),du)
    c2 =  zqpoly_encode(zqpoly_compress(v,dv),dv)

    return (c1,c2)


def kyber_cpapke_decrypt(sk:bytes, c:bytes) -> bytes:

    shat = zqpolyvec_decode(sk, 13)

    dhat = array.create(zqelem(0), 256)
    for i in range(kyber_k):
        dhat = zqpoly_add(dhat, zqpoly_pointwise(shat[i], uhat[i]))
    d = zqpoly_sub(v,zqpoly_invntt(dhat))

    return frombytes(d)


   


    
 

# just for debugging
def mul_schoolbook(p:zqpoly, q:zqpoly) -> zqpoly:
    t = array.create(zqelem(0),511)
    r = array.create(zqelem(0),256)
    for i in range(256):
        for j in range(256):
            t[i+j] = zqadd(t[i+j], zqmul(a[i],b[j]))
    for i in range(255):
        r[i] = zqsub(t[i],t[i+256])
    r[255] = t[255] % kyber_q
    return r
    
def mul_nttbased(p:zqpoly, q:zqpoly) -> zqpoly:
    return invntt(zqpoly_pointwise(ntt(p),ntt(q)))



a = array.create(zqelem(0),256)
for i in range(256):
    a[i] = zqelem(i)
    
b = array.create(zqelem(0),256)
for i in range(256):
    b[i] = zqelem(i+42)

r1 = mul_schoolbook(a,b)
r2 = mul_nttbased(a,b)

print(r1)
print(r2)
print(r1 == r2)

