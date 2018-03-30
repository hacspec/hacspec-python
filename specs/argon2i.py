from speclib import *
from blake2b import blake2b

version_number = uint8(0x13)
argon_type = 1
block_size = 1024
line_size = 128

max_size_t = 2**64 - 1
size_nat = refine(nat, lambda x: x <= max_size_t)

output_size_t = refine(nat, lambda x: x <= 64)


def h(a: refine(vlbytes_t, lambda x: vlbytes.length(x) < max_size_t - 2 * line_size), nn: output_size_t) -> refine(vlbytes_t, lambda x: vlbytes.length(x) == nn):
    return blake2b(a, array([]), nn)


def ceil32(x: size_nat) -> size_nat:
    if x % 32 == 0:
        return x // 32
    else:
        return x // 32 + 1


def compute_variable_length_output_size(t_len: refine(size_nat, lambda x: x + 64 <= max_size_t)) -> size_nat:
    if t_len <= 64:
        return t_len
    else:
        r = ceil32(t_len) - 2
        return 32 * r + 64


def h_prime(t_len: refine(size_nat, lambda x: 1 <= t_len and t_len + 64 <= max_size_t), x: refine(vlbytes_t, lambda x: vlbytes.length(x) + 4 <= max_size_t - 2 * line_size)) -> refine(vlbytes_t, lambda x: vlbytes.length(x) == compute_variable_length_output_size(t_len)):
    t_with_x = array.create(vlbytes.length(x) + 4, uint8(0))
    t_with_x[0:4] = vlbytes.from_uint32_le(uint32(t_len))
    t_with_x[4:] = x
    if t_len <= 64:
        return h(t_with_x, t_len)
    else:
        r = ceil32(t_len) - 2
        output = array.create(
            compute_variable_length_output_size(t_len), uint8(0))
        previous = h(t_with_x, 64)
        output[0:32] = previous[0:32]
        for i in range(r):
            i = i + 1
            v = h(previous, 64)
            output[i * 32:(i + 1) * 32] = v[0:32]
            previous = v
        output[r * 32:r * 32 + 64] = previous
        return output


idx_t = refine(size_nat, lambda x: x <= 15)


def low_bits(x: uint64_t) -> uint64_t:
    return uint64(uint32(x))

working_vector_t = array_t(uint64_t,16)


def g(v:working_vector_t, a: idx_t, b:idx_t, c:idx_t, i4:idx_t) -> working_vector_t:
    v[a] = v[a] + v[b] + uint64(2) * low_bits(v[a]) * low_bits(v[b])
    v[d] = uint64_t.rotate_right(v[d] ^ v[a], 32)
    v[c] = v[c] + v[d] + uint64(2) * low_bits(v[c]) * low_bits(v[d])
    v[b] = uint64_t.rotate_right(v[b] ^ v[c], 24)
    v[a] = v[a] + v[b] + uint64(2) * low_bits(v[a]) * low_bits(v[b])
    v[d] = uint64_t.rotate_right(v[d] ^ v[a], 16)
    v[c] = v[c] + v[d] + uint64(2) * low_bits(v[c]) * low_bits(v[d])
    v[b] = uint64_t.rotate_right(v[b] ^ v[c], 63)
    return v

def P(input: bytes_t(line_size)) -> bytes_t(line_size):
    v = array.create(16,uint64(0))
    for i in range(8):
        v[2*i] = vlbytes.to_uint64_le(inpit[i*16:i*16+8])
        v[2*i+1] = vlbytes.to_uint64_le(v[i*16+8:(i+1)*16])
    v = g(v,0,4,8,12)
    v = g(v,1,5,9,13)
    v = g(v,2,6,10,14)
    v = g(v,3,7,11,15)
    v = g(v,0,5,10,15)
    v = g(v,1,6,11,12)
    v = g(v,2,7,8,13)
    v = g(v,3,4,9,14)
    return v

def xor_blocks(X: bytes_t(block_size), Y:bytes_t(block_size)) -> bytes_t(block_size):
    output = create(block_size,uint8(0))
    for i in range(block_size//8):
        output[i*8:(i+1)*8] = vlbytes.from_uint64_be(vlbytes.to_uint64_be(X[8*i:8*(i+1)]) ^ vlbytes.to_uint64_be(Y[8*i:8*(i+1)]))
    return output

def extract_block_column(j:range_t(0,8), block:bytes_t(block_size)) -> bytes_t(line_size):
    col = array.create(line_size,uint8(0))
    for i in range(8):
        offset = i*line_size + j*16
        col[i*16:(i+1)*16] = block[offset:offset+16]
    return col

def update_block_column(j:range_t(0,8), col:bytes_t(line_size), block:bytes_t(block_size)) -> bytes_t(block_size):
     for i in range(8):
         offset = i*line_size + j*16
         block[offset:offset+16] = col[i*16:(i+1)*16]
     return block

def G(X:bytes_t(block_size), Y:bytes_t(block_size)) -> bytes_t(block_size):
    R = array.create(block_size,uint8(0))
    R = xor_blocks(X,Y)
    Q = array.copy(R)
    for i in range(8):
        row = Q[i*line_size:(i+1)*line_size]
        row = P(row)
        Q[line_size*i:line_size*(i+1)] = row
    Z = Q
    for j in range(8):
        col = extract_block_column(j,block)
        col = P(col)
        Z = update_block_column(j,col,Z)
    return xor_blocks(Z,R)
