#!/usr/bin/python3

# To run and check this file, you need Python 3 + mypy
# See install instructions at: http://mypy.readthedocs.io/en/latest/getting_started.html
# To typecheck this file: mypy kyber.py
# To run this file: python3 kyber.py

from lib.speclib import *
from specs.keccak import *
from math import floor

kyber_q   = 7681
kyber_n   =  256

variant_k   = refine(nat_t, lambda x: x == 2 or x == 3 or x == 4)
variant_eta = refine(nat_t, lambda x: x == 5 or x == 4 or x == 3)

#These following will be global parameters, like in SHA/BLAKE etc.
kyber_k   =    3
kyber_eta =    4

kyber_dt  =   11
kyber_du  =   11
kyber_dv  =    3

zqelem_t = natmod_t(kyber_q)
def zqelem(n:nat):
    return natmod(n,kyber_q)
zqpoly_t    = vector_t(zqelem_t,kyber_n)
zqpolyvec_t = vector_t(zqpoly_t,kyber_k)

omega     = zqelem(3844)
psi       = zqelem(62)
n_inv     = zqelem(7651)
psi_inv   = zqelem(1115)
omega_inv = zqelem(6584)

def zqpoly_mul(p:zqpoly_t, q:zqpoly_t) -> zqpoly_t:
    s = array.create(kyber_n + kyber_n, zqelem(0))
    for i in range(kyber_n):
        for j in range(kyber_n):
            s[i+j] += p[i] * q[j]
    high = s[kyber_n:(kyber_n + kyber_n)]
    low = s[0:kyber_n]
    r = vector(low) - vector(high)
    return r

kyber_symbytes = 32
kyber_polycompressedbytes = 96
kyber_polybytes = 416

kyber_polyveccompressedbytes = kyber_k * 352
kyber_polyvecbytes = kyber_k * kyber_polybytes
kyber_indcpa_publickeybytes = kyber_polyveccompressedbytes + kyber_symbytes
kyber_indcpa_secretkeybytes = kyber_polyvecbytes
kyber_indcpa_bytes = kyber_polyveccompressedbytes + kyber_polycompressedbytes

symbytes_t = bytes_t(kyber_symbytes)

def decode(l:nat) -> Callable[[bytes_t], zqpoly_t]:
    def _decode(b:bytes_t) -> zqpoly_t:
        beta = bytes.to_uintn_le(b)
        res = vector.create(kyber_n, zqelem(0))
        for i in range(kyber_n):
            res[i] = zqelem(beta[i*l:(i+1)*l])
        return res
    return _decode

def encode(l:nat) -> Callable[[zqpoly_t],bytes_t]:
    def _encode(p:zqpoly_t) -> bytes_t:
        beta = uintn(0,256*l)
        for i in range(kyber_n):
            beta = uintn.set_bits(beta,i*l,(i+1)*l, uintn(p[i], l))
        return (bytes.from_uintn_le(beta))
    return _encode

def compress(d:int) -> Callable[[zqelem_t],zqelem_t]:
    def _compress(x:zqelem_t) -> zqelem_t:
        x = natmod.to_int(x)
        d2 = 2 ** d
        res = floor (d2 / kyber_q * x + 1 /2)
        return zqelem(res % d2)
    return _compress

def decompress(d:int) -> Callable[[zqelem_t],zqelem_t]:
    def _decompress(x:zqelem_t) -> zqelem_t:
        x = natmod.to_int(x)
        d2 = 2 ** d
        res = floor (kyber_q / d2 * x + 1/2)
        return zqelem(res)
    return _decompress

def decode_decompress(d:int):
    def _decode_decompress(b:bytes_t):
        return vector(vector.map(decompress(d), decode(d)(b)))
    return _decode_decompress

def compress_encode(d:int):
    def _compress_encode(b:zqpoly_t):
        return encode(d)(vector.map(compress(d), b))
    return _compress_encode

@typechecked
def msg_to_poly(m:symbytes_t) -> zqpoly_t:
    return decode_decompress(1)(m)

@typechecked
def poly_to_msg(p:zqpoly_t) -> symbytes_t:
    return compress_encode(1)(p)

@typechecked
def pack_sk(sk:zqpolyvec_t) -> bytes_t(kyber_indcpa_secretkeybytes):
    #encode_13(sk mod+ q)
    return bytes.concat_blocks(vector.map(lambda x:encode(13)(x), sk), vector.create(0, uint8(0)))

@typechecked
def unpack_sk(packedsk:bytes_t(kyber_indcpa_secretkeybytes)) -> zqpolyvec_t:
    #decode_13(sk)
    res, last = bytes.split_blocks(packedsk, kyber_polybytes)
    res = vector.map(lambda x: decode(13)(x), res)
    return res

@typechecked
def pack_pk(pk:zqpolyvec_t, seed:symbytes_t) -> bytes_t(kyber_indcpa_publickeybytes):
    #(encode_dt(compress_q(t, dt)) || seed)
    return bytes.concat_blocks(vector.map(compress_encode(kyber_dt), pk), seed)

@typechecked
def unpack_pk(packedpk:bytes_t(kyber_indcpa_publickeybytes)) -> tuple2 (zqpolyvec_t, symbytes_t):
    #decompress_q(decode_dt(pk), dt)
    res, seed = bytes.split_blocks(packedpk, 352)
    pk = vector.map(decode_decompress(kyber_dt), res)
    return (pk, seed)

@typechecked
def pack_ciphertext(b:zqpolyvec_t, v:zqpoly_t) -> bytes_t(kyber_indcpa_bytes):
    #(encode_du(compress_q(b, du)) || encode_dv(compress_q(v, dv)))
    return bytes.concat_blocks(vector.map(compress_encode(kyber_du), b), compress_encode(kyber_dv)(v))

@typechecked
def unpack_ciphertext(c:bytes_t(kyber_indcpa_bytes)) -> tuple2 (zqpolyvec_t, zqpoly_t):
    #(decompress_q(decode_du(c), du), decompress_q(decode_dv(c_v), dv))
    u1, v1 = bytes.split_blocks(c, 352)
    u = vector.map(decode_decompress(kyber_du), u1)
    v = decode_decompress(kyber_dv)(v1)
    return (u, v)

@typechecked
def cbd(buf:bytes_t(kyber_eta * kyber_n // 4)) -> zqpoly_t:
    beta = bytes.to_uintn_le(buf)
    res = array.create(kyber_n, zqelem(0))
    for i in range(kyber_n):
        a = uintn.bit_count(beta[2 * i * kyber_eta: (2 * i + 1) * kyber_eta])
        b = uintn.bit_count(beta[(2 * i + 1) * kyber_eta:(2 * i + 2) * kyber_eta])
        res[i] = zqelem(a - b)
    return vector(res)

#cbd(prf(seed, nonce)), prf = shake256
@typechecked
def poly_getnoise(seed:symbytes_t, nonce:uint8_t) -> zqpoly_t:
    extseed = bytes.concat(seed, bytes.singleton(nonce))
    buf = shake256(kyber_symbytes + 1, extseed, kyber_eta * kyber_n // 4)
    return cbd(buf)

@typechecked
def shake128_absorb(inputByteLen:size_nat_t,
                    input_b:vlbytes_t) -> state_t:
    return absorb(168, inputByteLen, input_b, uint8(0x1F))

@typechecked
def shake128_squeeze(s:state_t,
                     outputByteLen:size_nat_t) -> vlbytes_t:
    return squeeze(s, 168, outputByteLen)

#parse(xof(p || a || b)), xof = shake128
@typechecked
def genAij_hat(seed:symbytes_t, a:uint8_t, b:uint8_t) -> zqpoly_t:
    shake128_rate = 168
    res = vector.create(kyber_n, zqelem(0))
    extseed = bytes.concat(bytes.concat(seed, bytes.singleton(a)), bytes.singleton(b))

    maxnblocks = 4
    nblocks = maxnblocks
    state = shake128_absorb(kyber_symbytes + 2, extseed)
    buf = shake128_squeeze(state, shake128_rate * nblocks)

    i = 0
    j = 0
    while (j < kyber_n):
        d = uintn.to_int(buf[i]) + 256 * uintn.to_int(buf[i + 1])
        d = d % (2**13)
        if (d < kyber_q):
            res[j] = zqelem(d)
            j = j + 1
        i = i + 2
        if (i > shake128_rate * nblocks - 2):
            nblocks = 1
            buf = shake128_squeeze(state, shake128_rate * nblocks)
            i = 0
    return res

def genAij(seed:symbytes_t, a:uint8_t, b:uint8_t) -> zqpoly_t:
    def zqpoly_invntt(p:zqpoly_t) -> zqpoly_t:
        np = vector.create(kyber_n, zqelem(0))
        for i in range(kyber_n):
            for j in range(kyber_n):
                np[i] += (p[j] * (omega_inv ** (i * j)))
            np[i] *= n_inv * (psi_inv ** i)
        return np

    def zqpoly_bit_reverse(p:zqpoly_t) -> zqpoly_t:
        return array.createi(kyber_n, lambda i: p[int(uintn.reverse(uint8(i)))])

    return zqpoly_invntt(zqpoly_bit_reverse(genAij_hat(seed, a, b)))

@typechecked
def kyber_cpapke_keypair(coins:symbytes_t) -> \
    tuple2 (bytes_t(kyber_indcpa_publickeybytes), bytes_t(kyber_indcpa_secretkeybytes)):
    rhosigma = sha3_512(kyber_symbytes, coins)
    rho = rhosigma[0:kyber_symbytes]
    sigma = rhosigma[kyber_symbytes:(2*kyber_symbytes)]

    A = matrix.createi(kyber_k, kyber_k, lambda i, j: genAij(rho, uint8(j), uint8(i)))
    s = vector.createi(kyber_k, lambda i: poly_getnoise(sigma, uint8(i)))
    e = vector(vector.createi(kyber_k, lambda i: poly_getnoise(sigma, uint8(kyber_k + i))))
    t = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))

    for i in range(kyber_k):
        for j in range(kyber_k):
            t[i] += zqpoly_mul(A[i][j], s[j])

    t += e
    sk = pack_sk(s)
    pk = pack_pk(t, rho)
    return (pk, sk)

@typechecked
def kyber_cpapke_encrypt(m:symbytes_t,
                         packedpk:bytes_t(kyber_indcpa_publickeybytes),
                         coins:symbytes_t) -> \
                         bytes_t(kyber_indcpa_bytes):
    t, rho = unpack_pk(packedpk)

    At = matrix.createi(kyber_k, kyber_k, lambda i, j: genAij(rho, uint8(i), uint8(j)))
    r  = vector.createi(kyber_k, lambda i: poly_getnoise(coins, uint8(i)))
    e1 = vector(vector.createi(kyber_k, lambda i: poly_getnoise(coins, uint8(kyber_k + i))))
    e2 = poly_getnoise(coins, uint8(kyber_k + kyber_k))
    u  = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    v  = vector.create(kyber_n, zqelem(0))

    for i in range(kyber_k):
        for j in range(kyber_k):
            u[i] += zqpoly_mul(At[i][j], r[j])

    u += e1

    for i in range(kyber_k):
        v += zqpoly_mul(t[i], r[i])

    v += e2 + msg_to_poly(m)
    c = pack_ciphertext(u, v)
    return c

@typechecked
def kyber_cpapke_decrypt(c:bytes_t(kyber_indcpa_bytes),
                         sk:bytes_t(kyber_indcpa_secretkeybytes)) -> symbytes_t:
    u, v = unpack_ciphertext(c)
    s = unpack_sk(sk)

    d = vector.create(kyber_n, zqelem(0))

    for i in range(kyber_k):
        d += zqpoly_mul(vector(s[i]), vector(u[i]))

    d = v - d
    msg = poly_to_msg(d)
    return msg

#KyberKEM
kyber_publickeybytes = kyber_indcpa_publickeybytes
kyber_secretkeybytes = kyber_indcpa_secretkeybytes + kyber_indcpa_publickeybytes + 2 * kyber_symbytes
kyber_ciphertextbytes = kyber_indcpa_bytes

@typechecked
def crypto_kem_keypair(keypaircoins:symbytes_t, coins:symbytes_t) -> \
    tuple2 (bytes_t(kyber_publickeybytes), bytes_t(kyber_secretkeybytes)):
    pk, sk1 = kyber_cpapke_keypair(keypaircoins)
    sk = bytes.concat(sk1, bytes.concat(pk, bytes.concat(sha3_256(kyber_publickeybytes, pk), coins)))
    return (pk, sk)

@typechecked
def crypto_kem_enc(pk:bytes_t(kyber_publickeybytes),
                   msgcoins:symbytes_t) -> tuple2 (bytes_t(kyber_ciphertextbytes), symbytes_t):

    buf = bytes.concat(sha3_256(kyber_symbytes, msgcoins), sha3_256(kyber_publickeybytes, pk))

    kr = sha3_512(2 * kyber_symbytes, buf)
    ct = kyber_cpapke_encrypt(buf[0:kyber_symbytes], pk, kr[kyber_symbytes:(2*kyber_symbytes)])
    kr[kyber_symbytes:(2*kyber_symbytes)] = sha3_256(kyber_ciphertextbytes, ct)
    ss = sha3_256(2*kyber_symbytes, kr)
    return (ct, ss)

@typechecked
def crypto_kem_dec(ct:bytes_t(kyber_ciphertextbytes),
                   sk:bytes_t(kyber_secretkeybytes)) -> symbytes_t:
    pk = sk[kyber_indcpa_secretkeybytes:(kyber_indcpa_secretkeybytes + kyber_indcpa_publickeybytes)]
    sk1 = sk[0:kyber_indcpa_secretkeybytes]
    sk2 = sk[(kyber_indcpa_secretkeybytes + kyber_indcpa_publickeybytes):(kyber_secretkeybytes - kyber_symbytes)]
    buf = bytes.concat(kyber_cpapke_decrypt(ct, sk1), sk2)
    kr = sha3_512(2 * kyber_symbytes, buf)
    cmp1 = kyber_cpapke_encrypt(buf[0:kyber_symbytes], pk, kr[kyber_symbytes:(2 * kyber_symbytes)])
    kr[kyber_symbytes:(2 * kyber_symbytes)] = sha3_256(kyber_ciphertextbytes, ct)
    if (cmp1 == ct):
        kr[0:kyber_symbytes] = kr[0:kyber_symbytes]
    else:
        kr[0:kyber_symbytes] = sk[(kyber_secretkeybytes - kyber_symbytes):kyber_secretkeybytes]
    ss = sha3_256(2 * kyber_symbytes, kr)
    return ss
