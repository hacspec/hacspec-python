from lib.speclib import *

prime = 2**256 - 2**224 + 2**192 + 2**96 - 1



felem_t,felem = refine(nat_t, lambda x: x < prime)


@typechecked
def to_felem(x: nat_t) -> felem_t:
    return felem(nat(x % prime))


@typechecked
def fadd(x: felem_t, y: felem_t) -> felem_t:
    return to_felem(x + y)


@typechecked
def fsub(x: felem_t, y: felem_t) -> felem_t:
    return to_felem(x - y)


@typechecked
def fmul(x: felem_t, y: felem_t) -> felem_t:
    return to_felem(x * y)


@typechecked
def fsqr(x: felem_t) -> felem_t:
    return to_felem(x * x)


@typechecked
def fexp(x: felem_t, n: nat_t) -> felem_t:
    return to_felem(pow(x, n, prime))


@typechecked
def finv(x: felem_t) -> felem_t:
    return to_felem(pow(x, prime-2, prime))


extended_point_t = tuple4(felem_t, felem_t, felem_t, felem_t)
jacobian_t = tuple3(felem_t, felem_t, felem_t)
affine_t = tuple2(felem_t, felem_t)


@typechecked
def jacobian(a: int, b: int, c: int) -> jacobian_t:
    return to_felem(nat(a)), to_felem(nat(b)), to_felem(nat(c))


scalar_t = bitvector_t(256)
def to_scalar(n:int):
    return bitvector(n,256)
    
serialized_point_t = bytes_t(33)
serialized_scalar_t = bytes_t(32)


@typechecked
def toAffine(p: jacobian_t) -> affine_t:
    (x, y, z) = p
    z2 = fsqr(z)
    z2i = finv(z2)
    z3 = fmul(z, z2)
    z3i = finv(z3)
    x = fmul(x, z2i)
    y = fmul(y, z3i)
    return x, y


@typechecked
def pointDouble(p: jacobian_t) -> jacobian_t:
    (x1, y1, z1) = p
    delta = fsqr(z1)
    gamma = fsqr(y1)

    beta = fmul(x1, gamma)

    alpha_1 = fsub(x1, delta)
    alpha_2 = fadd(x1, delta)
    alpha = fmul(felem(nat(3)), fmul(alpha_1, alpha_2))

    x3 = fsub(fsqr(alpha), fmul(felem(nat(8)), beta))

    z3_ = fsqr(fadd(y1, z1))
    z3 = fsub(z3_, fadd(gamma, delta))

    y3_1 = fsub(fmul(felem(nat(4)), beta), x3)
    y3_2 = fmul(felem(nat(8)), fsqr(gamma))
    y3 = fsub(fmul(alpha, y3_1), y3_2)
    return x3, y3, z3


@typechecked
def isPointAtInfinity(p: jacobian_t) -> bool:
    (_, _, z) = p
    return (z == 0)


@typechecked
def pointAdd(p: jacobian_t, q: jacobian_t) -> jacobian_t:
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
        if s1 == s2:
            return pointDouble(p)
        else:
            return jacobian(0, 1, 0)
    h = fsub(u2, u1)
    i = fsqr(fmul(felem(nat(2)), h))
    j = fmul(h, i)
    r = fmul(felem(nat(2)), fsub(s2, s1))
    v = fmul(u1, i)

    x3_1 = fmul(felem(nat(2)), v)
    x3_2 = fsub(fsqr(r), j)
    x3 = fsub(x3_2, x3_1)

    y3_1 = fmul(fmul(felem(nat(2)), s1), j)
    y3_2 = fmul(r, fsub(v, x3))
    y3 = fsub(y3_2, y3_1)

    z3_ = fsqr(fadd(z1, z2))
    z3 = fmul(fsub(z3_, fadd(z1z1, z2z2)), h)
    return x3, y3, z3


@typechecked
def montgomery_ladder(k: scalar_t, init: jacobian_t) -> jacobian_t:
    p0 = jacobian(0, 1, 0)
    p1 = init
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


basePoint = jacobian(0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
                     0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
                     1)


@typechecked
def point_mul(k: scalar_t) -> affine_t:
    jac = montgomery_ladder(k, basePoint)
    return toAffine(jac)
