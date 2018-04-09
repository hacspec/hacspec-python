from speclib import *

bits_in_word = 32
rounds_in_f = 10
block_bytes = 64
R1 = 16
R2 = 12
R3 = 8
R4 = 7

working_vector_t = array_t(uint32_t, 16)
hash_vector_t = array_t(uint32_t, 8)
index_t = range_t(0, 16)

SIGMA: array_t(index_t, 16 * 12) = array([
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3,
    11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4,
    7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8,
    9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13,
    2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9,
    12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11,
    13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10,
    6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5,
    10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0,
])

IV = array([
    uint32(0x6A09E667), uint32(0xBB67AE85), uint32(
        0x3C6EF372), uint32(0xA54FF53A),
    uint32(0x510E527F), uint32(0x9B05688C), uint32(
        0x1F83D9AB), uint32(0x5BE0CD19)
])


def G(v: working_vector_t, a: index_t, b: index_t, c: index_t, d: index_t, x: uint32_t, y: uint32_t) -> working_vector_t:
    v[a] = v[a] + v[b] + x
    v[d] = uint32_t.rotate_right(v[d] ^ v[a], R1)
    v[c] = v[c] + v[d]
    v[b] = uint32_t.rotate_right(v[b] ^ v[c], R2)
    v[a] = v[a] + v[b] + y
    v[d] = uint32_t.rotate_right(v[d] ^ v[a], R3)
    v[c] = v[c] + v[d]
    v[b] = uint32_t.rotate_right(v[b] ^ v[c], R4)
    return v


def F(h: hash_vector_t, m: working_vector_t, t: uint64_t, flag: bool) -> hash_vector_t:
    v = array.create(16, uint32(0))
    v[0:8] = h
    v[8:16] = IV
    v[12] = v[12] ^ uint32(t)
    v[13] = v[13] ^ uint32(t >> 32)
    if flag == True:
        v[14] = v[14] ^ uint32(0xFFFFFFFF)
    for i in range(rounds_in_f):
        s = SIGMA[i * 16:(i + 1) * 16]
        v = G(v, 0, 4, 8, 12, m[s[0]], m[s[1]])
        v = G(v, 1, 5, 9, 13, m[s[2]], m[s[3]])
        v = G(v, 2, 6, 10, 14, m[s[4]], m[s[5]])
        v = G(v, 3, 7, 11, 15, m[s[6]], m[s[7]])
        v = G(v, 0, 5, 10, 15, m[s[8]], m[s[9]])
        v = G(v, 1, 6, 11, 12, m[s[10]], m[s[11]])
        v = G(v, 2, 7, 8, 13, m[s[12]], m[s[13]])
        v = G(v, 3, 4, 9, 14, m[s[14]], m[s[15]])
    for i in range(8):
        h[i] = h[i] ^ v[i] ^ v[i + 8]
    return h


data_internal_t = refine(bytes_t, lambda x: vlbytes.length(
    x) < 2 ** 64 and (vlbytes.length(x) % block_bytes == 0))
key_t = refine(vlbytes_t, lambda x: vlbytes.length(x) <= 32)
key_size_t = refine(nat, lambda x: x <= 32)
out_size_t = refine(nat, lambda x: x <= 32)


def blake2s_internal(data: data_internal_t, input_bytes: uint64_t, kk: key_size_t, nn: out_size_t) \
        -> contract(vlbytes_t,
                    lambda data, input_bytes, kk, nn: True,
                    lambda data, input_bytes, kk, nn, res: vlbytes.length(res) == nn):
    h = array.copy(IV)
    h[0] = h[0] ^ uint32(0x01010000) ^ (uint32(kk) << 8) ^ uint32(nn)
    data_blocks = vlbytes.length(data) // block_bytes
    if data_blocks > 1:
        for i in range(data_blocks - 1):
            h = F(h, vlbytes.to_uint32s_le(
                data[block_bytes * i:block_bytes * (i + 1)]), uint64((i + 1) * block_bytes), False)
    if kk == 0:
        h = F(h, vlbytes.to_uint32s_le(
            data[block_bytes * (data_blocks - 1):block_bytes * data_blocks]), uint64(input_bytes), True)
    else:
        h = F(h, vlbytes.to_uint32s_le(
            data[block_bytes * (data_blocks - 1):block_bytes * data_blocks]), uint64(input_bytes + block_bytes), True)
    return vlbytes.from_uint32s_le(h)[:nn]


max_size_t = 2**32 - 1
data_t = refine(vlbytes_t, lambda x: vlbytes.lenght(x)
                < max_size_t - 2 * block_bytes)


def blake2s(data: data_t, key: key_t, nn: out_size_t) \
        -> contract(vlbytes_t,
                    lambda data, key, nn: True, lambda data, key, nn, res: vlbytes.length(res) == nn):
    ll = vlbytes.length(data)
    kk = vlbytes.length(key)
    data_blocks = (ll - 1) // block_bytes + 1
    padded_data_length = data_blocks * block_bytes
    if kk == 0:
        padded_data = array.create(padded_data_length, uint8(0))
        padded_data[:ll] = data
    else:
        padded_data = array.create(padded_data_length + block_bytes, uint8(0))
        padded_data[0:kk] = key
        padded_data[block_bytes:block_bytes + ll] = key
    return blake2s_internal(padded_data, ll, kk, nn)
