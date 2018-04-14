from speclib import *

prime = 2**256 - 2**224 + 2**192 + 2**96 - 1

if __name__ == '__main__':
	print(prime)

felem = refine3('felem_t', nat, lambda x: x < p25519)
felem_t = felem

def to_felem(x:nat_t) -> felem_t:
    return felem(x % p25519)

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

scalar_t = bitvector_t(256)

serialized_point_t = bytes_t(32)
serialized_scalar_t = bytes_t(32)

def point_double(p: jacobian_t) -> jacobian_t:
	(x1, y1, z1) = p
	delta = fsqr(z1)
	gama = fsqr(y1)
	beta = fmul(x1, gamma)
	alpha = fmul(3, fmul(fsub(x1, delta), fadd(x1, delta)))
	x3 = fsub(fsqr(alpha), fmul(8, beta))
	z3_ = fsqr(fadd(y1, z1))
	z3 = fsub(z3_, fsub(gamma, delta))
	y3_1 = fsub(fmul(4, beta), x3)
	y3_2 = fmul(8, fsqr(gamma))
	y3 = fsub(fmul(alpha, y3_1), y3_2)
	return jacobian_t(x3, y3, z3)

def point_add (p: jacobian_t, q: jacobian_t) -> jacobian_t:
	(x1, y1, z1) = p
	(x2, y2, z2) = q
	z1z1 = z1**2
	z2z2 = z2**2
	u1 = fmul(x1, z2z2)
	u2 = fmul(x2, z1z1)
	s1 = fmul(fmul(y1, z2), z2z2)
	s2 = fmul(fmul(y2, z1), z1z1)
	if u1 == u2:
		if s1==s2:
			point_double(p)
		else:
			jacobian_t(1, 1, 0)
	h = fsub(u2, u1)
	i = fsqr(fmul(2, h))
	j = fmul(h, i)
	r = fmul(2, fsub(s2, s1))
	v = fmul(u1, i)
	x3_ = fmul(2, v)
	x3 = fsub(fsub(fsqr(r), j), x3_)
	y3_ = fmul(fmul(2, s1), j) 		
	y3__ = fmul(r, fsub(v, x3))
	y3 = fsub(y3__ , y3_)
	z3_ = fsqr(fadd(z1, z2))
	z3 = fmul(fsub(z3_, fsub(z1z1, z2z2)), h)
	return jacobian_t(x3, y3, z3)