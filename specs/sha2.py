# Run mypy sha2.py to type check.

from speclib import *

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
    padding = array.create(uint8(0), pad_len)
    padding[0] = uint8(0x80)
    msg_len_bytes = uint64.to_bytes_be(uint64(msg_len_bits))
    # msg_len_array = array.create_type(msg_len_bytes, uint8) # tpye: array[uint8]
    padding = padding.extend(msg_len_bytes)
    padded_msg = array.copy(msg)
    padded_msg = padded_msg.extend(padding)
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
        state = array.create(uint32(0), 64)
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

        h0 = uint32(h0 + a)
        h1 = uint32(h1 + b)
        h2 = uint32(h2 + c)
        h3 = uint32(h3 + d)
        h4 = uint32(h4 + e)
        h5 = uint32(h5 + f)
        h6 = uint32(h6 + g)
        h7 = uint32(h7 + h)

    return array([h7, h6, h5, h4, h3, h2, h1, h0])

def sha256(msg: array[uint8]) -> array[uint32]:
    padded = pad(msg)
    return hash(padded)
