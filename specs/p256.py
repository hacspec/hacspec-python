from lib.speclib import *

prime : int = 2**256 - 2**224 + 2**192 + 2**96 - 1
felem_t = natmod_t(prime)
@typechecked
def to_felem(x: nat_t) -> felem_t:
    return natmod(x, prime)


@typechecked
def finv(x: felem_t) -> felem_t:
    return x ** (prime - 2)


jacobian_t = tuple_t(felem_t, felem_t, felem_t)
affine_t = tuple_t(felem_t, felem_t)


@typechecked
def jacobian(a: int, b: int, c: int) -> jacobian_t:
    return to_felem(nat(a)), to_felem(nat(b)), to_felem(nat(c))


scalar_t = uintn_t(256)

@typechecked
def to_scalar(n:int) -> scalar_t:
    return uintn(n, 256)
    

@typechecked
def toAffine(p: jacobian_t) -> affine_t:
    x : felem_t
    y : felem_t
    z : felem_t
    (x, y, z) = p
    z2 : felem_t = z ** 2
    z2i : felem_t = finv(z2)
    z3 : felem_t = z * z2
    z3i : felem_t = finv(z3)
    x = x * z2i
    y = y * z3i
    return x, y


@typechecked
def pointDouble(p: jacobian_t) -> jacobian_t:
    x1 : felem_t
    y1 : felem_t
    z1 : felem_t
    (x1, y1, z1) = p
    delta : felem_t = z1 ** 2
    gamma : felem_t = y1 ** 2

    beta : felem_t = x1 * gamma

    alpha_1 : felem_t = x1 - delta
    alpha_2 : felem_t = x1 + delta
    alpha : felem_t = to_felem(3) * (alpha_1 * alpha_2)

    x3 : felem_t = (alpha ** 2) - (to_felem(8) * beta)

    z3_ : felem_t = (y1 + z1) ** 2
    z3 : felem_t = z3_ - (gamma + delta)

    y3_1 : felem_t = (to_felem(4) * beta) - x3
    y3_2 : felem_t = to_felem(8) * (gamma ** 2)
    y3 : felem_t = (alpha * y3_1) - y3_2
    return x3, y3, z3


@typechecked
def isPointAtInfinity(p: jacobian_t) -> bool:
    z : felem_t
    x_ : felem_t
    y_ : felem_t
    (x_, y_, z) = p
    return (z == to_felem(0))



@typechecked
def pointAddFinite(p: jacobian_t, q: jacobian_t) -> jacobian_t:
    x1 : felem_t
    y1 : felem_t
    z1 : felem_t
    x2 : felem_t
    y2 : felem_t
    z2 : felem_t
    (x1, y1, z1) = p
    (x2, y2, z2) = q
    z1z1 : felem_t = z1 ** 2
    z2z2 : felem_t = z2 ** 2
    u1 : felem_t = x1 * z2z2
    u2 : felem_t = x2 * z1z1
    s1 : felem_t = (y1 * z2) * z2z2
    s2 : felem_t = (y2 * z1) * z1z1
    h : felem_t = u2 - u1
    i : felem_t = (to_felem(2) * h) ** 2
    j : felem_t = h * i
    r : felem_t = to_felem(2) * (s2 - s1)
    v : felem_t = u1 * i
    
    x3_1 : felem_t = to_felem(2) * v
    x3_2 : felem_t = (r ** 2) - j
    x3 : felem_t = x3_2 - x3_1
    
    y3_1 : felem_t = (to_felem(2) * s1) * j
    y3_2 : felem_t = r * (v - x3)
    y3 : felem_t = y3_2 - y3_1
    
    z3_ : felem_t = (z1 + z2) ** 2
    z3 : felem_t = (z3_ - (z1z1 + z2z2)) * h
    ret : jacobian_t
    if u1 == u2:
        if s1 == s2:
            ret = pointDouble(p)
        else:
            ret = jacobian(0, 1, 0)
    else:
        ret = x3, y3, z3
    return ret

@typechecked
def pointAdd(p: jacobian_t, q: jacobian_t) -> jacobian_t:
    ret:jacobian_t
    if isPointAtInfinity(p):
        ret = q
    elif isPointAtInfinity(q):
        ret = p
    else: 
        ret = pointAddFinite(p,q)
    return ret

@typechecked
def montgomery_ladder(k: scalar_t, init: jacobian_t) -> jacobian_t:
    p0 : jacobian_t = jacobian(0, 1, 0)
    p1 : jacobian_t = init
    for i in range(256):
        if k[255-i] == bit(1):
            (p0, p1) = (p1, p0)
        xx : jacobian_t = pointDouble(p0)
        xp1 : jacobian_t = pointAdd(p0, p1)
        if k[255-i] == bit(1):
            (p0, p1) = (xp1, xx)
        else:
            (p0, p1) = (xx, xp1)
    return p0


basePoint : jacobian_t = jacobian(0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
                                  0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
                                  1)


@typechecked
def point_mul(k: scalar_t) -> affine_t:
    jac : jacobian_t = montgomery_ladder(k, basePoint)
    return toAffine(jac)
