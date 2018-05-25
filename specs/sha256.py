# Run mypy sha2.py to type check.

from speclib import *

variant = refine(nat,lambda x: x == 224 or x == 256 or x == 384 or x == 512)
def wt(n:variant):
    if x == 224 or x == 256:
        return uint32_t
    else:
        return uint64_t

   
const_224_256_ops = List.Tot.map rotval32 [
    2; 13; 22;
    6; 11; 25;
    7; 18; 3;
    17; 19; 10]

const_384_512_ops = List.Tot.map rotval64 [
    28; 34; 39;
    14; 18; 41;
    1;   8;  7;
    19; 61;  6]


const_224_h0 = [
    0xc1059ed8, 0x367cd507, 0x3070dd17, 0xf70e5939,
    0xffc00b31, 0x68581511, 0x64f98fa7, 0xbefa4fa4]

const_256_h0 = List.Tot.map u32 [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

const_384_h0 = List.Tot.map u64 [
    0xcbbb9d5dc1059ed8, 0x629a292a367cd507, 0x9159015a3070dd17, 0x152fecd8f70e5939,
    0x67332667ffc00b31, 0x8eb44a8768581511, 0xdb0c2e0d64f98fa7, 0x47b5481dbefa4fa4]

const_512_h0 = List.Tot.map u64 [
    0x6a09e667f3bcc908, 0xbb67ae8584caa73b, 0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
    0x510e527fade682d1, 0x9b05688c2b3e6c1f, 0x1f83d9abfb41bd6b, 0x5be0cd19137e2179]


const_224_256_k = List.Tot.map u32 [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

const_384_512_k = List.Tot.map u64 [
    0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
    0x3956c25bf348b538, 0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
    0xd807aa98a3030242, 0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
    0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 0xc19bf174cf692694,
    0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
    0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
    0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4,
    0xc6e00bf33da88fc2, 0xd5a79147930aa725, 0x06ca6351e003826f, 0x142929670a0e6e70,
    0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
    0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6, 0x92722c851482353b,
    0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30,
    0xd192e819d6ef5218, 0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
    0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
    0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
    0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
    0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b,
    0xca273eceea26619c, 0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
    0x06f067aa72176fba, 0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
    0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
    0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817]


    const_224_256_ops = [

    ]
def opTable(n:variant):
    

# Constants
H0 = uint32(0x6a09e667)
H1 = uint32(0xbb67ae85)
H2 = uint32(0x3c6ef372)
H3 = uint32(0xa54ff53a)
H4 = uint32(0x510e527f)
H5 = uint32(0x9b05688c)
H6 = uint32(0x1f83d9ab)
H7 = uint32(0x5be0cd19)

constants = array([
    uint32(0x428a2f98), uint32(0x71374491), uint32(0xb5c0fbcf),
    uint32(0xe9b5dba5), uint32(0x3956c25b), uint32(0x59f111f1),
    uint32(0x923f82a4), uint32(0xab1c5ed5), uint32(0xd807aa98),
    uint32(0x12835b01), uint32(0x243185be), uint32(0x550c7dc3),
    uint32(0x72be5d74), uint32(0x80deb1fe), uint32(0x9bdc06a7),
    uint32(0xc19bf174), uint32(0xe49b69c1), uint32(0xefbe4786),
    uint32(0x0fc19dc6), uint32(0x240ca1cc), uint32(0x2de92c6f),
    uint32(0x4a7484aa), uint32(0x5cb0a9dc), uint32(0x76f988da),
    uint32(0x983e5152), uint32(0xa831c66d), uint32(0xb00327c8),
    uint32(0xbf597fc7), uint32(0xc6e00bf3), uint32(0xd5a79147),
    uint32(0x06ca6351), uint32(0x14292967), uint32(0x27b70a85),
    uint32(0x2e1b2138), uint32(0x4d2c6dfc), uint32(0x53380d13),
    uint32(0x650a7354), uint32(0x766a0abb), uint32(0x81c2c92e),
    uint32(0x92722c85), uint32(0xa2bfe8a1), uint32(0xa81a664b),
    uint32(0xc24b8b70), uint32(0xc76c51a3), uint32(0xd192e819),
    uint32(0xd6990624), uint32(0xf40e3585), uint32(0x106aa070),
    uint32(0x19a4c116), uint32(0x1e376c08), uint32(0x2748774c),
    uint32(0x34b0bcb5), uint32(0x391c0cb3), uint32(0x4ed8aa4a),
    uint32(0x5b9cca4f), uint32(0x682e6ff3), uint32(0x748f82ee),
    uint32(0x78a5636f), uint32(0x84c87814), uint32(0x8cc70208),
    uint32(0x90befffa), uint32(0xa4506ceb), uint32(0xbef9a3f7),
    uint32(0xc67178f2)])

# We expect messages to have full byte lengths.


def pad(msg: array[uint8]) -> array[uint8]:
    msg_len_bits = len(msg) * 8
    one_len = 512 - ((msg_len_bits + 1 + 64) % 512)
    pad_len = (one_len + 1) // 8
    padding = array.create(pad_len,uint8(0))
    padding[0] = uint8(0x80)
    msg_len_bytes = bytes.from_uint64_be(uint64(msg_len_bits))
    msg_len_array = array.create_type(msg_len_bytes, uint8) # type: array[uint8]
    padding[0:array.length(msg_len_array)] = msg_len_array
    padded_msg = array.copy(msg)
    padded_msg.extend(padding)
    return padded_msg


def hash(msg: array[uint8]) -> array[uint32]:
    blocks = msg.split(512//8)
    h0 = H0
    h1 = H1
    h2 = H2
    h3 = H3
    h4 = H4
    h5 = H5
    h6 = H6
    h7 = H7
    for block in blocks:
        state = array.create(64,uint32(0))
        for i in range(0, 16):
            state[i] = uint32.from_u8array(block[i*4:i*4+4])
        for i in range(16, 64):
            s0 = uint32.rotate_right(
                state[i-15], 7) ^ uint32.rotate_right(state[i-15], 18) ^ (state[i-15] >> 3)
            s1 = uint32.rotate_right(
                state[i-2], 17) ^ uint32.rotate_right(state[i-2], 19) ^ (state[i-2] >> 10)
            state[i] = state[i-16] + s0 + state[i-7] + s1
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        f = h5
        g = h6
        h = h7
        for i in range(0, 64):
            s1 = uint32.rotate_right(e, 6) ^ uint32.rotate_right(
                e, 11) ^ uint32.rotate_right(e, 25)
            not_e = ~e
            ch = (e & f) ^ (not_e & g)
            tmp = h + s1 + ch + constants[i] + state[i]
            s0 = uint32.rotate_right(a, 2) ^ uint32.rotate_right(
                a, 13) ^ uint32.rotate_right(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            tmp2 = s0 + maj

            h = g
            g = f
            f = e
            e = d + tmp
            d = c
            c = b
            b = a
            a = tmp + tmp2

        h0 = h0 + a
        h1 = h1 + b
        h2 = h2 + c
        h3 = h3 + d
        h4 = h4 + e
        h5 = h5 + f
        h6 = h6 + g
        h7 = h7 + h

    return array([h7, h6, h5, h4, h3, h2, h1, h0])
