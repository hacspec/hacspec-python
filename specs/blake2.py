from hacspec.speclib import *

variant_t = refine(nat, lambda x: x == 0 or x == 1)
out_size_t = refine(nat, lambda x: x <= 32)

@typechecked
def highbits_128(x:uint128_t) -> uint64_t:
    return uint64(x >> 64)

@typechecked
def highbits_64(x:uint64_t) -> uint32_t:
    return uint32(x >> 32)

@typechecked
def blake2(v:variant_t) -> FunctionType:
    if v == 1:
        bits_in_word = 64
        rounds_in_f = 12
        block_bytes = 128
        _R1 = 32
        _R2 = 24
        _R3 = 16
        _R4 = 63
        working_vector_t = array_t(uint64_t, 16)
        hash_vector_t = array_t(uint64_t, 8)
        index_t = range_t(0, 16)
        _IV = hash_vector_t([
            uint64(0x6A09E667F3BCC908), uint64(0xBB67AE8584CAA73B),
            uint64(0x3C6EF372FE94F82B), uint64(0xA54FF53A5F1D36F1),
            uint64(0x510E527FADE682D1), uint64(0x9B05688C2B3E6C1F),
            uint64(0x1F83D9ABFB41BD6B), uint64(0x5BE0CD19137E2179)
        ])
        to_word = uint64
        word_t = uint64_t
        minus_one = uint64(0xFFFFFFFFFFFFFFFF)
        data_internal_t = refine(bytes, lambda x: array.length(
            x) < 2 ** 64 and (array.length(x) % block_bytes == 0))
        key_t = refine(vlbytes_t, lambda x: array.length(x) <= 64)
        key_size_t = refine(nat, lambda x: x <= 64)
        to_words_le = vlbytes_t.to_uint64s_le
        from_words_le = vlbytes_t.from_uint64s_le
        low_bits = to_word
        high_bits = highbits_128
        double_word_t = uint128_t
        to_double_word = uint128
        max_size_t = 2**64 - 1
        data_t = refine(vlbytes_t, lambda x: vlbytes_t.length(x)
                            < max_size_t - 2 * block_bytes)
    else:
        bits_in_word = 32
        rounds_in_f = 10
        block_bytes = 64
        _R1 = 16
        _R2 = 12
        _R3 = 8
        _R4 = 7
        working_vector_t = array_t(uint32_t, 16)
        hash_vector_t = array_t(uint32_t, 8)
        index_t = range_t(0, 16)
        _IV = hash_vector_t([
            uint32(0x6A09E667), uint32(0xBB67AE85),
            uint32(0x3C6EF372), uint32(0xA54FF53A),
            uint32(0x510E527F), uint32(0x9B05688C),
            uint32(0x1F83D9AB), uint32(0x5BE0CD19)
        ])
        to_word = uint32
        word_t = uint32_t
        minus_one = uint32(0xFFFFFFFF)
        data_internal_t = refine(bytes, lambda x: array.length(
            x) < 2 ** 64 and (array.length(x) % block_bytes == 0))
        key_t = refine(vlbytes_t, lambda x: array.length(x) <= 32)
        key_size_t = refine(nat, lambda x: x <= 32)
        to_words_le = vlbytes_t.to_uint32s_le
        from_words_le = vlbytes_t.from_uint32s_le
        low_bits = to_word
        high_bits = highbits_64
        double_word_t = uint64_t
        to_double_word = uint64
        max_size_t = 2**32 - 1
        data_t = refine(vlbytes_t, lambda x: vlbytes_t.length(x)
                        < max_size_t - 2 * block_bytes)


    sigma_t = array_t(index_t, 16 * 12)
    _SIGMA = sigma_t([
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
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
        14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3
    ])


    @typechecked
    def _G(v: working_vector_t, a: index_t, b: index_t, c: index_t, d: index_t, x: word_t, y: word_t) -> working_vector_t:
        v[a] = v[a] + v[b] + x
        v[d] = word_t.rotate_right(v[d] ^ v[a], _R1)
        v[c] = v[c] + v[d]
        v[b] = word_t.rotate_right(v[b] ^ v[c], _R2)
        v[a] = v[a] + v[b] + y
        v[d] = word_t.rotate_right(v[d] ^ v[a], _R3)
        v[c] = v[c] + v[d]
        v[b] = word_t.rotate_right(v[b] ^ v[c], _R4)
        return v


    @typechecked
    def _F(h: hash_vector_t, m: working_vector_t, t: double_word_t, flag: bool) -> hash_vector_t:
        v = array.create(16, to_word(0))
        v[0:8] = h
        v[8:16] = _IV
        v[12] = v[12] ^ low_bits(t)
        v[13] = v[13] ^ high_bits(t)
        if flag == True:
            v[14] = v[14] ^ minus_one
        for i in range(rounds_in_f):
            s = _SIGMA[i * 16:(i + 1) * 16]
            v = _G(v, 0, 4, 8, 12, m[s[0]], m[s[1]])
            v = _G(v, 1, 5, 9, 13, m[s[2]], m[s[3]])
            v = _G(v, 2, 6, 10, 14, m[s[4]], m[s[5]])
            v = _G(v, 3, 7, 11, 15, m[s[6]], m[s[7]])
            v = _G(v, 0, 5, 10, 15, m[s[8]], m[s[9]])
            v = _G(v, 1, 6, 11, 12, m[s[10]], m[s[11]])
            v = _G(v, 2, 7, 8, 13, m[s[12]], m[s[13]])
            v = _G(v, 3, 4, 9, 14, m[s[14]], m[s[15]])
        for i in range(8):
            h[i] = h[i] ^ v[i] ^ v[i + 8]
        return h


    @typechecked
    def blake2_internal(data: data_internal_t, input_bytes: double_word_t, kk: key_size_t, nn: out_size_t) \
            -> contract(vlbytes,
                        lambda data, input_bytes, kk, nn: True,
                        lambda data, input_bytes, kk, nn, res: array.length(res) == nn):
        h = array.copy(_IV)
        h[0] = h[0] ^ to_word(0x01010000) ^ (to_word(kk) << 8) ^ to_word(nn)
        data_blocks = array.length(data) // block_bytes
        if data_blocks > 1:
            for i in range(data_blocks - 1):
                h = _F(h, to_words_le(
                    data[block_bytes * i:block_bytes * (i + 1)]), to_double_word((i + 1) * block_bytes), False)
        if kk == 0:
            h = _F(h, to_words_le(
                data[block_bytes * (data_blocks - 1):block_bytes * data_blocks]), input_bytes, True)
        else:
            h = _F(h, to_words_le(
                data[block_bytes * (data_blocks - 1):block_bytes * data_blocks]), input_bytes + to_double_word(block_bytes), True)
        return from_words_le(h)[:nn]


    @typechecked
    def blake2(data: data_t, key: key_t, nn: out_size_t) \
            -> contract(vlbytes_t,
                        lambda data, key, nn: True, lambda data, key, nn, res: array.length(res) == nn):
        ll = array.length(data)
        kk = array.length(key)
        data_blocks = (ll - 1) // block_bytes + 1
        padded_data_length = data_blocks * block_bytes
        if kk == 0:
            padded_data = bytes(array.create(padded_data_length, uint8(0)))
            padded_data[0:ll] = data
        else:
            padded_data = bytes(array.create(padded_data_length + block_bytes, uint8(0)))
            padded_data[0:kk] = key
            padded_data[block_bytes:block_bytes+ll] = data
        return blake2_internal(padded_data, to_double_word(ll), key_size_t(nat(kk)), nn)

    return blake2

blake2s = blake2(variant_t(nat(0)))
blake2b = blake2(variant_t(nat(1)))
