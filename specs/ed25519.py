
#!/usr/bin/python3

from lib.speclib import *
from specs.curve25519 import felem_t, to_felem, finv, serialized_scalar_t, serialized_point_t, scalar_t, p25519,to_scalar, zero, one
from specs.sha2 import sha512

# Define prime field
d25519: felem_t = (to_felem(
    37095705934669439343138083508754565189542113879843219016388785533085940283555))

q25519 : nat_t = nat((1 << 252) + 27742317777372353535851937790883648493)
qelem_t = natmod_t(q25519)
@typechecked
def to_qelem(n:nat_t) -> qelem_t:
    return natmod(n,q25519)

extended_point_t = tuple_t(felem_t, felem_t, felem_t, felem_t)

@typechecked
def extended_point(a: felem_t, b: felem_t, c: felem_t, d: felem_t) -> extended_point_t:
    return (a,b,c,d)

@typechecked
def sha512_modq(s: vlbytes_t) -> qelem_t:
    h : digest_t = sha512(s)
    return to_qelem(bytes.to_nat_le(h))


@typechecked
def point_add(p: extended_point_t, q: extended_point_t) -> extended_point_t:
    if p == extended_point(zero, one, one, zero):
        return q
    if q == extended_point(zero, one, one, zero):
        return p
    x1 : felem_t
    x2 : felem_t
    y1 : felem_t
    y2 : felem_t
    z1 : felem_t
    z2 : felem_t
    t1 : felem_t
    t2 : felem_t
    (x1, y1, z1, t1) = p
    (x2, y2, z2, t2) = q
    a : felem_t = (y1 - x1) * (y2 - x2)
    b : felem_t = (y1 + x1) * (y2 + x2)
    c : felem_t = to_felem(2) * d25519 * t1 * t2
    d : felem_t = to_felem(2) * z1 * z2
    e : felem_t = b - a
    f : felem_t = d - c
    g : felem_t = d + c
    h : felem_t = b + a
    x3 : felem_t = e * f
    y3 : felem_t = g * h
    t3 : felem_t = e * h
    z3 : felem_t = f * g
    return extended_point(x3, y3, z3, t3)


@typechecked
def point_double(p: extended_point_t) -> extended_point_t:
    if p == extended_point(zero, one, one, zero):
        return p
    x1 : felem_t
    y1 : felem_t
    z1 : felem_t
    t1 : felem_t
    (x1, y1, z1, t1) = p
    a : felem_t = x1 ** 2
    b : felem_t = y1 ** 2
    c : felem_t = to_felem(2) * (z1 ** 2)
    h : felem_t = a + b
    e : felem_t = h - ((x1 + y1) ** 2)
    g : felem_t = a - b
    f : felem_t = c + g
    x3 : felem_t = e * f
    y3 : felem_t = g * h
    t3 : felem_t = e * h
    z3 : felem_t = f * g
    return extended_point(x3, y3, z3, t3)


@typechecked
def montgomery_ladder(k: scalar_t, init: extended_point_t) -> extended_point_t:
    p0: extended_point_t = extended_point(zero, one, one, zero)
    p1: extended_point_t = init
    for i in range(256):
        if k[255-i] == bit(1):
            (p0, p1) = (p1, p0)
        xx : extended_point_t = point_double(p0)
        xp1 : extended_point_t = point_add(p0, p1)
        if k[255-i] == bit(1):
            (p0, p1) = (xp1, xx)
        else:
            (p0, p1) = (xx, xp1)
    return p0


@typechecked
def point_mul(s: serialized_scalar_t, p: extended_point_t) -> extended_point_t:
    s_ : scalar_t = to_scalar(bytes.to_nat_le(s))
    Q : extended_point_t = extended_point(zero, one, one, zero)
    Q1 : extended_point_t = montgomery_ladder(s_, p)
    return Q1


@typechecked
def point_compress(p: extended_point_t) -> serialized_point_t:
    px : felem_t
    py : felem_t
    pz : felem_t
    pt : felem_t
    (px, py, pz, pt) = p
    zinv : felem_t = finv(pz)
    x : felem_t = px * zinv
    y : felem_t = py * zinv
    r : int = (2**255 * (natmod.to_int(x) % 2)) + natmod.to_int(y)
    return bytes.from_nat_le(r)

fsqrt_m1: felem_t = (to_felem(pow(2, ((p25519 - 1) // 4), p25519)))
  

@typechecked
def recover_x_coordinate(y:nat_t,sign:bool) -> result_t(felem_t):
    if y >= p25519:
        return result.error("y >= p25519")
    else:
        y : felem_t = to_felem(y)
        p1 : felem_t = d25519 * (y ** 2)
        p1_1 : felem_t = p1 + one
        x2 : felem_t = ((y ** 2) - one) * finv(p1_1)
        if x2 == zero and sign:
            return result.error("x == -0")
        elif x2 == zero and not sign:
            return result.retval(to_felem(0))
        else:
            x : felem_t = x2 ** ((p25519 + 3)//8)
            if (x ** 2) - x2 != zero:
                x = x * fsqrt_m1
            if ((x ** 2) - x2) != zero:
                return result.error("x**2 - x2 is not 0")
            else:
                if (natmod.to_int(x) % 2 == 1) != sign:
                    return result.retval(to_felem(p25519 - natmod.to_int(x)))
                else:
                    return result.retval(x)


@typechecked
def point_decompress(s:serialized_point_t) -> result_t(extended_point_t) :
    y : nat_t = bytes.to_nat_le(s)
    sign : bool = (y // (1 << 255)) % 2 == 1
    y : nat_t = y % (1 << 255)
    x : result_t(felem_t) = recover_x_coordinate(y, sign)
    if result.is_valid(x):
        x : felem_t = result.get_value(x)
        y_felemt : felem_t = to_felem(y)
        r : extended_point_t = extended_point(x, y_felemt, one, x * y_felemt)
        return result.retval(r)
    return result.error("Couldn't recover X coordinate.")

@typechecked
def expand_secret(s: serialized_scalar_t) -> tuple2(serialized_scalar_t, serialized_scalar_t):
    h : digest_t = sha512(s)
    h_low : bytes_t = h[0:32]
    h_high : bytes_t = h[32:64]
    h_low[0] &= uint8(0xf8)
    h_low[31] &= uint8(127)
    h_low[31] |= uint8(64)
    return serialized_scalar_t(h_low), serialized_scalar_t(h_high)


_g_x: felem_t = (to_felem(
    15112221349535400772501151409588531511454012693041857206046113283949847762202))
_g_y: felem_t = (to_felem(
    46316835694926478169428394003475163141307993866256225615783033603165251855960))

g_ed25519: extended_point_t = extended_point(_g_x, _g_y, one, _g_x * _g_y)

sigval_t = bytes_t(64)


@typechecked
def private_to_public(s: serialized_scalar_t) -> serialized_point_t:
    a : serialized_scalar_t
    (a, _) = expand_secret(s)
    return point_compress(point_mul(s, g_ed25519))


@typechecked
def sign(priv: serialized_scalar_t, msg: vlbytes_t) -> sigval_t:
    a : serialized_scalar_t
    prefix : serialized_scalar_t
    a, prefix = expand_secret(priv)
    ap : serialized_point_t = point_compress(point_mul(a, g_ed25519))
    tmp = bytes(array.create(array.length(msg)+64, uint8(0)))
    tmp[32:64] = prefix
    tmp[64:array.length(msg)] = msg
    pmsg : bytes_t = tmp[32:array.length(msg)]
    r : qelem_t = sha512_modq(pmsg)
    rp : serialized_point_t = point_compress(point_mul(bytes.from_nat_le(natmod.to_int(r)), g_ed25519))
    tmp[0:32] = rp
    tmp[32:64] = ap
    h : qelem_t = sha512_modq(tmp)
    s : qelem_t = r + (h * to_qelem(bytes.to_nat_le(a)))
    tmp[32:64] = bytes.from_nat_le(natmod.to_int(s))
    return tmp[0:64]


@typechecked
def point_equal(p: extended_point_t, q: extended_point_t) -> bool:
    px : felem_t
    py : felem_t
    pz : felem_t
    pt : felem_t
    qx : felem_t
    qy : felem_t
    qz : felem_t
    qt : felem_t
    (px, py, pz, pt) = p
    (qx, qy, qz, qt) = q
    return (px * qz == qx * pz) and (py * qz == qy * pz)


@typechecked
def verify(pub: serialized_point_t, msg: vlbytes_t, sigval: sigval_t) -> bool:
    ap : result_t(felem_t) = point_decompress(pub)
    if not result.is_valid(ap):
        return False
    ap : felem_t = result.get_value(ap)
    rs : bytes_t = sigval[0:32]
    rp : result_t(felem_t) = point_decompress(rs)
    if not result.is_valid(rp):
        return False
    rp : felem_t = result.get_value(rp)
    s : nat_t = bytes.to_nat_le(sigval[32:64])
    if s >= q25519:
        return False
    else:
        tmp = bytes(array.create(array.length(msg)+64, uint8(0)))
        tmp[0:32] = rs
        tmp[32:64] = pub
        tmp[64:array.length(msg)] = msg
        h : qelem_t = sha512_modq(tmp)
        sB : extended_point_t = point_mul(bytes.from_nat_le(s), g_ed25519)
        hA : extended_point_t = point_mul(bytes.from_nat_le(natmod.to_int(h)), ap)
        return point_equal(sB, point_add(rp, hA))
