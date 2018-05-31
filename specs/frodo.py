from lib.speclib import *
from specs.keccak import *
from math import floor

# Parameters for "FrodoKEM-640"
params_n = 640
params_nbar = 8
params_logq = 15
params_extracted_bits = 2
params_symbytes = 16

params_q = 2 ** params_logq
bytes_mu = (params_extracted_bits * params_nbar * params_nbar) // 8
crypro_publickeybytes = params_symbytes + (params_logq * params_n * params_nbar) // 8
crypto_secretkeybytes = params_symbytes + crypro_publickeybytes  #+2 * params_n * params_nbar
crypto_bytes = params_symbytes
crypto_ciphertextbytes = ((params_nbar * params_n + params_nbar * params_nbar) * params_logq) // 8 + params_symbytes

cdf_table_len = 12
cdf_table = array([4727, 13584, 20864, 26113, 29434, 31278, 32176, 32560, 32704, 32751, 32764, 32767])

zqelem_t = natmod_t(params_q)
def zqelem(n:nat):
    return natmod(n, params_q)

# def zqmatrix_t(n:nat, m:nat):
#     return matrix_t(zqelem_t, n, m)

zqmatrix_t = [[zqelem_t]]

#res[n1; n3] = a[n1; n2] * b[n2; n3]
def zqmatrix_mul(n1:nat, n2:nat, n3:nat, a:zqmatrix_t, b:zqmatrix_t) -> zqmatrix_t:
    res = matrix.create(n1, n3, zqelem(0))
    for i in range(n1):
        for k in range(n3):
            tmp = zqelem(0)
            for j in range(n2):
                tmp += zqelem(a[i][j]) * zqelem(b[j][k])
            res[i][k] = tmp
    return res

#res[n1; n2] = a[n1; n2] + b[n1; n2]
def zqmatrix_add(n1:nat, n2:nat, a:zqmatrix_t, b:zqmatrix_t) -> zqmatrix_t:
    res = matrix.create(n1, n2, zqelem(0))
    for i in range(n1):
        for j in range(n2):
            res[i][j] = zqelem(a[i][j]) + zqelem(b[i][j])
    return res

#res[n1; n2] = a[n1; n2] - b[n1; n2]
def zqmatrix_sub(n1:nat, n2:nat, a:zqmatrix_t, b:zqmatrix_t) -> zqmatrix_t:
    res = matrix.create(n1, n2, zqelem(0))
    for i in range(n1):
        for j in range(n2):
            res[i][j] = zqelem(a[i][j]) - zqelem(b[i][j])
    return res

#FrodoKEM
def cshake128_frodo(inputByteLen:nat,
                    input_b:refine(vlbytes_t, lambda x: array.length(x) == inputByteLen),
                    cstm:uint16_t,
                    outputByteLen:nat) -> refine(vlbytes_t, lambda x: array.length(x) == outputByteLen):

    delimitedSuffix = uint8(0x04)
    rateInBytes = 168

    s1 = array.create(8, uint8(0))
    s1[0] = uint8(0x01)
    s1[1] = uint8(0xa8)
    s1[2] = uint8(0x01)
    s1[3] = uint8(0x00)
    s1[4] = uint8(0x01)
    s1[5] = uint8(16)
    s1[6] = uint8(cstm)
    s1[7] = uint8(cstm >> 8)

    s = array.create(25, uint64(0))
    s[0] = bytes.to_uint64_le(s1)
    s = state_permute(s)

    s = absorb(s, rateInBytes, inputByteLen, input_b, delimitedSuffix)
    output = squeeze(s, rateInBytes, outputByteLen)
    return output

def frodo_key_encode(a:bytes_t, b:nat) -> zqmatrix_t:
    a = bytes.to_uintn_le(a)
    res = matrix.create(params_nbar, params_nbar, zqelem(0))
    for i in range(params_nbar):
        for j in range(params_nbar):
            k = uintn.to_int(a[(i*params_nbar+j)*b:(i*params_nbar+j+1)*b])
            res[i][j] = zqelem(k * (params_q // (2 ** b)))
    return res

def frodo_key_decode(a:zqmatrix_t, b:nat) -> bytes_t:
    res = uintn(0, params_nbar*params_nbar*b)
    for i in range(params_nbar):
        for j in range(params_nbar):
            k = floor(natmod.to_int(a[i][j]) * (2 ** b) / params_q + 1/2)
            res = uintn.set_bits(res,(i*params_nbar+j)*b,(i*params_nbar+j+1)*b, uintn(k, b))
    res = bytes.from_uintn_le(res)
    return res

def frodo_pack(n1:nat, n2:nat, a:zqmatrix_t, d:nat) -> bytes_t:
    res = uintn(0, n1*n2*d)
    for i in range(n1):
        for j in range(n2):
            res = uintn.set_bits(res,(i*n2+j)*d,(i*n2+j+1)*d, uintn.reverse(uintn(a[i][j], d)))
    res = bytes.from_uintn_le(res)
    return res

def frodo_unpack(n1:nat, n2:nat, b:bytes_t, d:nat) -> zqmatrix_t:
    b = bytes.to_uintn_le(b)
    res = matrix.create(n1, n2, zqelem(0))
    for i in range(n1):
        for j in range(n2):
            res[i][j] = zqelem(uintn.reverse(b[(i*n2+j)*d:(i*n2+j+1)*d]))
    return res

def frodo_sample(r:uint16_t) -> int:
    t = uintn.to_int(r >> 1)
    e = 0
    r0 = uintn.to_int(r & uint16(0x01))

    for z in range(cdf_table_len - 1):
        if (t > cdf_table[z]):
            e += 1
    e = ((-1) ** r0) * e
    return e

def frodo_sample_matrix(n1:nat, n2:nat, seedLen:nat, seed:bytes_t, ctr:uint16_t) -> zqmatrix_t:
    r = cshake128_frodo(seedLen, seed, ctr, n1 * n2 * 2)
    res = matrix.create(n1, n2, zqelem(0))
    for i in range(n1):
        for j in range(n2):
            res[i][j] = frodo_sample(bytes.to_uint16_le(r[2*(i * n2 + j):2*(i * n2 + j + 2)]))
    return res

def frodo_gen_matrix(n:nat, seedLen:nat, seed:bytes_t) -> zqmatrix_t:
    res = matrix.create(n, n, zqelem(0))
    for i in range(n):
        res_i = cshake128_frodo(seedLen, seed, uint16(256 + i), n * 2)
        for j in range(n):
            res[i][j] = zqelem(bytes.to_uint16_le(res_i[(j * 2):(j * 2 + 2)]))
    return res

def crypto_kem_keypair(coins:bytes_t(2*crypto_bytes+params_symbytes)) -> \
    tuple2 (bytes_t(crypro_publickeybytes), tuple2 (bytes_t(crypto_secretkeybytes), matrix_t)):
    s, x = bytes.split(coins, crypto_bytes)
    seed_e, z = bytes.split(x, crypto_bytes)
    seed_a = cshake128_frodo(params_symbytes, z, uint16(0), params_symbytes)

    a_matrix = frodo_gen_matrix(params_n, params_symbytes, seed_a)
    s_matrix = frodo_sample_matrix(params_n, params_nbar, crypto_bytes, seed_e, uint16(1))
    e_matrix = frodo_sample_matrix(params_n, params_nbar, crypto_bytes, seed_e, uint16(2))

    b_matrix = zqmatrix_mul(params_n, params_n, params_nbar, a_matrix, s_matrix)
    b_matrix = zqmatrix_add(params_n, params_nbar, b_matrix, e_matrix)
    b = frodo_pack(params_n, params_nbar, b_matrix, params_logq)

    pk = bytes.concat(seed_a, b)
    sk = bytes.concat(s, pk)
    return (pk, (sk, s_matrix))

def crypto_kem_enc(coins:bytes_t, pk:bytes_t(crypro_publickeybytes)) -> \
    (bytes_t(crypto_ciphertextbytes), bytes_t(crypto_bytes)):
    seed_a, b = bytes.split(pk, params_symbytes)

    tmp = bytes.concat(pk, coins)
    g = cshake128_frodo(crypro_publickeybytes + bytes_mu, tmp, uint16(3), 3 * crypto_bytes)
    seed_e, x = bytes.split(g, crypto_bytes)
    k, d = bytes.split(x, crypto_bytes)

    sp_matrix = frodo_sample_matrix(params_nbar, params_n, crypto_bytes, seed_e, uint16(4))
    ep_matrix = frodo_sample_matrix(params_nbar, params_n, crypto_bytes, seed_e, uint16(5))
    a_matrix = frodo_gen_matrix(params_n, params_symbytes, seed_a)
    bp_matrix = zqmatrix_mul(params_nbar, params_n, params_n, sp_matrix, a_matrix)
    bp_matrix = zqmatrix_add(params_nbar, params_n, bp_matrix, ep_matrix)
    c1 = frodo_pack(params_nbar, params_n, bp_matrix, params_logq)

    epp_matrix = frodo_sample_matrix(params_nbar, params_nbar, crypto_bytes, seed_e, uint16(6))
    b_matrix = frodo_unpack(params_n, params_nbar, b, params_logq)
    v_matrix = zqmatrix_mul(params_nbar, params_n, params_nbar, sp_matrix, b_matrix)
    v_matrix = zqmatrix_add(params_nbar, params_nbar, v_matrix, epp_matrix)

    mu_encode = frodo_key_encode(coins, params_extracted_bits)
    c_matrix = zqmatrix_add(params_nbar, params_nbar, v_matrix, mu_encode)
    c2 = frodo_pack(params_nbar, params_nbar, c_matrix, params_logq)

    ss_init = bytes.concat(c1, bytes.concat(c2, bytes.concat(k, d)))
    c1Len = (params_logq * params_n * params_nbar) // 8
    c2Len = (params_logq * params_nbar * params_nbar) // 8
    ss = cshake128_frodo(c1Len+c2Len+2*crypto_bytes, ss_init, uint16(7), crypto_bytes)
    ct = bytes.concat(c1, bytes.concat(c2, d))
    return (ct, ss)

def crypto_kem_dec(ct:bytes_t(crypto_ciphertextbytes), sk:tuple2 (bytes_t(crypto_secretkeybytes), matrix_t)) -> bytes_t(crypto_bytes):
    #parse ct
    c1Len = (params_logq * params_n * params_nbar) // 8
    c2Len = (params_logq * params_nbar * params_nbar) // 8
    c1, x = bytes.split(ct, c1Len)
    c2, d = bytes.split(x, c2Len)

    #parse sk
    sk1, s_matrix = sk
    s, pk = bytes.split(sk1, crypto_bytes)
    seed_a, b = bytes.split(pk, params_symbytes)

    bp_matrix = frodo_unpack(params_nbar, params_n, c1, params_logq)
    c_matrix = frodo_unpack(params_nbar, params_nbar, c2, params_logq)
    m_matrix = zqmatrix_mul(params_nbar, params_n, params_nbar, bp_matrix, s_matrix)
    m_matrix = zqmatrix_sub(params_nbar, params_nbar, c_matrix, m_matrix)
    mu_decode = frodo_key_decode(m_matrix, params_extracted_bits)

    tmp = bytes.concat(pk, mu_decode)
    g = cshake128_frodo(crypro_publickeybytes + bytes_mu, tmp, uint16(3), 3 * crypto_bytes)
    seed_ep, x = bytes.split(g,crypto_bytes)
    kp, dp =bytes.split(x, crypto_bytes)

    sp_matrix = frodo_sample_matrix(params_nbar, params_n, crypto_bytes, seed_ep, uint16(4))
    ep_matrix = frodo_sample_matrix(params_nbar, params_n, crypto_bytes, seed_ep, uint16(5))
    a_matrix = frodo_gen_matrix(params_n, params_symbytes, seed_a)
    bpp_matrix = zqmatrix_mul(params_nbar, params_n, params_n, sp_matrix, a_matrix)
    bpp_matrix = zqmatrix_add(params_nbar, params_n, bpp_matrix, ep_matrix)

    epp_matrix = frodo_sample_matrix(params_nbar, params_nbar, crypto_bytes, seed_ep, uint16(6))
    b_matrix = frodo_unpack(params_n, params_nbar, b, params_logq)
    v_matrix = zqmatrix_mul(params_nbar, params_n, params_nbar, sp_matrix, b_matrix)
    v_matrix = zqmatrix_add(params_nbar, params_nbar, v_matrix, epp_matrix)

    mu_encode = frodo_key_encode(mu_decode, params_extracted_bits)
    cp_matrix = zqmatrix_add(params_nbar, params_nbar, v_matrix, mu_encode)

    #ss_init = c1 || c2 || (kp or s) || d
    ssiLen = c1Len+c2Len+2*crypto_bytes
    ss_init = bytes.concat(c1, c2)

    if (d == dp and bp_matrix == bpp_matrix and c_matrix == cp_matrix):
        ss_init = bytes.concat(ss_init, bytes.concat(kp, d))
    else:
        ss_init = bytes.concat(ss_init, bytes.concat(s, d))

    ss = cshake128_frodo(ssiLen, ss_init, uint16(7), crypto_bytes)
    return ss
