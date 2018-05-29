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


def zqpoly_ntt(p:zqpoly_t) -> zqpoly_t:
    np = vector.create(kyber_n, zqelem(0))
    for i in range(kyber_n):
        for j in range(kyber_n):
            np[i] += (((psi ** j) * p[j]) * (omega ** (i * j)))
    return np

def zqpoly_invntt(p:zqpoly_t) -> zqpoly_t:
    np = vector.create(kyber_n, zqelem(0))
    for i in range(kyber_n):
        for j in range(kyber_n):
            np[i] += (p[j] * (omega_inv ** (i * j)))
        np[i] *= n_inv * (psi_inv ** i)
    return np

def zqpoly_bit_reverse(p:zqpoly_t) -> zqpoly_t:
    res = vector.create(kyber_n, zqelem(0))
    for i in range(kyber_n):
        i_new = uintn.reverse(uint8(i))
        res[i] = p[int(i_new)]
    return res

#TESTING NTT
#just for debugging
# def mul_schoolbook(p:zqpoly_t, q:zqpoly_t) -> zqpoly_t:
#     s = array.create(kyber_n + kyber_n, zqelem(0))
#     for i in range(kyber_n):
#         for j in range(kyber_n):
#             s[i+j] += p[i] * q[j]
#     high = s[kyber_n:(kyber_n + kyber_n)]
#     low = s[0:kyber_n]
#     r = vector(low) - vector(high)
#     return r

# def mul_nttbased(p:zqpoly_t, q:zqpoly_t) -> zqpoly_t:
#     return zqpoly_invntt(zqpoly_ntt(p) * zqpoly_ntt(q))

# a = vector.create(256,zqelem(0))
# for i in range(256):
#     a[i] = zqelem(i)
# #print(a)

# b = vector.create(256,zqelem(0))
# for i in range(256):
#     b[i] = zqelem(i+42)
# #print(b)

# r2 = mul_nttbased(a,b)
# r1 = mul_schoolbook(a,b)
# print(r1 == r2)


def zqpolyvec_ntt(r:zqpolyvec_t) :
    return vector.map(zqpoly_ntt,r)
def zqpolyvec_invntt(r:zqpolyvec_t) :
    return vector(vector.map(zqpoly_invntt,r))
def zqpolyvec_bit_reverse(p:zqpolyvec_t):
    return vector.map(zqpoly_bit_reverse,p)

kyber_symbytes = 32
kyber_polycompressedbytes = 96
kyber_polybytes = 416

kyber_polyveccompressedbytes = kyber_k * 352
kyber_polyvecbytes = kyber_k * kyber_polybytes
kyber_indcpa_publickeybytes = kyber_polyveccompressedbytes + kyber_symbytes
kyber_indcpa_secretkeybytes = kyber_polyvecbytes
kyber_indcpa_bytes = kyber_polyveccompressedbytes + kyber_polycompressedbytes

symbytes_t = bytes_t(kyber_symbytes)

def decode(l:nat, b:bytes_t) -> [int]:
    beta = bytes.to_uintn_le(b)
    res = array.create(kyber_n, 0)
    for i in range(kyber_n):
        res[i] = beta[i*l:(i+1)*l]
    return res

def encode(l:nat, p:[int]) -> bytes_t:
    beta = uintn(0,256*l)
    for i in range(kyber_n):
        beta = uintn.set_bits(beta,i*l,(i+1)*l,uintn(p[i], l))
    return (bytes.from_uintn_le(beta))

def compress(x:zqelem_t, d:int) -> int:
    x = natmod.to_int(x)
    d2 = 2 ** d
    res = floor (d2 / kyber_q * x + 1 /2)
    return res % d2

def decompress(x:int, d:int) -> zqelem_t:
    x = uintn.to_int(x)
    d2 = 2 ** d
    res = floor (kyber_q / d2 * x + 1/2)
    return zqelem(res)

@typechecked
def msg_to_poly(m:symbytes_t) -> zqpoly_t:
    return vector(vector.map(lambda x: decompress(x,1),decode(1,m)))

@typechecked
def poly_to_msg(p:zqpoly_t) -> symbytes_t:
    return encode(1,vector.map(lambda x: compress(x,1),p))

@typechecked
def pack_sk(sk:zqpolyvec_t) -> \
    refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_secretkeybytes):
    #encode_13(sk mod+ q)
    res = array.create(kyber_polyvecbytes, uint8(0))
    for i in range(kyber_k):
        res[i*kyber_polybytes:(i+1)*kyber_polybytes] = encode(13, vector.map(lambda x:natmod.to_int(x),sk[i]))
    return res

@typechecked
def unpack_sk(packedsk: refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_secretkeybytes)) -> zqpolyvec_t:
    #decode_13(sk)
    res = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    for i in range(kyber_k):
        res[i] = vector(vector.map(lambda x:zqelem(x), decode(13, packedsk[i*kyber_polybytes:(i+1)*kyber_polybytes])))
    return res

@typechecked
def pack_pk(pk:zqpolyvec_t, seed:symbytes_t) -> \
    refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_publickeybytes):
    #(encode_dt(compress_q(t, dt)) || seed)
    res = array.create(kyber_indcpa_publickeybytes, uint8(0))
    for i in range(kyber_k):
        res[i*352:(i+1)*352] = encode(kyber_dt, vector.map(lambda x:compress(x, kyber_dt), pk[i]))
    res[kyber_polyveccompressedbytes:kyber_indcpa_publickeybytes] = seed
    return res

@typechecked
def unpack_pk(packedpk:refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_publickeybytes)) ->\
    tuple2 (zqpolyvec_t, symbytes_t):
    #decompress_q(decode_dt(pk), dt)
    pk = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    for i in range(kyber_k):
        pk[i] = vector.map(lambda x: decompress(x, kyber_dt), decode(kyber_dt, packedpk[i*352:(i+1)*352]))

    seed = packedpk[kyber_polyveccompressedbytes:kyber_indcpa_publickeybytes]
    return (pk, seed)

@typechecked
def pack_ciphertext(b:zqpolyvec_t, v:zqpoly_t) -> \
    refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_bytes):
    #encode_du(compress_q(b, du))
    res = array.create(kyber_indcpa_bytes, uint8(0))
    for i in range(kyber_k):
        res[i*352:(i+1)*352] = encode(kyber_du, vector.map(lambda x:compress(x, kyber_du), b[i]))

    #encode_dv(compress_q(v, dv))
    res[kyber_polyveccompressedbytes:kyber_indcpa_bytes] = encode(kyber_dv, vector.map(lambda x:compress(x, kyber_dv), v))
    return res

@typechecked
def unpack_ciphertext(c:refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_bytes)) -> \
    tuple2 (zqpolyvec_t, zqpoly_t):
    #decompress_q(decode_du(c), du)
    u = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    for i in range(kyber_k):
        u[i] = vector.map(lambda x:decompress(x, kyber_du), decode(kyber_du, c[i*352:(i+1)*352]))

    #decompress_q(decode_dv(c_v), dv)
    v = vector(vector.map(lambda x:decompress(x, kyber_dv), decode(kyber_dv, c[kyber_polyveccompressedbytes:kyber_indcpa_bytes])))
    return (u, v)

@typechecked
def bytesToBits(b:vlbytes_t) -> bitvector_t:
    return bitvector(bytes.to_nat_le(b), 8 * array.length(b))

#Sampling from a binomial distribution
@typechecked
def cbd(buf:refine(vlbytes_t, lambda x: array.length(x) == kyber_eta * kyber_n // 4)) -> zqpoly_t:
    beta = bytesToBits(buf)
    res = array.create(kyber_n, zqelem(0))
    for i in range(kyber_n):
        a = nat(0)
        b = nat(0)
        for j in range(kyber_eta):
            a = a + uintn.to_int(beta[2 * i * kyber_eta + j])
        for j in range(kyber_eta):
            b = b + uintn.to_int(beta[2 * i * kyber_eta + kyber_eta + j])
        res[i] = zqelem(a) - zqelem(b)
    return vector(res)

#cbd(prf(seed, nonce)), prf = shake256
@typechecked
def poly_getnoise(seed:symbytes_t, nonce:uint8_t) -> zqpoly_t:
    extseed = array.create(kyber_symbytes + 1, uint8(0))
    extseed[0:kyber_symbytes] = seed
    extseed[kyber_symbytes] = nonce
    buf = shake256(kyber_symbytes + 1, extseed, kyber_eta * kyber_n // 4)
    r = cbd(buf)
    return vector(r)

@typechecked
def shake128_absorb(inputByteLen:size_nat_t,
                    input_b:refine(vlbytes_t, lambda x: array.length(x) == inputByteLen)) -> state_t:
    return absorb(168, inputByteLen, input_b, uint8(0x1F))

@typechecked
def shake128_squeeze(s:state_t,
                     outputByteLen:size_nat_t) -> refine(vlbytes_t, lambda x: array.length(x) == outputByteLen):
    return squeeze(s, 168, outputByteLen)

#parse(xof(p || a || b)), xof = shake128
@typechecked
def genAij(seed:symbytes_t, a:uint8_t, b:uint8_t) -> zqpoly_t:
    shake128_rate = 168
    res = vector.create(kyber_n, zqelem(0))

    extseed = array.create(kyber_symbytes + 2, uint8(0))
    extseed[0:kyber_symbytes] = seed
    extseed[kyber_symbytes] = a
    extseed[kyber_symbytes + 1] = b

    maxnblocks = 4
    nblocks = maxnblocks
    state = shake128_absorb(kyber_symbytes + 2, extseed)
    buf = shake128_squeeze(state, shake128_rate * nblocks)

    i = 0
    j = 0
    while (j < kyber_n):
        d = uint16(buf[i]) | (uint16(buf[i + 1]) << 8)
        d = int(d & uint16(0x1fff))
        if (d < kyber_q):
            res[j] = zqelem(d)
            j = j + 1
        i = i + 2
        if (i > shake128_rate * nblocks - 2):
            nblocks = 1
            buf = shake128_squeeze(state, shake128_rate * nblocks)
            i = 0
    return res

# array.length(fst(res)) == kyber_indcpa_publickeybytes
# array.length(snd(res)) == kyber_indcpa_secretkeybytes
@typechecked
def kyber_cpapke_keypair(coins:symbytes_t) -> tuple2 (vlbytes_t, vlbytes_t):
    rhosigma = sha3_512(kyber_symbytes, coins)
    rho = rhosigma[0:kyber_symbytes]
    sigma = rhosigma[kyber_symbytes:(2*kyber_symbytes)]

    n = uint8(0)
    s = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    e = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    that = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    A = matrix.create(kyber_k, kyber_k, vector.create(kyber_n, zqelem(0)))

    for i in range(kyber_k):
        for j in range(kyber_k):
            A[i][j] = genAij(rho, uint8(j), uint8(i))

    for i in range(kyber_k):
        s[i] = poly_getnoise(sigma, n)
        n += uint8(1)

    for i in range(kyber_k):
        e[i] = poly_getnoise(sigma, n)
        n += uint8(1)

    shat = zqpolyvec_bit_reverse(zqpolyvec_ntt(s))

    for i in range(kyber_k):
        for j in range(kyber_k):
            that[i] += A[i][j] * shat[j]

    t = zqpolyvec_invntt(zqpolyvec_bit_reverse(that))
    t += e

    sk = pack_sk(shat)
    pk = pack_pk(t, rho)

    return (pk, sk)

@typechecked
def kyber_cpapke_encrypt(m:symbytes_t,
                         packedpk:refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_publickeybytes),
                         coins:symbytes_t) -> \
                         refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_bytes):
    n = uint8(0)
    r = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    e1 = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    uhat = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
    vhat = vector.create(kyber_n, zqelem(0))
    At = matrix.create(kyber_k, kyber_k, vector.create(kyber_n, zqelem(0)))

    t, rho = unpack_pk(packedpk)

    for i in range(kyber_k):
        for j in range(kyber_k):
            At[i][j] = genAij(rho, uint8(i), uint8(j))

    for i in range(kyber_k):
        r[i] = poly_getnoise(coins, n)
        n += uint8(1)

    for i in range(kyber_k):
        e1[i] = poly_getnoise(coins, n)
        n += uint8(1)

    e2 = poly_getnoise(coins, n)
    rhat = zqpolyvec_bit_reverse(zqpolyvec_ntt(r))

    for i in range(kyber_k):
        for j in range(kyber_k):
            uhat[i] += At[i][j] * rhat[j]

    u = zqpolyvec_invntt(zqpolyvec_bit_reverse(uhat))
    u += e1
    that = zqpolyvec_bit_reverse(zqpolyvec_ntt(t))

    for i in range(kyber_k):
        vhat += that[i] * rhat[i]

    v = zqpoly_invntt(zqpoly_bit_reverse(vhat))
    v += e2 + msg_to_poly(m)
    c = pack_ciphertext(u, v)

    return c

@typechecked
def kyber_cpapke_decrypt(c:refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_bytes),
                         sk:refine(vlbytes_t, lambda x: array.length(x) == kyber_indcpa_secretkeybytes)) -> symbytes_t:
    dhat = vector.create(kyber_n, zqelem(0))

    u, v = unpack_ciphertext(c)
    s = unpack_sk(sk)

    uhat = zqpolyvec_bit_reverse(zqpolyvec_ntt(u))

    for i in range(kyber_k):
        dhat += s[i] * uhat[i]

    d = zqpoly_invntt(zqpoly_bit_reverse(dhat))
    d = v - d
    msg = poly_to_msg(d)

    return msg

#KyberKEM
kyber_publickeybytes = kyber_indcpa_publickeybytes
kyber_secretkeybytes = kyber_indcpa_secretkeybytes + kyber_indcpa_publickeybytes + 2 * kyber_symbytes
kyber_ciphertextbytes = kyber_indcpa_bytes

 #array.length(fst(res)) == kyber_publickeybytes
 #array.length(snd(res)) == kyber_secretkeybytes
@typechecked
def crypto_kem_keypair(keypaircoins:symbytes_t, coins:symbytes_t) -> tuple2 (vlbytes_t, vlbytes_t):
    sk = array.create(kyber_secretkeybytes, uint8(0))
    pk, sk1 = kyber_cpapke_keypair(keypaircoins)
    sk[0:kyber_indcpa_secretkeybytes] = sk1
    sk[kyber_indcpa_secretkeybytes:(kyber_indcpa_secretkeybytes + kyber_indcpa_publickeybytes)] = pk
    sk[(kyber_indcpa_secretkeybytes + kyber_indcpa_publickeybytes):(kyber_secretkeybytes - kyber_symbytes)] = sha3_256(kyber_publickeybytes, pk)
    sk[(kyber_secretkeybytes - kyber_symbytes):kyber_secretkeybytes] = coins
    return (pk, sk)

 #array.length(fst(res)) == kyber_ciphertextbytes
@typechecked
def crypto_kem_enc(pk:refine(vlbytes_t, lambda x: array.length(x) == kyber_publickeybytes),
                   msgcoins:symbytes_t) -> tuple2 (vlbytes_t, symbytes_t):
    buf = array.create(2 * kyber_symbytes, uint8(0))

    buf[0:kyber_symbytes] = sha3_256(kyber_symbytes, msgcoins)
    buf[kyber_symbytes:(2 * kyber_symbytes)] = sha3_256(kyber_publickeybytes, pk)

    kr = sha3_512(2 * kyber_symbytes, buf)
    ct = kyber_cpapke_encrypt(buf[0:kyber_symbytes], pk, kr[kyber_symbytes:(2*kyber_symbytes)])
    kr[kyber_symbytes:(2*kyber_symbytes)] = sha3_256(kyber_ciphertextbytes, ct)
    ss = sha3_256(2*kyber_symbytes, kr)
    return (ct, ss)

@typechecked
def crypto_kem_dec(ct:refine(vlbytes_t, lambda x: array.length(x) == kyber_ciphertextbytes),
                   sk:refine(vlbytes_t, lambda x: array.length(x) == kyber_secretkeybytes)) -> symbytes_t:
    buf = array.create(2 * kyber_symbytes, uint8(0))
    pk = sk[kyber_indcpa_secretkeybytes:(kyber_indcpa_secretkeybytes + kyber_indcpa_publickeybytes)]
    sk1 = sk[0:kyber_indcpa_secretkeybytes]
    buf[0:kyber_symbytes] = kyber_cpapke_decrypt(ct, sk1)
    buf[kyber_symbytes:(2 * kyber_symbytes)] = sk[(kyber_indcpa_secretkeybytes + kyber_indcpa_publickeybytes):(kyber_secretkeybytes - kyber_symbytes)]
    kr = sha3_512(2 * kyber_symbytes, buf)
    cmp1 = kyber_cpapke_encrypt( buf[0:kyber_symbytes], pk, kr[kyber_symbytes:(2 * kyber_symbytes)])
    kr[kyber_symbytes:(2 * kyber_symbytes)] = sha3_256(kyber_ciphertextbytes, ct)
    if (cmp1 == ct):
        kr[0:kyber_symbytes] = kr[0:kyber_symbytes]
    else:
        kr[0:kyber_symbytes] = sk[(kyber_secretkeybytes - kyber_symbytes):kyber_secretkeybytes]
    ss = sha3_256(2 * kyber_symbytes, kr)
    return ss
