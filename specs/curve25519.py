#!/usr/bin/python3

from speclib import *

# Define prime field

p25519 = (2 ** 255) - 19
felem_t = refine(nat,lambda x: x < p25519)
def felem(x:nat) -> felem_t:
    return (x % p25519)
def fadd(x:felem_t,y:felem_t) -> felem_t:
    return felem(x + y)
def fsub(x:felem_t,y:felem_t) -> felem_t:
    return felem(x - y)
def fmul(x:felem_t,y:felem_t) -> felem_t:
    return felem(x * y)
def fsqr(x:felem_t) -> felem_t:
    return felem(x * x)
def fexp(x:felem_t,n:nat) -> felem_t:
    return felem(pow(x,nat,p25519))
def finv(x:felem_t) -> felem_t:
    return felem(pow(x,p25519-2,p25519))


felem_len = 16
point_t = tuple2(felem_t, felem_t)   #projective coordinates
scalar_t = bitvector_t(256)

serialized_point_t = bytes_t(32)
serialized_scalar_t = bytes_t(32)

def decodeScalar(s:serialized_scalar_t) -> scalar_t:
    k = vlbytes.copy(s)
    k[0]  &= uint8(248)
    k[31] &= uint8(127)
    k[31] |= uint8(64)
    return bitvector(bytes.to_nat_le(k),256)

def decodePoint(u:serialized_point_t) -> point_t :
    b = bytes.to_nat_le(u)
    return ((b & ((1 << 255) - 1)) % p25519,1)

def encodePoint(p:point_t) -> serialized_point_t :
    b = fmul(p[0],finv(p[1]))
    return bytes.from_nat_le(b)

def add_and_double(q:point_t,nq:point_t,nqp1:point_t) -> tuple2(point_t,point_t):
  (x_1, _) = q
  (x_2, z_2) = nq
  (x_3, z_3) = nqp1
  a  = fadd(x_2 ,z_2)
  aa = fsqr(a)
  b  = fsub(x_2,z_2)
  bb = fsqr(b)
  e  = fsub(aa, bb)
  c  = fadd(x_3,z_3)
  d  = fsub(x_3,z_3)
  da = fmul(d,a)
  cb = fmul(c,b)
  x_3 = fsqr(fadd(da,cb))
  z_3 = fmul(x_1,(fsqr(fsub(da,cb))))
  x_2 = fmul(aa,bb)
  z_2 = fmul(e,fadd(aa,fmul(felem(121665),e)))
  return ((x_2, z_2), (x_3, z_3))

def montgomery_ladder(k:scalar_t,init:point_t) -> point_t :
    p0 : point_t = (1,0)
    p1 : point_t = init
    for i in range(256):
        if k[255-i] == bit(1):
            (p1,p0) = add_and_double(init,p1,p0)
        else:
            (p0,p1) = add_and_double(init,p0,p1)
    return(p0)

def scalarmult(s:serialized_scalar_t,p:serialized_point_t) -> serialized_point_t:
    s_ = decodeScalar(s)
    p_ = decodePoint(p)
    r = montgomery_ladder(s_,p_)
    return encodePoint(r)

