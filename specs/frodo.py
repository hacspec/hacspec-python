from lib.speclib import *
from specs.sha3 import *
from math import floor
from specs.aes import aes128_encrypt_block

variant_gen_t = refine(str, lambda x: x == 'AES128' or x == 'CSHAKE128')
variant_frodo_kem_t = refine(str, lambda x: x == 'FrodoKEM-640' or x == 'FrodoKEM-976')

@typechecked
def cshake128_frodo(input_b:bytes_t, cstm:uint16_t, outputByteLen:nat) -> \
    refine(vlbytes_t, lambda x: array.length(x) == outputByteLen):
    inputByteLen = array.length(input_b)
    s = array.create(25, uint64(0))
    s[0] = uint64(0x10010001a801) | (uint64(cstm) << 48)
    s = state_permute(s)

    s = absorb(s, 168, inputByteLen, input_b, uint8(0x04))
    output = squeeze(s, 168, outputByteLen)
    return output

@typechecked
def cshake256_frodo(input_b:bytes_t, cstm:uint16_t, outputByteLen:nat) -> \
    refine(vlbytes_t, lambda x: array.length(x) == outputByteLen):
    inputByteLen = array.length(input_b)
    s = array.create(25, uint64(0))
    s[0] = uint64(0x100100018801) | (uint64(cstm) << 48)
    s = state_permute(s)

    s = absorb(s, 136, inputByteLen, input_b, uint8(0x04))
    output = squeeze(s, 136, outputByteLen)
    return output

@typechecked
def Frodo(frodo_kem:variant_frodo_kem_t, gen_a:variant_gen_t):
    if (frodo_kem == 'FrodoKEM-640'):
        params_n = 640
        params_logq = 15
        params_extracted_bits = 2
        crypto_bytes = 16
        cdf_table_len = 12
        cdf_table = array([4727, 13584, 20864, 26113, 29434, 31278, 32176, 32560, 32704, 32751, 32764, 32767])
        cshake_frodo = cshake128_frodo
    else:
        params_n = 976
        params_logq = 16
        params_extracted_bits = 3
        crypto_bytes = 24
        cdf_table_len = 11
        cdf_table = array([5638, 15915, 23689, 28571, 31116, 32217, 32613, 32731, 32760, 32766, 32767])
        cshake_frodo = cshake256_frodo

    bytes_seed_a = 16
    params_nbar = 8
    params_q = 2 ** params_logq
    bytes_mu = (params_extracted_bits * params_nbar * params_nbar) // 8
    crypro_publickeybytes  = bytes_seed_a + (params_logq * params_n * params_nbar) // 8
    crypto_secretkeybytes  = crypto_bytes + crypro_publickeybytes  #+2 * params_n * params_nbar
    crypto_ciphertextbytes = ((params_nbar * params_n + params_nbar * params_nbar) * params_logq) // 8 + crypto_bytes

    zqelem_t = natmod_t(params_q)
    
    @typechecked
    def zqelem(n:nat):
        return natmod(n, params_q)

    zqmatrix_t = [[zqelem_t]]
    # def zqmatrix_t(n:nat, m:nat):
    #return matrix_t(zqelem_t, n, m)


    @typechecked
    def frodo_key_encode(a:bytes_t, b:nat) -> zqmatrix_t:
        a = bytes.to_uintn_le(a)
        res = matrix.create(params_nbar, params_nbar, zqelem(0))
        for i in range(params_nbar):
            for j in range(params_nbar):
                k = uintn.to_int(a[(i*params_nbar+j)*b:(i*params_nbar+j+1)*b])
                res[i][j] = zqelem(k * (params_q // (2 ** b)))
        return res

    @typechecked
    def frodo_key_decode(a:zqmatrix_t, b:nat) -> bytes_t:
        res = uintn(0, params_nbar*params_nbar*b)
        for i in range(params_nbar):
            for j in range(params_nbar):
                k = floor(natmod.to_int(a[i][j]) * (2 ** b) / params_q + 1/2)
                res = uintn.set_bits(res,(i*params_nbar+j)*b,(i*params_nbar+j+1)*b, uintn(k, b))
        return bytes.from_uintn_le(res)

    @typechecked
    def frodo_pack(n1:nat, n2:nat, a:zqmatrix_t, d:nat) -> bytes_t:
        res = uintn(0, n1*n2*d)
        for i in range(n1):
            for j in range(n2):
                res = uintn.set_bits(res,(i*n2+j)*d,(i*n2+j+1)*d, uintn.reverse(uintn(a[i][j], d)))
        return bytes.from_uintn_be(uintn.reverse(res))

    @typechecked
    def frodo_unpack(n1:nat, n2:nat, b:bytes_t, d:nat) -> zqmatrix_t:
        b = uintn.reverse(bytes.to_uintn_be(b))
        res = matrix.create(n1, n2, zqelem(0))
        for i in range(n1):
            for j in range(n2):
                res[i][j] = zqelem(uintn.reverse(b[(i*n2+j)*d:(i*n2+j+1)*d]))
        return res

    @typechecked
    def frodo_sample(r:uint16_t) -> zqelem_t:
        t = uintn.to_int(r >> 1)
        e = 0
        r0 = uintn.to_int(r & uint16(0x01))

        for z in range(cdf_table_len - 1):
            if (t > cdf_table[z]):
                e += 1
        e = ((-1) ** r0) * e
        return zqelem(e)

    @typechecked
    def frodo_sample_matrix(n1:nat, n2:nat, seed:bytes_t, ctr:uint16_t) -> zqmatrix_t:
        r = cshake_frodo(seed, ctr, n1 * n2 * 2)
        res = matrix.create(n1, n2, zqelem(0))
        for i in range(n1):
            for j in range(n2):
                res[i][j] = frodo_sample(bytes.to_uint16_le(r[2*(i * n2 + j):2*(i * n2 + j + 2)]))
        return res

    @typechecked
    def frodo_sample_matrix_tr(n1:nat, n2:nat, seed:bytes_t, ctr:uint16_t) -> zqmatrix_t:
        r = cshake_frodo(seed, ctr, n1 * n2 * 2)
        res = matrix.create(n1, n2, zqelem(0))
        for i in range(n1):
            for j in range(n2):
                res[i][j] = frodo_sample(bytes.to_uint16_le(r[2*(j * n1 + i):2*(j * n1 + i + 2)]))

        return res

    @typechecked
    def frodo_gen_matrix_cshake(n:nat, seed:bytes_t) -> zqmatrix_t:
        res = matrix.create(n, n, zqelem(0))
        for i in range(n):
            res_i = cshake128_frodo(seed, uint16(256 + i), n * 2)
            for j in range(n):
                res[i][j] = zqelem(bytes.to_uint16_le(res_i[(j * 2):(j * 2 + 2)]))
        return res

    @typechecked
    def frodo_gen_matrix_aes(n:nat, seed:bytes_t) -> zqmatrix_t:
        res = matrix.create(n, n, zqelem(0))
        tmp = array.create(8, uint16(0))
        for i in range(n):
            for j in range(0, n, 8):
                tmp[0] = uint16(i)
                tmp[1] = uint16(j)
                res_i = aes128_encrypt_block(seed, bytes.from_uint16s_le(tmp))
                for k in range(8):
                    res[i][j+k] = zqelem(bytes.to_uint16_le(res_i[k*2:(k+1)*2]))
        return res

    if (gen_a == 'AES128'):
        frodo_gen_matrix = frodo_gen_matrix_aes
    else:
        frodo_gen_matrix = frodo_gen_matrix_cshake

    @typechecked
    def crypto_kem_keypair(coins:bytes_t(2*crypto_bytes+bytes_seed_a)) -> \
        tuple2 (bytes_t(crypro_publickeybytes), tuple2 (bytes_t(crypto_secretkeybytes), matrix_t)):
        s, x = bytes.split(coins, crypto_bytes)
        seed_e, z = bytes.split(x, crypto_bytes)
        seed_a = cshake_frodo(z, uint16(0), bytes_seed_a)

        a_matrix = frodo_gen_matrix(params_n, seed_a)
        s_matrix = frodo_sample_matrix_tr(params_n, params_nbar, seed_e, uint16(1))
        e_matrix = frodo_sample_matrix(params_n, params_nbar, seed_e, uint16(2))
        b_matrix = a_matrix @ s_matrix + e_matrix
        b = frodo_pack(params_n, params_nbar, b_matrix, params_logq)

        pk = bytes.concat(seed_a, b)
        sk = bytes.concat(s, pk)
        return (pk, (sk, s_matrix))

    @typechecked
    def crypto_kem_enc(coins:bytes_t(bytes_mu), pk:bytes_t(crypro_publickeybytes)) -> \
        (bytes_t(crypto_ciphertextbytes), bytes_t(crypto_bytes)):
        seed_a, b = bytes.split(pk, bytes_seed_a)

        g = cshake_frodo(bytes.concat(pk, coins), uint16(3), 3 * crypto_bytes)
        seed_e, x = bytes.split(g, crypto_bytes)
        k, d = bytes.split(x, crypto_bytes)

        sp_matrix = frodo_sample_matrix(params_nbar, params_n, seed_e, uint16(4))
        ep_matrix = frodo_sample_matrix(params_nbar, params_n, seed_e, uint16(5))
        a_matrix = frodo_gen_matrix(params_n, seed_a)
        bp_matrix = sp_matrix @ a_matrix + ep_matrix
        c1 = frodo_pack(params_nbar, params_n, bp_matrix, params_logq)

        epp_matrix = frodo_sample_matrix(params_nbar, params_nbar, seed_e, uint16(6))
        b_matrix = frodo_unpack(params_n, params_nbar, b, params_logq)
        v_matrix = sp_matrix @ b_matrix + epp_matrix

        mu_encode = frodo_key_encode(coins, params_extracted_bits)
        c_matrix = v_matrix + mu_encode
        c2 = frodo_pack(params_nbar, params_nbar, c_matrix, params_logq)

        ss_init = bytes.concat(c1, bytes.concat(c2, bytes.concat(k, d)))
        ss = cshake_frodo(ss_init, uint16(7), crypto_bytes)
        ct = bytes.concat(c1, bytes.concat(c2, d))
        return (ct, ss)

    @typechecked
    def crypto_kem_dec(ct:bytes_t(crypto_ciphertextbytes),
                       sk:tuple2 (bytes_t(crypto_secretkeybytes), matrix_t)) -> bytes_t(crypto_bytes):
        c1Len = (params_logq * params_n * params_nbar) // 8
        c2Len = (params_logq * params_nbar * params_nbar) // 8
        c1, x = bytes.split(ct, c1Len)
        c2, d = bytes.split(x, c2Len)

        sk1, s_matrix = sk
        s, pk = bytes.split(sk1, crypto_bytes)
        seed_a, b = bytes.split(pk, bytes_seed_a)

        bp_matrix = frodo_unpack(params_nbar, params_n, c1, params_logq)
        c_matrix = frodo_unpack(params_nbar, params_nbar, c2, params_logq)
        m_matrix = c_matrix - bp_matrix @ s_matrix
        mu_decode = frodo_key_decode(m_matrix, params_extracted_bits)

        g = cshake_frodo(bytes.concat(pk, mu_decode), uint16(3), 3 * crypto_bytes)
        seed_ep, x = bytes.split(g,crypto_bytes)
        kp, dp =bytes.split(x, crypto_bytes)

        sp_matrix = frodo_sample_matrix(params_nbar, params_n, seed_ep, uint16(4))
        ep_matrix = frodo_sample_matrix(params_nbar, params_n, seed_ep, uint16(5))
        a_matrix = frodo_gen_matrix(params_n, seed_a)
        bpp_matrix = sp_matrix @ a_matrix + ep_matrix

        epp_matrix = frodo_sample_matrix(params_nbar, params_nbar, seed_ep, uint16(6))
        b_matrix = frodo_unpack(params_n, params_nbar, b, params_logq)
        v_matrix = sp_matrix @ b_matrix + epp_matrix

        mu_encode = frodo_key_encode(mu_decode, params_extracted_bits)
        cp_matrix = v_matrix + mu_encode

        ss_init = bytes.concat(c1, c2)
        if (d == dp and bp_matrix == bpp_matrix and c_matrix == cp_matrix):
            ss_init = bytes.concat(ss_init, bytes.concat(kp, d))
        else:
            ss_init = bytes.concat(ss_init, bytes.concat(s, d))
        ss = cshake_frodo(ss_init, uint16(7), crypto_bytes)
        return ss

    return (crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec)
