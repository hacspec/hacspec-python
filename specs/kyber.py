#!/usr/bin/python3
from lib.speclib import *
from specs.keccak import *
from math import floor

variant_k   = refine(nat_t, lambda x: x == 2 or x == 3 or x == 4)
variant_eta = refine(nat_t, lambda x: x == 5 or x == 4 or x == 3)

kyber_q   = 7681
kyber_n   =  256
kyber_dt  =   11
kyber_du  =   11
kyber_dv  =    3

kyber_polycompressedbytes = 96
kyber_polybytes = 416
kyber_symbytes = 32
kyber_polyveccompressedbytes = lambda kyber_k: kyber_k * 352
kyber_polyvecbytes = lambda kyber_k: kyber_k * kyber_polybytes
kyber_indcpa_publickeybytes = lambda kyber_k: kyber_polyveccompressedbytes(kyber_k) + kyber_symbytes
kyber_indcpa_secretkeybytes = kyber_polyvecbytes
kyber_indcpa_bytes = lambda kyber_k: kyber_polyveccompressedbytes(kyber_k) + kyber_polycompressedbytes
kyber_publickeybytes = kyber_indcpa_publickeybytes
kyber_secretkeybytes = lambda kyber_k: kyber_indcpa_secretkeybytes(kyber_k) + kyber_indcpa_publickeybytes(kyber_k) + 2 * kyber_symbytes
kyber_ciphertextbytes = kyber_indcpa_bytes

symbytes_t = bytes_t(kyber_symbytes)
def kyber_publickey_t(kyber_k:variant_k):
    return bytes_t(kyber_publickeybytes(kyber_k))
def kyber_secretkey_t(kyber_k:variant_k):
    return bytes_t(kyber_secretkeybytes(kyber_k))
def kyber_ciphertext_t(kyber_k:variant_k):
    return bytes_t(kyber_ciphertextbytes(kyber_k))
    
def Kyber(kyber_k:variant_k,kyber_eta:variant_eta):
    zqelem_t = natmod_t(kyber_q)
    def zqelem(n:nat):
        return natmod(n,kyber_q)
    zqpoly_t    = vector_t(zqelem_t,kyber_n)
    zqpolyvec_t = vector_t(zqpoly_t,kyber_k)
    zqpolymatrix_t = vector_t(zqpolyvec_t,kyber_k)

    zqpoly0   = vector.create(kyber_n,zqelem(0))
    omega     = zqelem(3844)
    psi       = zqelem(62)
    n_inv     = zqelem(7651)
    psi_inv   = zqelem(1115)
    omega_inv = zqelem(6584)

    def zqpoly_mul(p:zqpoly_t, q:zqpoly_t) -> zqpoly_t:
        s = vector.poly_mul(p,q,zqelem(0))
        low,high = vector.split(s,kyber_n)
        r = low - high
        return r

    def zqpolyvec_dot(p:zqpolyvec_t, q:zqpolyvec_t) -> zqpoly_t:
        t = vector.create(kyber_n, zqelem(0))
        for i in range(kyber_k):
            t += zqpoly_mul(p[i], q[i])
        return(t)

    def zqpolymatrix_dot(p:zqpolymatrix_t, q:zqpolyvec_t) -> zqpolyvec_t:
        t = vector.create(kyber_k, vector.create(kyber_n, zqelem(0)))
        for i in range(kyber_k):
            t[i] = zqpolyvec_dot(p[i],q)
        return(t)

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
            return vector.map(decompress(d), decode(d)(b))
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
    def pack_sk(sk:zqpolyvec_t) -> bytes_t(kyber_indcpa_secretkeybytes(kyber_k)):
        #encode_13(sk mod+ q)
        return bytes.concat_blocks(vector.map(lambda x:encode(13)(x), sk), vector.empty())

    @typechecked
    def unpack_sk(packedsk:bytes_t(kyber_indcpa_secretkeybytes(kyber_k))) -> zqpolyvec_t:
        #decode_13(sk)
        res, last = bytes.split_blocks(packedsk, kyber_polybytes)
        res = vector.map(lambda x: decode(13)(x), res)
        return res

    @typechecked
    def pack_pk(pk:zqpolyvec_t, seed:symbytes_t) -> bytes_t(kyber_indcpa_publickeybytes(kyber_k)):
        #(encode_dt(compress_q(t, dt)) || seed)
        return bytes.concat_blocks(vector.map(compress_encode(kyber_dt), pk), seed)

    @typechecked
    def unpack_pk(packedpk:bytes_t(kyber_indcpa_publickeybytes(kyber_k))) -> tuple2 (zqpolyvec_t, symbytes_t):
        #decompress_q(decode_dt(pk), dt)
        res, seed = bytes.split_blocks(packedpk, 352)
        pk = vector.map(decode_decompress(kyber_dt), res)
        return (pk, seed)

    @typechecked
    def pack_ciphertext(b:zqpolyvec_t, v:zqpoly_t) -> bytes_t(kyber_indcpa_bytes(kyber_k)):
        #(encode_du(compress_q(b, du)) || encode_dv(compress_q(v, dv)))
        return bytes.concat_blocks(vector.map(compress_encode(kyber_du), b), compress_encode(kyber_dv)(v))

    @typechecked
    def unpack_ciphertext(c:bytes_t(kyber_indcpa_bytes(kyber_k))) -> tuple2 (zqpolyvec_t, zqpoly_t):
        #(decompress_q(decode_du(c), du), decompress_q(decode_dv(c_v), dv))
        u1, v1 = bytes.split_blocks(c, 352)
        u = vector.map(decode_decompress(kyber_du), u1)
        v = decode_decompress(kyber_dv)(v1)
        return (u, v)

    @typechecked
    def cbd(buf:bytes_t(kyber_eta * kyber_n // 4)) -> zqpoly_t:
        beta = bytes.to_uintn_le(buf)
        res = vector.create(kyber_n, zqelem(0))
        for i in range(kyber_n):
            a = uintn.bit_count(beta[2 * i * kyber_eta: (2 * i + 1) * kyber_eta])
            b = uintn.bit_count(beta[(2 * i + 1) * kyber_eta:(2 * i + 2) * kyber_eta])
            res[i] = zqelem(a - b)
        return res

    #cbd(prf(seed, nonce)), prf = shake256
    @typechecked
    def zqpoly_getnoise(seed:symbytes_t) -> Callable[[int],zqpoly_t]:
        def _getnoise(nonce:int) -> zqpoly_t:
            extseed = bytes.concat(seed, bytes.singleton(uint8(nonce)))
            buf = shake256(kyber_symbytes + 1, extseed, kyber_eta * kyber_n // 4)
            return cbd(buf)
        return _getnoise

    @typechecked
    def shake128_absorb(inputByteLen:size_nat_t,
                        input_b:vlbytes_t) -> state_t:
        s = array.create(25, uint64(0))
        return absorb(s,168, inputByteLen, input_b, uint8(0x1F))

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

    def genAij(seed:symbytes_t) -> Callable[[int,int],zqpoly_t]:
        def zqpoly_invntt(p:zqpoly_t) -> zqpoly_t:
            np = vector.create(kyber_n, zqelem(0))
            for i in range(kyber_n):
                for j in range(kyber_n):
                    np[i] += (p[j] * (omega_inv ** (i * j)))
                np[i] *= n_inv * (psi_inv ** i)
            return np

        def zqpoly_bit_reverse(p:zqpoly_t) -> zqpoly_t:
            return vector.createi(kyber_n, zqelem(0), lambda i: p[int(uintn.reverse(uint8(i)))])

        def _genAij(a:uint8_t, b:uint8_t) -> zqpoly_t:
            return zqpoly_invntt(zqpoly_bit_reverse(genAij_hat(seed, uint8(a), uint8(b))))
        return _genAij

    @typechecked
    def kyber_cpapke_keypair(coins:symbytes_t) -> \
        tuple2 (bytes_t(kyber_indcpa_publickeybytes(kyber_k)), bytes_t(kyber_indcpa_secretkeybytes(kyber_k))):
        rhosigma = sha3_512(kyber_symbytes, coins)
        rho,sigma = bytes.split(rhosigma,kyber_symbytes)

        A = matrix.createi(kyber_k, kyber_k, lambda i,j: genAij(rho)(j,i))
        s = vector.createi(kyber_k, zqpoly0, zqpoly_getnoise(sigma))
        e = vector.createi(kyber_k, zqpoly0, lambda i: zqpoly_getnoise(sigma)(kyber_k + i))
        t = zqpolymatrix_dot(A,s) + e
        sk = pack_sk(s)
        pk = pack_pk(t, rho)
        return (pk, sk)

    @typechecked
    def kyber_cpapke_encrypt(m:symbytes_t,
                             packedpk:bytes_t(kyber_indcpa_publickeybytes(kyber_k)),
                             coins:symbytes_t) -> \
                             bytes_t(kyber_indcpa_bytes(kyber_k)):
        t, rho = unpack_pk(packedpk)
        At = matrix.createi(kyber_k, kyber_k, genAij(rho))
        r  = vector.createi(kyber_k, zqpoly0, zqpoly_getnoise(coins))
        e1 = vector.createi(kyber_k, zqpoly0, lambda i: zqpoly_getnoise(coins)(kyber_k+i))
        e2 = zqpoly_getnoise(coins)(kyber_k + kyber_k)
        u = zqpolymatrix_dot(At,r) + e1
        v = zqpolyvec_dot(t,r) + e2 + msg_to_poly(m)
        c = pack_ciphertext(u, v)
        return c

    @typechecked
    def kyber_cpapke_decrypt(c:bytes_t(kyber_indcpa_bytes(kyber_k)),
                             sk:bytes_t(kyber_indcpa_secretkeybytes(kyber_k))) -> symbytes_t:
        u, v = unpack_ciphertext(c)
        s = unpack_sk(sk)
        d = zqpolyvec_dot(s,u)
        d = v - d
        msg = poly_to_msg(d)
        return msg


    @typechecked
    def crypto_kem_keypair(keypaircoins:symbytes_t, coins:symbytes_t) -> \
                           tuple2 (kyber_publickey_t(kyber_k), kyber_secretkey_t(kyber_k)):
        pk, sk1 = kyber_cpapke_keypair(keypaircoins)
        sk = bytes.concat(sk1, bytes.concat(pk, bytes.concat(sha3_256(kyber_publickeybytes(kyber_k), pk), coins)))
        return (pk, sk)

    @typechecked
    def crypto_kem_enc(pk:kyber_publickey_t(kyber_k),msgcoins:symbytes_t) -> \
                       tuple2 (kyber_ciphertext_t(kyber_k), symbytes_t):
        buf = bytes.concat(sha3_256(kyber_symbytes, msgcoins),
                           sha3_256(kyber_publickeybytes(kyber_k), pk))
        kr = sha3_512(2 * kyber_symbytes, buf)
        ct = kyber_cpapke_encrypt(buf[0:kyber_symbytes], pk, kr[kyber_symbytes:(2*kyber_symbytes)])
        kr[kyber_symbytes:(2*kyber_symbytes)] = sha3_256(kyber_ciphertextbytes(kyber_k), ct)
        ss = sha3_256(2*kyber_symbytes, kr)
        return (ct, ss)

    @typechecked
    def crypto_kem_dec(ct:kyber_ciphertext_t(kyber_k), sk:kyber_secretkey_t(kyber_k)) -> \
                       symbytes_t:
        sk1,x = bytes.split(sk,kyber_indcpa_secretkeybytes(kyber_k))
        pk,x = bytes.split(x,kyber_indcpa_publickeybytes(kyber_k))
        sk2,kr_ = bytes.split(x,kyber_symbytes)
        buf = bytes.concat(kyber_cpapke_decrypt(ct, sk1), sk2)
        kr = sha3_512(2 * kyber_symbytes, buf)
        cmp1 = kyber_cpapke_encrypt(buf[0:kyber_symbytes], pk, kr[kyber_symbytes:(2 * kyber_symbytes)])
        kr[kyber_symbytes:(2 * kyber_symbytes)] = sha3_256(kyber_ciphertextbytes(kyber_k), ct)
        if (cmp1 != ct):
            kr[0:kyber_symbytes] = kr_
        ss = sha3_256(2 * kyber_symbytes, kr)
        return ss

    return (crypto_kem_keypair,crypto_kem_enc,crypto_kem_dec)
