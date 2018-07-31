#!/usr/bin/python3

from lib.speclib import *

# Define prime field
p25519 : nat_t = (2 ** 255) - 19

felem_t = natmod_t(p25519)
@typechecked
def to_felem(x: nat_t) -> felem_t:
    return natmod(x,p25519)
zero : felem_t = to_felem(0)
one  : felem_t = to_felem(1)
@typechecked
def finv(x: felem_t) -> felem_t:
    return x ** (p25519 - 2)

point_t  = tuple_t(felem_t, felem_t)  # projective coordinates
scalar_t = uintn_t(256)
@typechecked
def to_scalar(i:nat_t) -> uintn_t(256):
    return uintn(i,256)
serialized_point_t = bytes_t(32)
serialized_scalar_t = bytes_t(32)

g25519: point_t = (to_felem(9), to_felem(1))


@typechecked
def point(a: nat_t, b: nat_t) -> point_t:
    return to_felem(a), to_felem(b)


@typechecked
def decodeScalar(s: serialized_scalar_t) -> scalar_t:
    k : serialized_scalar_t = bytes.copy(s)
    k[0] &= uint8(248)
    k[31] &= uint8(127)
    k[31] |= uint8(64)
    return to_scalar(bytes.to_nat_le(k))


@typechecked
def decodePoint(u: serialized_point_t) -> point_t:
    b : nat_t = bytes.to_nat_le(u)
    return point((b % (2 ** 255)) % p25519, 1)


@typechecked
def encodePoint(p: point_t) -> serialized_point_t:
    x:felem_t
    y:felem_t
    (x,y) = p
    b : nat_t = natmod.to_int(x * finv(y))
    return bytes.from_nat_le(b, 32)


@typechecked
def point_add_and_double(q: point_t, nq: point_t, nqp1: point_t) -> tuple_t(point_t, point_t):
    x_1 : felem_t
    z_1 : felem_t
    x_2 : felem_t
    z_2 : felem_t
    x_3 : felem_t
    z_3 : felem_t
    (x_1, z_1) = q
    (x_2, z_2) = nq
    (x_3, z_3) = nqp1
    a  : felem_t = x_2 + z_2
    aa : felem_t = a ** 2
    b  : felem_t = x_2 - z_2
    bb : felem_t = b * b
    e  : felem_t = aa - bb
    c  : felem_t = x_3 + z_3
    d  : felem_t = x_3 - z_3
    da : felem_t = d * a
    cb : felem_t = c * b
    x_3 = (da + cb) ** 2
    z_3 = x_1 * ((da - cb) ** 2)
    x_2 = aa * bb
    z_2 = e * (aa + (to_felem(121665) * e))
    return ((x_2, z_2), (x_3, z_3))


@typechecked
def montgomery_ladder(k: scalar_t, init: point_t) -> point_t:
    p0: point_t = point(1, 0)
    p1: point_t = init
    for i in range(256):
        if k[255-i] == bit(1):
            (p1, p0) = point_add_and_double(init, p1, p0)
        else:
            (p0, p1) = point_add_and_double(init, p0, p1)
    return p0


@typechecked
def scalarmult(s: serialized_scalar_t, p: serialized_point_t) -> serialized_point_t:
    s_:scalar_t = decodeScalar(s)
    p_:point_t  = decodePoint(p)
    r :point_t  = montgomery_ladder(s_, p_)
    return encodePoint(r)

# ECDH API: we assume a key generation function that generates 32 random bytes for serialized_scalar_t

@typechecked
def is_on_curve(s: serialized_point_t) -> bool:
    n : nat_t = bytes.to_nat_le(s)
    disallowed : array_t(nat_t,12) = array([0, 1, 325606250916557431795983626356110631294008115727848805560023387167927233504, 39382357235489614581723060781553021112529911719440698176882885853963445705823, 2**255 - 19 - 1, 2**255 - 19, 2**255 - 19 + 1, 2**255 - 19 + 325606250916557431795983626356110631294008115727848805560023387167927233504, 2**255 - 19 + 39382357235489614581723060781553021112529911719440698176882885853963445705823, 2*(2**255 - 19) - 1, 2*(2**255 - 19), 2*(2**255 - 19) + 1])
    res : bool = True
    for i in range(array.length(disallowed)):
        if n == disallowed[i]:
            res = False
    return res


@typechecked
def private_to_public(s: serialized_scalar_t) -> serialized_point_t:
    return scalarmult(s, encodePoint(g25519))


@typechecked
def ecdh_shared_secret(priv: serialized_scalar_t, pub: serialized_point_t) -> result_t(serialized_point_t):
    res : result_t(serialized_point_t)
    if is_on_curve(pub):
        res = result.retval(scalarmult(priv, pub))
    else:
        res = result.error("public key is not on curve")
    return res
