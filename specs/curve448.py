#!/usr/bin/python3

from lib.speclib import *

p448 : int = 2 ** 448 - 2 ** 224 - 1
felem_t = natmod_t(p448)
@typechecked
def to_felem(x: nat_t) -> felem_t:
    return natmod(x, p448)

@typechecked
def finv(x: felem_t) -> felem_t:
    return x ** (p448 - 2)

point_t = tuple_t(felem_t, felem_t)


@typechecked
def point(a: int, b: int) -> point_t:
    return to_felem(nat(a)), to_felem(nat(b))


scalar_t = uintn_t(448)

@typechecked
def to_scalar(n:nat_t) -> scalar_t:
    return uintn(n, 448)

serialized_point_t = bytes_t(56)
serialized_scalar_t = bytes_t(56)


@typechecked
def decodeScalar(s: serialized_scalar_t) -> scalar_t:
    k: serialized_scalar_t = bytes.copy(s)
    k[0] &= uint8(252)
    k[55] |= uint8(128)
    return to_scalar(bytes.to_nat_le(k))


@typechecked
def decodePoint(u: serialized_point_t) -> point_t:
    b : nat_t = bytes.to_nat_le(u)
    return point((b % (2 ** 448)) % p448, 1)


@typechecked
def encodePoint(p: point_t) -> serialized_point_t:
    x:felem_t
    y:felem_t
    (x,y) = p
    b : int = natmod.to_int(x * finv(y))
    return bytes.from_nat_le(b, 56)


@typechecked
def point_add_and_double(q: point_t, nq: point_t, nqp1: point_t) -> tuple_t(point_t, point_t):
    x_1 : felem_t
    x_2 : felem_t
    x_3 : felem_t
    z_1 : felem_t
    z_2 : felem_t
    z_3 : felem_t
    (x_1, z_1) = q
    (x_2, z_2) = nq
    (x_3, z_3) = nqp1
    a : felem_t = x_2 + z_2
    aa : felem_t = a ** 2
    b : felem_t = x_2 - z_2
    bb : felem_t = b ** 2
    e : felem_t = aa - bb
    c : felem_t = x_3 + z_3
    d : felem_t = x_3 - z_3
    da : felem_t = d * a
    cb : felem_t = c * b
    x_3 : felem_t = (da + cb) ** 2
    z_3 : felem_t = x_1 * ((da - cb) ** 2)
    x_2 : felem_t = aa * bb
    z_2 : felem_t = e * (aa + (to_felem(39081) * e))
    return ((x_2, z_2), (x_3, z_3))


@typechecked
def montgomery_ladder(k: scalar_t, init: point_t) -> point_t:
    p0: point_t = point(1, 0)
    p1: point_t = init
    for i in range(448):
        if k[447-i] == bit(1):
            (p1, p0) = point_add_and_double(init, p1, p0)
        else:
            (p0, p1) = point_add_and_double(init, p0, p1)
    return(p0)


@typechecked
def scalarmult(s: serialized_scalar_t, p: serialized_point_t) -> serialized_point_t:
    s_ : scalar_t = decodeScalar(s)
    p_ : point_t = decodePoint(p)
    r : point_t = montgomery_ladder(s_, p_)
    return encodePoint(r)
