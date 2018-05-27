#!/usr/bin/python3

# To run and check this file, you need Python 3 + mypy
# See install instructions at: http://mypy.readthedocs.io/en/latest/getting_started.html
# To typecheck this file: mypy kyber.py
# To run this file: python3 kyber.py

from lib.speclib import *
#from keccak import shake128, shake256, sha3_512, sha3_256, shake128_absorb, shake128_squeeze

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
    res = vector.create(kyber_n, zqelem_t(0))
    for i in range(kyber_n):
        i_new = reverse(uint8(i))
        res[i] = p[int(i_new)]
    return res

#TESTING NTT
# just for debugging
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
    return vector.map(zqpoly_invntt,r)
def zqpolyvec_bit_reverse(p:zqpolyvec_t):
    return vector.map(zqpoly_bit_reverse,p)


kyber_symbytes = 32
kyber_polycompressedbytes = 96
kyber_polybytes = 416

def kyber_polyveccompressedbytes(kyber_k:variant_k):
    return (kyber_k * 352)

def kyber_polyvecbytes(kyber_k:variant_k):
    return (kyber_k * kyber_polybytes)

def kyber_indcpa_publickeybytes(kyber_k:variant_k):
    return (kyber_polyveccompressedbytes(kyber_k) + kyber_symbytes)

def kyber_indcpa_secretkeybytes(kyber_k:variant_k):
    return kyber_polyvecbytes(kyber_k)

def kyber_indcpa_bytes(kyber_k:variant_k):
    return (kyber_polyveccompressedbytes(kyber_k) + kyber_polycompressedbytes)

symbytes_t = bytes_t(kyber_symbytes)

def decode(l:nat, b:bytes_t) -> zqpoly_t: 
    beta = bytes.to_uintn_le(b)
    res = vector.create(kyber_n, zqelem(0))
    for i in range(kyber_n):
        res[i] = zqelem(beta[i*l:(i+1)*l])
    return res

def encode(l:nat, p:zqpoly_t) -> bytes_t: 
    beta = uintn(0,256*l)
    for i in range(kyber_n):
        beta = uintn.set_bits(beta,i*l,(i+1)*l,p[i])
    return (bytes.from_uintn_le(beta))

def compress(x:zqelem_t, d:int) -> int:
    x = natmod.to_int(x)
    d2 = 2 ** d
    res = floor (d2 / kyber_q * x + 1 /2)
    return res % d2

def decompress(x:int, d:int) -> zqelem_t:
    d2 = 2 ** d
    res = floor (kyber_q / d2 * x + 1/2)
    return zqelem(res)

@typechecked
def msg_to_poly(m:symbytes_t) -> zqpoly_t:
    return vector.map(lambda x: decompress(x,1),decode(1,m))

@typechecked
def poly_to_msg(p:zqpoly_t) -> symbytes_t:
    return encode(1,vector.map(lambda x: compress(x,1),p))

# # def cbd(kyber_eta:variant_eta, buf:bytes_t) \
# #     -> contract(zqpoly_t,
# #                 lambda kyber_eta, buf: array.length(buf) == kyber_eta * kyber_n // 4,
# #                 lambda kyber_eta, buf, res: True):
# #     beta = bytesToBits(buf)
# #     res = array.create(kyber_n, zqelem(0))
# #     for i in range(kyber_n):
# #         a = nat(0)
# #         b = nat(0)
# #         for j in range(kyber_eta):
# #             a = a + bit.to_int(beta[2 * i * kyber_eta + j])
# #         for j in range(kyber_eta):
# #             b = b + bit.to_int(beta[2 * i * kyber_eta + kyber_eta + j])
# #         res[i] = zqsub(zqelem(a), zqelem(b))
# #     return res

# # #cbd(prf(seed, nonce)), prf = shake256
# # def poly_getnoise(kyber_eta:variant_eta, seed:symbytes_t, nonce:uint8_t) -> zqpoly_t:
# #     extseed = array.create(kyber_symbytes + 1, uint8(0))
# #     extseed[0:kyber_symbytes] = seed
# #     extseed[kyber_symbytes] = nonce
# #     buf = shake256(kyber_symbytes + 1, extseed, kyber_eta * kyber_n // 4)
# #     r = cbd(kyber_eta, buf)
# #     return r

# # def poly_tobytes (a:zqpoly_t) -> bytes_t(kyber_polybytes):
# #     res = array.create(kyber_polybytes, uint8(0))
# #     tmp = array.create(8, uint16(0))
# #     for i in range(kyber_n // 8):
# #         for j in range(8):
# #             tmp[j] = (a[8*i+j]) % kyber_q

# #         res[13*i+0] = uint8(tmp[0] & 0xff)
# #         res[13*i+1] = uint8((tmp[0] >> 8) | ((tmp[1] & 0x07) << 5))
# #         res[13*i+2] = uint8((tmp[1] >> 3) & 0xff)
# #         res[13*i+3] = uint8((tmp[1] >> 11) | ((tmp[2] & 0x3f) << 2))
# #         res[13*i+4] = uint8((tmp[2] >> 6) | ((tmp[3] & 0x01) << 7))
# #         res[13*i+5] = uint8((tmp[3] >> 1) & 0xff)
# #         res[13*i+6] = uint8((tmp[3] >> 9) | ((tmp[4] & 0x0f) << 4))
# #         res[13*i+7] = uint8((tmp[4] >> 4) & 0xff)
# #         res[13*i+8] = uint8((tmp[4] >> 12) | ((tmp[5] & 0x7f) << 1))
# #         res[13*i+9] = uint8((tmp[5] >> 7) | ((tmp[6] & 0x03) << 6))
# #         res[13*i+10] = uint8((tmp[6] >> 2) & 0xff)
# #         res[13*i+11] = uint8((tmp[6] >> 10) | ((tmp[7] & 0x1f) << 3))
# #         res[13*i+12] = uint8(tmp[7] >> 5)
# #     return res

# # def poly_frombytes (a:bytes_t(kyber_polybytes)) -> zqpoly_t:
# #     res = array.create(kyber_n, zqelem_t(0))

# #     for i in range(kyber_n // 8):
# #         res[8*i+0] = zqelem(int(uint16(a[13*i+0]) | ((uint16(a[13*i+1]) & uint16(0x1f)) << 8)))
# #         res[8*i+1] = zqelem(int((uint16(a[13*i+1]) >> 5) | (uint16(a[13*i+2]) << 3) | ((uint16(a[13*i+3]) & uint16(0x03)) << 11)))
# #         res[8*i+2] = zqelem(int((uint16(a[13*i+3]) >> 2) | ((uint16(a[13*i+4]) & uint16(0x7f)) << 6)))
# #         res[8*i+3] = zqelem(int((uint16(a[13*i+4]) >> 7) | (uint16(a[13*i+5]) << 1) | ((uint16(a[13*i+6]) & uint16(0x0f)) << 9)))
# #         res[8*i+4] = zqelem(int((uint16(a[13*i+6]) >> 4) | (uint16(a[13*i+7]) << 4) | ((uint16(a[13*i+8]) & uint16(0x01)) << 12)))
# #         res[8*i+5] = zqelem(int((uint16(a[13*i+8]) >> 1) | ((uint16(a[13*i+9]) & uint16(0x3f)) << 7)))
# #         res[8*i+6] = zqelem(int((uint16(a[13*i+9]) >> 6) | (uint16(a[13*i+10]) << 2) | ((uint16(a[13*i+11]) & uint16(0x07)) << 10)))
# #         res[8*i+7] = zqelem(int((uint16(a[13*i+11]) >> 3) | (uint16(a[13*i+12]) << 5)))
# #     return res

# # def poly_compress_vec(a:zqpoly_t) -> bytes_t(352):
# #     res = array.create(352, uint8(0))
# #     tmp = array.create(8, uint16(0))

# #     for j in range(kyber_n // 8):
# #         for k in range(8):
# #             tmp_k = (int(uint32((a[8*j+k]) % kyber_q) << 11) + kyber_q // 2) // kyber_q
# #             tmp[k] = tmp_k & 0x7ff

# #         res[11*j+0] = uint8(tmp[0] & 0xff)
# #         res[11*j+1] = uint8((tmp[0] >> 8) | ((tmp[1] & 0x1f) << 3))
# #         res[11*j+2] = uint8((tmp[1] >> 5) | ((tmp[2] & 0x03) << 6))
# #         res[11*j+3] = uint8((tmp[2] >> 2) & 0xff)
# #         res[11*j+4] = uint8((tmp[2] >> 10) | ((tmp[3] & 0x7f) << 1))
# #         res[11*j+5] = uint8((tmp[3] >> 7) | ((tmp[4] & 0x0f) << 4))
# #         res[11*j+6] = uint8((tmp[4] >> 4) | ((tmp[5] & 0x01) << 7))
# #         res[11*j+7] = uint8((tmp[5] >> 1) & 0xff)
# #         res[11*j+8] = uint8((tmp[5] >> 9) | ((tmp[6] & 0x3f) << 2))
# #         res[11*j+9] = uint8((tmp[6] >> 6) | ((tmp[7] & 0x07) << 5))
# #         res[11*j+10] = uint8(tmp[7] >> 3)
# #     return res

# # def poly_decompress_vec(a:bytes_t(352)) -> zqpoly_t:
# #     res = array.create(kyber_n, zqelem_t(0))

# #     for j in range(kyber_n // 8):
# #       res[8*j+0] = zqelem(int((((uint32(a[11*j+0]) | ((uint32(a[11*j+1]) & uint32(0x07)) << 8)) * uint32(kyber_q)) + uint32(1024)) >> 11))
# #       res[8*j+1] = zqelem(int(((((uint32(a[11*j+1]) >> 3) | ((uint32(a[11*j+2]) & uint32(0x3f)) << 5)) * uint32(kyber_q)) + uint32(1024)) >> 11))
# #       res[8*j+2] = zqelem(int(((((uint32(a[11*j+2]) >> 6) | ((uint32(a[11*j+3]) & uint32(0xff)) << 2) | ((uint32(a[11*j+4]) & uint32(0x01)) << 10)) * uint32(kyber_q)) + uint32(1024)) >> 11))
# #       res[8*j+3] = zqelem(int(((((uint32(a[11*j+4]) >> 1) | ((uint32(a[11*j+5]) & uint32(0x0f)) << 7)) * uint32(kyber_q)) + uint32(1024)) >> 11))
# #       res[8*j+4] = zqelem(int(((((uint32(a[11*j+5]) >> 4) | ((uint32(a[11*j+6]) & uint32(0x7f)) << 4)) * uint32(kyber_q)) + uint32(1024)) >> 11))
# #       res[8*j+5] = zqelem(int(((((uint32(a[11*j+6]) >> 7) | ((uint32(a[11*j+7]) & uint32(0xff)) << 1) | ((uint32(a[11*j+8]) & uint32(0x03)) <<  9)) * uint32(kyber_q)) + uint32(1024)) >> 11))
# #       res[8*j+6] = zqelem(int(((((uint32(a[11*j+8]) >> 2) | ((uint32(a[11*j+9]) & uint32(0x1f)) << 6)) * uint32(kyber_q)) + uint32(1024)) >> 11))
# #       res[8*j+7] = zqelem(int(((((uint32(a[11*j+9]) >> 5) | ((uint32(a[11*j+10]) & uint32(0xff)) << 3)) * uint32(kyber_q)) + uint32(1024)) >> 11))
# #     return res

# # def poly_compress(a:zqpoly_t) -> bytes_t(kyber_polycompressedbytes):
# #     res = array.create(kyber_polycompressedbytes, uint8(0))
# #     tmp = array.create(8, uint32(0))
# #     k = 0

# #     for i in range(kyber_n // 8):
# #         for j in range(8):
# #             tmp[j] = (((a[i*8+j] << 3) + kyber_q // 2) // kyber_q) & 7

# #         res[k] = uint8(tmp[0] | (tmp[1] << 3) | (tmp[2] << 6))
# #         res[k+1] = uint8((tmp[2] >> 2) | (tmp[3] << 1) | (tmp[4] << 4) | (tmp[5] << 7))
# #         res[k+2] = uint8((tmp[5] >> 1) | (tmp[6] << 2) | (tmp[7] << 5))
# #         k = k + 3
# #     return res

# # def poly_decompress(a:bytes_t(kyber_polycompressedbytes)) -> zqpoly_t:
# #     res = array.create(kyber_n, zqelem_t(0))
# #     k = 0

# #     for i in range(kyber_n // 8):
# #         res[8*i+0] = zqelem(int(((uint16(a[k+0]) & uint16(7)) * uint16(kyber_q)) + uint16(4)) >> 3)
# #         res[8*i+1] = zqelem(int((((uint16(a[k+0]) >> 3) & uint16(7)) * uint16(kyber_q)) + uint16(4)) >> 3)
# #         res[8*i+2] = zqelem(int((((uint16(a[k+0]) >> 6) | ((uint16(a[k+1]) << 2) & uint16(4))) * uint16(kyber_q)) + uint16(4)) >> 3)
# #         res[8*i+3] = zqelem(int((((uint16(a[k+1]) >> 1) & uint16(7)) * uint16(kyber_q)) + uint16(4)) >> 3)
# #         res[8*i+4] = zqelem(int((((uint16(a[k+1]) >> 4) & uint16(7)) * uint16(kyber_q)) + uint16(4)) >> 3)
# #         res[8*i+5] = zqelem(int((((uint16(a[k+1]) >> 7) | ((uint16(a[k+2]) << 1) & uint16(6))) * uint16(kyber_q)) + uint16(4)) >> 3)
# #         res[8*i+6] = zqelem(int((((uint16(a[k+2]) >> 2) & uint16(7)) * uint16(kyber_q)) + uint16(4)) >> 3)
# #         res[8*i+7] = zqelem(int((((uint16(a[k+2]) >> 5)) * uint16(kyber_q)) + uint16(4)) >> 3)
# #         k = k + 3
# #     return res

# # def polyvec_tobytes(kyber_k:variant_k, a:zqpolyvec_t) \
# #     -> contract(bytes_t,
# #                 lambda kyber_k, a: array.length(a) == kyber_k,
# #                 lambda kyber_k, a, res: array.length(res) == kyber_polyvecbytes(kyber_k)):
# #     res = array.create(kyber_polyvecbytes(kyber_k), uint8(0))

# #     for i in range(kyber_k):
# #         res[i*kyber_polybytes:(i+1)*kyber_polybytes] = poly_tobytes(a[i])
# #     return res

# # def polyvec_frombytes(kyber_k:variant_k, a:bytes_t) \
# #     -> contract(zqpolyvec_t,
# #                 lambda kyber_k, a: array.length(a) == kyber_polyvecbytes(kyber_k),
# #                 lambda kyber_k, a, res: array.length(res) == kyber_k):
# #     res = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))

# #     for i in range(kyber_k):
# #         res[i] = poly_frombytes(a[i*kyber_polybytes:(i+1)*kyber_polybytes])
# #     return res

# # def polyvec_compress(kyber_k:variant_k, a:zqpolyvec_t) \
# #     -> contract(bytes_t,
# #                 lambda kyber_k, a: array.length(a) == kyber_k,
# #                 lambda kyber_k, a, res: array.length(res) == kyber_polyveccompressedbytes(kyber_k)):
# #     res = array.create(kyber_polyveccompressedbytes(kyber_k), uint8(0))

# #     for i in range(kyber_k):
# #         res[i*352:(i+1)*352] = poly_compress_vec(a[i])
# #     return res

# # def polyvec_decompress(kyber_k:variant_k, a:bytes_t) \
# #     -> contract(zqpolyvec_t,
# #                 lambda kyber_k, a: array.length(a) == kyber_polyveccompressedbytes(kyber_k),
# #                 lambda kyber_k, a, res: array.length(res) == kyber_k):
# #     res = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))

# #     for i in range(kyber_k):
# #         res[i] = poly_decompress_vec(a[i*352:(i+1)*352])
# #     return res

# # def pack_sk(kyber_k:variant_k, sk:zqpolyvec_t) \
# #     -> contract(bytes_t,
# #                 lambda kyber_k, sk: array.length(sk) == kyber_k,
# #                 lambda kyber_k, sk, res: array.length(res) == kyber_indcpa_secretkeybytes(kyber_k)):
# #     return polyvec_tobytes(kyber_k, sk)

# # def unpack_sk(kyber_k:variant_k, packedsk:bytes_t) \
# #     -> contract(zqpolyvec_t,
# #                 lambda kyber_k, packedsk: array.length(packedsk) == kyber_indcpa_secretkeybytes(kyber_k),
# #                 lambda kyber_k, packedsk, res: array.length(res) == kyber_k):
# #     return polyvec_frombytes(kyber_k, packedsk)

# # def pack_pk(kyber_k:variant_k, pk:zqpolyvec_t, seed:symbytes_t) \
# #     -> contract(bytes_t,
# #                 lambda kyber_k, pk: array.length(pk) == kyber_k,
# #                 lambda kyber_k, pk, res: array.length(res) == kyber_indcpa_publickeybytes(kyber_k)):
# #     res = array.create(kyber_indcpa_publickeybytes(kyber_k), uint8(0))
# #     res[0:kyber_polyveccompressedbytes(kyber_k)] = polyvec_compress(kyber_k, pk)
# #     res[kyber_polyveccompressedbytes(kyber_k):kyber_indcpa_publickeybytes(kyber_k)] = seed
# #     return res

# # def unpack_pk(kyber_k:variant_k, packedpk:bytes_t) \
# #     -> contract((zqpolyvec_t, symbytes_t),
# #                 lambda kyber_k, packedpk: array.length(packedpk) == kyber_indcpa_publickeybytes(kyber_k),
# #                 lambda kyber_k, packedpk, res: True): # array.length(fst(res)) == kyber_k
# #     pk = polyvec_decompress(kyber_k, packedpk[0:kyber_polyveccompressedbytes(kyber_k)])
# #     seed = packedpk[kyber_polyveccompressedbytes(kyber_k):kyber_indcpa_publickeybytes(kyber_k)]
# #     return (pk, seed)

# # def pack_ciphertext(kyber_k:variant_k, b:zqpolyvec_t, v:zqpoly_t) \
# #     -> contract(bytes_t,
# #                 lambda kyber_k, b, v: array.length(b) == kyber_k,
# #                 lambda kyber_k, b, v, res: array.length(res) == kyber_indcpa_bytes(kyber_k)):
# #     res = array.create(kyber_indcpa_bytes(kyber_k), uint8(0))
# #     res[0:kyber_polyveccompressedbytes(kyber_k)] = polyvec_compress(kyber_k, b)
# #     res[kyber_polyveccompressedbytes(kyber_k):kyber_indcpa_bytes(kyber_k)] = poly_compress(v)
# #     return res

# # def unpack_ciphertext(kyber_k:variant_k, c:bytes_t) \
# #     -> contract((zqpolyvec_t, zqpoly_t),
# #                 lambda kyber_k, c: array.length(c) == kyber_indcpa_bytes(kyber_k),
# #                 lambda kyber_k, c, res: True): # array.length(fst(res)) == kyber_k
# #     u = polyvec_decompress(kyber_k, c[0:kyber_polyveccompressedbytes(kyber_k)])
# #     v = poly_decompress(c[kyber_polyveccompressedbytes(kyber_k):kyber_indcpa_bytes(kyber_k)])
# #     return (u, v)

# # #parse(xof(p || a || b)), xof = shake128
# # def genAij(seed:symbytes_t, a:uint8_t, b:uint8_t) -> zqpoly_t:
# #     shake128_rate = 168
# #     res = array.create(kyber_n, zqelem(0))

# #     extseed = array.create(kyber_symbytes + 2, uint8(0))
# #     extseed[0:kyber_symbytes] = seed
# #     extseed[kyber_symbytes] = a
# #     extseed[kyber_symbytes + 1] = b

# #     maxnblocks = 4
# #     nblocks = maxnblocks
# #     state = shake128_absorb(kyber_symbytes + 2, extseed)
# #     buf = shake128_squeeze(state, shake128_rate * nblocks)

# #     i = 0
# #     j = 0
# #     while (j < kyber_n):
# #         d = uint16(buf[i]) | (uint16(buf[i + 1]) << 8)
# #         d = int(d & uint16(0x1fff))
# #         if (d < kyber_q):
# #             res[j] = zqelem(d)
# #             j = j + 1
# #         i = i + 2
# #         if (i > shake128_rate * nblocks - 2):
# #             nblocks = 1
# #             buf = shake128_squeeze(state, shake128_rate * nblocks)
# #             i = 0
# #     return res

# # def kyber_cpapke_keypair(kyber_k:variant_k, kyber_eta:variant_eta, coins:symbytes_t) \
# #     -> contract((bytes_t, bytes_t),
# #                 lambda kyber_k, kyber_eta, coins: True,
# #                 lambda kyber_k, kyber_eta, coins, res: True): # array.length(fst(res)) == kyber_indcpa_publickeybytes(kyber_k) and array.length(snd(res)) == kyber_indcpa_secretkeybytes(kyber_k)
# #     rhosigma = sha3_512(kyber_symbytes, coins)
# #     rho = rhosigma[0:kyber_symbytes]
# #     sigma = rhosigma[kyber_symbytes:(2*kyber_symbytes)]

# #     n = uint8(0)
# #     s = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))
# #     e = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))
# #     that = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))
# #     A = array.create(kyber_k, array.create(kyber_k, array.create(kyber_n, zqelem_t(0))))

# #     for i in range(kyber_k):
# #         A[i] = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))
# #         for j in range(kyber_k):
# #             A[i][j] = array.create(kyber_n, zqelem_t(0))

# #     for i in range(kyber_k):
# #         for j in range(kyber_k):
# #             A[i][j] = genAij(rho, uint8(j), uint8(i))

# #     for i in range(kyber_k):
# #         s[i] = poly_getnoise(kyber_eta, sigma, n)
# #         n += uint8(1)

# #     for i in range(kyber_k):
# #         e[i] = poly_getnoise(kyber_eta, sigma, n)
# #         n += uint8(1)

# #     shat = zqpolyvec_bit_reverse(kyber_k, zqpolyvec_ntt(kyber_k, s))

# #     # that = A * shat
# #     for i in range(kyber_k):
# #         for j in range(kyber_k):
# #             that[i] = zqpoly_add(that[i], zqpoly_pointwise_mul(A[i][j], shat[j]))

# #     t = zqpolyvec_invntt(kyber_k, zqpolyvec_bit_reverse(kyber_k, that))
# #     t = zqpolyvec_add(kyber_k, t, e)

# #     sk = pack_sk(kyber_k, shat)
# #     pk = pack_pk(kyber_k, t, rho)

# #     return (pk, sk)

# # def kyber_cpapke_encrypt(kyber_k:variant_k, kyber_eta:variant_eta, m:symbytes_t, packedpk:bytes_t, coins:symbytes_t) \
# #     -> contract(bytes_t,
# #                 lambda kyber_k, kyber_eta, m, packedpk, coins: array.length(packedpk) == kyber_indcpa_publickeybytes(kyber_k),
# #                 lambda kyber_k, kyber_eta, m, packedpk, coins, res: array.length(res) == kyber_indcpa_bytes(kyber_k)):
# #     n = uint8(0)
# #     r = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))
# #     e1 = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))
# #     uhat = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))
# #     vhat = array.create(kyber_n, zqelem(0))
# #     At = array.create(kyber_k, array.create(kyber_k, array.create(kyber_n, zqelem_t(0))))

# #     t, rho = unpack_pk(kyber_k, packedpk)

# #     for i in range(kyber_k):
# #         At[i] = array.create(kyber_k, array.create(kyber_n, zqelem_t(0)))
# #         for j in range(kyber_k):
# #             At[i][j] = array.create(kyber_n, zqelem_t(0))

# #     for i in range(kyber_k):
# #         for j in range(kyber_k):
# #             At[i][j] = genAij(rho, uint8(i), uint8(j))

# #     for i in range(kyber_k):
# #         r[i] = poly_getnoise(kyber_eta, coins, n)
# #         n += uint8(1)

# #     for i in range(kyber_k):
# #         e1[i] = poly_getnoise(kyber_eta, coins, n)
# #         n += uint8(1)

# #     e2 = poly_getnoise(kyber_eta, coins, n)

# #     rhat = zqpolyvec_bit_reverse(kyber_k, zqpolyvec_ntt(kyber_k, r))

# #     for i in range(kyber_k):
# #         for j in range(kyber_k):
# #             uhat[i] = zqpoly_add(uhat[i], zqpoly_pointwise_mul(At[i][j], rhat[j]))

# #     u = zqpolyvec_invntt(kyber_k, zqpolyvec_bit_reverse(kyber_k, uhat))
# #     u = zqpolyvec_add(kyber_k, u, e1)

# #     that = zqpolyvec_bit_reverse(kyber_k, zqpolyvec_ntt(kyber_k, t))

# #     for i in range(kyber_k):
# #         vhat = zqpoly_add(vhat, zqpoly_pointwise_mul(that[i], rhat[i]))

# #     v = zqpoly_invntt(bit_reversed_poly(vhat))
# #     v = zqpoly_add(zqpoly_add(v, e2), msg_topoly(m))
# #     c = pack_ciphertext(kyber_k, u, v)

# #     return c

# # def kyber_cpapke_decrypt(kyber_k:variant_k, kyber_eta:variant_eta, c:bytes_t, sk:bytes_t) \
# #     -> contract(symbytes_t,
# #                 lambda kyber_k, kyber_eta, c, sk: array.length(c) == kyber_indcpa_bytes(kyber_k) and array.length(sk) == kyber_indcpa_secretkeybytes(kyber_k),
# #                 lambda kyber_k, kyber_eta, c, sk, res: True):
# #     dhat = array.create(kyber_n, zqelem(0))

# #     u, v = unpack_ciphertext(kyber_k, c)
# #     s = unpack_sk(kyber_k, sk)

# #     uhat = zqpolyvec_bit_reverse(kyber_k, zqpolyvec_ntt(kyber_k, u))

# #     for i in range(kyber_k):
# #         dhat = zqpoly_add(dhat, zqpoly_pointwise_mul(s[i], uhat[i]))

# #     d = zqpoly_invntt(bit_reversed_poly(dhat))
# #     d = zqpoly_sub(v, d)
# #     msg = poly_tomsg(d)

# #     return msg

# # #KyberKEM
# # def kyber_publickeybytes(kyber_k:variant_k):
# #     return kyber_indcpa_publickeybytes(kyber_k)

# # def kyber_secretkeybytes(kyber_k:variant_k):
# #     return (kyber_indcpa_secretkeybytes(kyber_k) + kyber_indcpa_publickeybytes(kyber_k) + 2 * kyber_symbytes)

# # def kyber_ciphertextbytes(kyber_k:variant_k):
# #     return kyber_indcpa_bytes(kyber_k)

# # def crypto_kem_keypair(kyber_k:variant_k, kyber_eta:variant_eta, keypaircoins:symbytes_t, coins:symbytes_t) \
# #     -> contract((bytes_t, bytes_t),
# #                 lambda kyber_k, kyber_eta, keypaircoins, coins: True,
# #                 lambda kyber_k, kyber_eta, keypaircoins, coins, res: True): #array.length(fst(res)) == kyber_publickeybytes(kyber_k) and array.length(snd(res)) == kyber_secretkeybytes(kyber_k)
# #     sk = array.create(kyber_secretkeybytes(kyber_k), uint8(0))
# #     pk, sk1 = kyber_cpapke_keypair(kyber_k, kyber_eta, keypaircoins)
# #     sk[0:kyber_indcpa_secretkeybytes(kyber_k)] = sk1
# #     sk[kyber_indcpa_secretkeybytes(kyber_k):(kyber_indcpa_secretkeybytes(kyber_k) + kyber_indcpa_publickeybytes(kyber_k))] = pk
# #     sk[(kyber_indcpa_secretkeybytes(kyber_k) + kyber_indcpa_publickeybytes(kyber_k)):(kyber_secretkeybytes(kyber_k) - kyber_symbytes)] = sha3_256(kyber_publickeybytes(kyber_k), pk)
# #     sk[(kyber_secretkeybytes(kyber_k) - kyber_symbytes):kyber_secretkeybytes(kyber_k)] = coins
# #     return (pk, sk)

# # def crypto_kem_enc(kyber_k:variant_k, kyber_eta:variant_eta, pk:bytes_t, msgcoins:symbytes_t) \
# #     -> contract((bytes_t, symbytes_t),
# #                 lambda kyber_k, kyber_eta, pk, msgcoins: array.length(pk) == kyber_publickeybytes(kyber_k),
# #                 lambda kyber_k, kyber_eta, pk, msgcoins, res: True): #array.length(fst(res)) == kyber_ciphertextbytes(kyber_k)
# #     buf = array.create(2 * kyber_symbytes, uint8(0))

# #     buf[0:kyber_symbytes] = sha3_256(kyber_symbytes, msgcoins)
# #     buf[kyber_symbytes:(2 * kyber_symbytes)] = sha3_256(kyber_publickeybytes(kyber_k), pk)

# #     kr = sha3_512(2 * kyber_symbytes, buf)
# #     ct = kyber_cpapke_encrypt(kyber_k, kyber_eta, buf[0:kyber_symbytes], pk, kr[kyber_symbytes:(2*kyber_symbytes)])
# #     kr[kyber_symbytes:(2*kyber_symbytes)] = sha3_256(kyber_ciphertextbytes(kyber_k), ct)
# #     ss = sha3_256(2*kyber_symbytes, kr)
# #     return (ct, ss)

# # def crypto_kem_dec(kyber_k:variant_k, kyber_eta:variant_eta, ct:bytes_t, sk:bytes_t(kyber_secretkeybytes)) \
# #     -> contract(symbytes_t,
# #                 lambda kyber_k, kyber_eta, ct, sk: array.length(ct) == kyber_ciphertextbytes(kyber_k) and array.length(sk) == kyber_secretkeybytes(kyber_k),
# #                 lambda kyber_k, kyber_eta, ct, sk, res: True):
# #     buf = array.create(2 * kyber_symbytes, uint8(0))
# #     pk = sk[kyber_indcpa_secretkeybytes(kyber_k):(kyber_indcpa_secretkeybytes(kyber_k) + kyber_indcpa_publickeybytes(kyber_k))]
# #     sk1 = sk[0:kyber_indcpa_secretkeybytes(kyber_k)]
# #     buf[0:kyber_symbytes] = kyber_cpapke_decrypt(kyber_k, kyber_eta, ct, sk1)
# #     buf[kyber_symbytes:(2 * kyber_symbytes)] = sk[(kyber_indcpa_secretkeybytes(kyber_k) + kyber_indcpa_publickeybytes(kyber_k)):(kyber_secretkeybytes(kyber_k) - kyber_symbytes)]
# #     kr = sha3_512(2 * kyber_symbytes, buf)
# #     cmp1 = kyber_cpapke_encrypt(kyber_k, kyber_eta, buf[0:kyber_symbytes], pk, kr[kyber_symbytes:(2 * kyber_symbytes)])
# #     kr[kyber_symbytes:(2 * kyber_symbytes)] = sha3_256(kyber_ciphertextbytes(kyber_k), ct)
# #     if (cmp1 == ct):
# #         kr[0:kyber_symbytes] = kr[0:kyber_symbytes]
# #     else:
# #         kr[0:kyber_symbytes] = sk[(kyber_secretkeybytes(kyber_k) - kyber_symbytes):kyber_secretkeybytes(kyber_k)]
# #     ss = sha3_256(2 * kyber_symbytes, kr)
# #     return ss
