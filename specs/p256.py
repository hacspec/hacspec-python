from speclib import *

prime = 2**256 - 2**224 + 2**192 + 2**96 - 1


felem = refine3(nat, lambda x: x < prime)
felem_t = felem

def to_felem(x:nat_t) -> felem_t:
    return felem(x % prime)

def fadd(x:felem_t,y:felem_t) -> felem_t:
    return to_felem(x + y)

def fsub(x:felem_t,y:felem_t) -> felem_t:
    return to_felem(x - y)

def fmul(x:felem_t,y:felem_t) -> felem_t:
    return to_felem(x * y)

def fsqr(x:felem_t) -> felem_t:
    return to_felem(x * x)    

def fexp(x:felem_t,n:nat_t) -> felem_t:
    return to_felem(pow(x,n,prime))

def finv(x:felem_t) -> felem_t:
    return to_felem(pow(x,prime-2,prime))

jacobian_t = tuple3(felem_t, felem_t, felem_t)
affine_t = tuple2(felem_t, felem_t)

scalar_t = bitvector_t(256)

serialized_point_t = bytes_t(33)
serialized_scalar_t = bytes_t(32)

def toAffine(p: jacobian_t) -> affine_t:
	(x, y, z) = p 
	z2 = fsqr(z)
	z2i = finv(z2)
	z3 = fmul(z, z2)
	z3i = finv(z3)
	x = fmul(x, z2i)
	y = fmul(y, z3i)
	return (x, y)

# def pointCompress(p: jacobian_t) -> serialized_point_t:
# 	(x, y, z) = p
# 	(x_a, y_a) = toAffine(p)
# 	r = 2**256 * (y_a % 2) + x_a
# 	return bytes.from_nat_le(nat(r))

# def recoverY(x: felem_t, sign: nat) -> jacobian_t:
# 	if x >= prime:
# 		return None
# 	a = prime -3
# 	b = 41058363725152142129326129780047268409114441015993725554835256314039467401291
	
# 	x3 = fmul(x, fsqr(x))
# 	ax = fmul(a, x)
# 	z = fadd(fadd(x3, ax), b)
# 	p = felem((prime+1)/4)
# 	z1 = felem(pow(z, p, prime))
# 	if sign:
# 		return (prime - z1)
# 	return z1
	
# def pointDecompress(s:serialized_point_t) -> jacobian_t:
#     x = bytes.to_nat_le(s)
#     sign = (x // (1 << 256)) % 2 == 1 
#     x = x % (1 << 256)
#     y = recoverY(x,sign)
#     if x is None:
#         return None
#     else:
#         return (x, y % prime, 1)


def pointDouble(p: jacobian_t) -> jacobian_t:
	(x1, y1, z1) = p
	delta = fsqr(z1)
	gamma = fsqr(y1)

	beta = fmul(x1, gamma)

	alpha_1 = fsub(x1, delta)
	alpha_2 = fadd(x1, delta)
	alpha = fmul(3, fmul(alpha_1, alpha_2))

	x3 = fsub(fsqr(alpha), fmul(8, beta))

	z3_ = fsqr(fadd(y1, z1))
	z3 = fsub(z3_, fadd(gamma, delta))

	y3_1 = fsub(fmul(4, beta), x3)
	y3_2 = fmul(8, fsqr(gamma))
	y3 = fsub(fmul(alpha, y3_1), y3_2)
	return (x3, y3, z3)

def isPointAtInfinity (p: jacobian_t) -> bool:
	(_, _, z) = p
	return (z==0)

def pointAdd (p: jacobian_t, q: jacobian_t) -> jacobian_t:
	if isPointAtInfinity(p):
		return q
	if isPointAtInfinity(q):
		return p	 
	(x1, y1, z1) = p
	(x2, y2, z2) = q
	z1z1 = fsqr(z1)
	z2z2 = fsqr(z2)
	u1 = fmul(x1, z2z2)
	u2 = fmul(x2, z1z1)
	s1 = fmul(fmul(y1, z2), z2z2)
	s2 = fmul(fmul(y2, z1), z1z1)
	if u1 == u2:
		if s1==s2:
			return pointDouble(p)
		else:
			return (0, 1, 0)
	h = fsub(u2, u1)
	i = fsqr(fmul(2, h))
	j = fmul(h, i)
	r = fmul(2, fsub(s2, s1))
	v = fmul(u1, i)

	x3_1 = fmul(2, v)
	x3_2 = fsub(fsqr(r), j)
	x3 = fsub(x3_2, x3_1)
	
	y3_1 = fmul(fmul(2, s1), j) 		
	y3_2 = fmul(r, fsub(v, x3))
	y3 = fsub(y3_2 , y3_1)

	z3_ = fsqr(fadd(z1, z2))
	z3 = fmul(fsub(z3_, fadd(z1z1, z2z2)), h)
	return (x3, y3, z3)

def montgomery_ladder(k:scalar_t, init: jacobian_t) -> jacobian_t:
    p0 : extended_point_t = (0, 1, 0)
    p1 : extended_point_t = init
    for i in range(256):
    	if k[255-i] == bit(1):
    		(p0, p1) = (p1, p0)	
    	xx = pointDouble(p0)
    	xp1 = pointAdd(p0, p1)
    	if k[255-i] == bit(1):
    		(p0, p1) = (xp1, xx)
    	else:
    		(p0, p1) = (xx, xp1)	
    return p0 	

basePoint =  (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296, 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5, 1) 
	
def point_mul(k: scalar_t) -> affine_t:
	k = bitvector(bytes.to_nat_le(k),256)
	return toAffine(montgomery_ladder(k, basePoint))
