from speclib import *
from blake2b import blake2b

version_number = uint8(0x13)
argon_type = 1
block_size = 1024
line_size = 128

max_size_t = 2**64 - 1
size_nat = refine3('size_nat', nat, lambda x: x <= max_size_t)
output_size = refine3('size_nat', nat, lambda x: x <= 64)
output_size_t = output_size


j_range = range_t('j_range', 0, 8)
lanes_t = range_t('lanes_t', 1, 2**24)
segment_t = range_t('segment_t', 0, 4)
t_len_t = range(1, max_size_t - 65)
idx_t = refine(size_nat, lambda x: x <= 15)
working_vector_t = array_t(uint64_t, 16)


def h(a: refine(vlbytes_t, lambda x: array.length(x) < max_size_t - 2 * line_size), nn: output_size_t) \
        -> contract(vlbytes_t, lambda a, nn: True, lambda a, nn, res: array.length(res) == nn):
    res = blake2b(a, array([]), nn)
    return res


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


def h_prime(t_len: refine(size_nat, lambda x: 1 <= t_len and t_len + 64 <= max_size_t),
            x: refine(vlbytes_t, lambda x: array.length(x) + 4 <= max_size_t - 2 * line_size)) \
        -> contract(vlbytes_t,
                    lambda t_len, x: True,
                    lambda t_len, x, res: array.length(x) == compute_variable_length_output_size(t_len)):
    t_with_x = array.create(array.length(x) + 4, uint8(0))
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


def low_bits(x: uint64_t) -> uint64_t:
    return uint64(uint32(x))


def g(v: working_vector_t, a: idx_t, b: idx_t, c: idx_t, d: idx_t) -> working_vector_t:
    v_res = array.copy(v)
    v_res[a] = v_res[a] + v_res[b] + \
        uint64(2) * low_bits(v_res[a]) * low_bits(v_res[b])
    v_res[d] = uint64_t.rotate_right(v_res[d] ^ v_res[a], 32)
    v_res[c] = v_res[c] + v_res[d] + \
        uint64(2) * low_bits(v_res[c]) * low_bits(v_res[d])
    v_res[b] = uint64_t.rotate_right(v_res[b] ^ v_res[c], 24)
    v_res[a] = v_res[a] + v_res[b] + \
        uint64(2) * low_bits(v_res[a]) * low_bits(v_res[b])
    v_res[d] = uint64_t.rotate_right(v_res[d] ^ v_res[a], 16)
    v_res[c] = v_res[c] + v_res[d] + \
        uint64(2) * low_bits(v_res[c]) * low_bits(v_res[d])
    v_res[b] = uint64_t.rotate_right(v_res[b] ^ v_res[c], 63)
    return v_res


def P(input: bytes_t(line_size)) -> bytes_t(line_size):
    v = array.create(16, uint64(0))
    for i in range(8):
        v[2 * i] = vlbytes.to_uint64_le(input[i * 16:i * 16 + 8])
        v[2 * i + 1] = vlbytes.to_uint64_le(input[i * 16 + 8:(i + 1) * 16])
    v = g(v, 0, 4, 8, 12)
    v = g(v, 1, 5, 9, 13)
    v = g(v, 2, 6, 10, 14)
    v = g(v, 3, 7, 11, 15)
    v = g(v, 0, 5, 10, 15)
    v = g(v, 1, 6, 11, 12)
    v = g(v, 2, 7, 8, 13)
    v = g(v, 3, 4, 9, 14)
    return vlbytes.from_uint64s_le(v)


def xor_blocks(X: bytes_t(block_size), Y: bytes_t(block_size)) -> bytes_t(block_size):
    output = array.create(block_size, uint8(0))
    for i in range(block_size // 8):
        output[i * 8:(i + 1) * 8] = vlbytes.from_uint64_be(vlbytes.to_uint64_be(
            X[8 * i:8 * (i + 1)]) ^ vlbytes.to_uint64_be(Y[8 * i:8 * (i + 1)]))
    return output


def extract_block_column(j: j_range, block: bytes_t(block_size)) -> bytes_t(line_size):
    col = array.create(line_size, uint8(0))
    for i in range(8):
        offset = i * line_size + j * 16
        col[i * 16:(i + 1) * 16] = block[offset:offset + 16]
    return col


def update_block_column(j: j_range, col: bytes_t(line_size), block: bytes_t(block_size)) -> bytes_t(block_size):
    output = array.copy(block)
    for i in range(8):
        offset = i * line_size + j * 16
        output[offset:offset + 16] = col[i * 16:(i + 1) * 16]
    return output


def G(X: bytes_t(block_size), Y: bytes_t(block_size)) -> bytes_t(block_size):
    R = array.create(block_size, uint8(0))
    R[:] = xor_blocks(X, Y)
    Q = array.copy(R)
    for i in range(8):
        row = array.copy(Q[i * line_size:(i + 1) * line_size])
        row = P(row)
        Q[line_size * i:line_size * (i + 1)] = row
    for j in range(8):
        col = extract_block_column(j, Q)
        col = P(col)
        Q = update_block_column(j, col, Q)
    return xor_blocks(Q, R)


def extend_to_block(input: refine(vlbytes_t, lambda x: array.length(x) <= block_size)) -> bytes_t(block_size):
    output = array.create(block_size, uint8(0))
    output[:array.length(intput)] = input
    return output


def block_offset(lanes: lanes_t, columns: size_nat, i: size_nat, j: size_nat) \
    -> contract(size_nat,
                lambda lanes, columns, i, j: columns <= 4 and lanes *
                columns * block_size <= max_size_t and
                i < lanes and j < columns,
                lambda lanes, columns, i, j, res: res <= (columns * lanes - 1) * block_size):
    return block_size * (columns * i + j)


def xor_last_column(lanes: lanes_t, columns: size_nat, memory: vlbytes) \
    -> contract(vlbytes,
                lambda lanes, columns, memory: columns <= 4 and columns *
                columns * block_size <= max_size_t and
                array.length(memory) == lanes * columns * block_size,
                lambda lanes, columns, memory, res: array.length(res) ==
                lanes * columns * block_size):
    output = array.create(block_size, uint8(0))
    offset = block_offset(lanes, columns, 0, columns - 1)
    output = memory[offset:offset + block_size]
    for i in range(lanes - 1):
        offset = block_offset(lanes, columns, i + 1, columns - 1)
        output = xor_blocks(
            output, memory[offset:offset + block_size])
    return output


def pseudo_random_generation(j1: size_nat, r_size: size_nat) \
    -> contract(size_nat,
                lambda j1, r_size: r_size != 0,
                lambda j1, r_size, res: res < r_size):
    tmp = (j1 * j1) // (2**32)
    tmp = (tmp * r_size) // (2**32)
    return r_size - 1 - tmp


def seeds_length(lanes: lanes_t, columns: size_nat) \
    -> contract(size_nat,
                lambda lanes, columns: columns <= 4 and lanes *
                columns * block_size <= max_size_t,
                lambda lanes, columns, res: True):
    segment_length = columns // 4
    tmp = segment_length // line_size + 1
    return tmp * line_size * 2


def generate_seeds(lanes: lanes_t, columns: size_nat, i: size_nat, iterations: size_nat, t: size_nat, segment: segment_t) \
    -> contract(vlarray_t(uint32),
                lambda lanes, columns, i, iterations, t, segment: columns <= 4 and lanes *
                columns * block_size <= max_size_t and i < lanes and
                t < iterations,
                lambda lanes, columns, i, iterations, t, segment, res:
                array.length(res) == seeds_length(lanes, columns)):
    segment_length = columns // 4
    pseudo_rands_rounds = segment_length // line_size + 1
    pseudo_rands_size = pseudo_rands_rounds * line_size * 2
    pseudo_rands = array.create(pseudo_rands_size, uint32(0))
    for ctr in range(pseudo_rands_rounds):
        zero_block = array.create(block_size, uint8(0))
        concat_block = array.create(block_size, uint8(0))
        concat_block[0:8] = vlbytes.from_uint64_le(uint64(t))
        concat_block[8:16] = vlbytes.from_uint64_le(uint64(i))
        concat_block[16:24] = vlbytes.from_uint64_le(uint64(segment))
        concat_block[24:32] = vlbytes.from_uint64_le(uint64(lanes * columns))
        concat_block[32:40] = vlbytes.from_uint64_le(uint64(iterations))
        concat_block[40:48] = vlbytes.from_uint64_le(uint64(argon_type))
        concat_block[48:56] = vlbytes.from_uint64_le(uint64(ctr + 1))
        arg_block = G(zero_block, concat_block)
        address_block = G(zero_block, arg_block)
        addresses_list = vlbytes.to_uint32s_le(address_block)
        pseudo_rands[ctr * line_size *
                     2:(ctr + 1) * line_size * 2] = addresses_list
    return pseudo_rands


def map_indexes(t: size_nat, segment: segment_t, lanes: lanes_t, columns: size_nat,
                idx: size_nat, i: size_nat, j: size_nat, j1: uint32_t, j2: uint32_t) \
    -> contract(Tuple[size_nat, size_nat],
                lambda t, segment, lanes, columns, idx, i, j, j1, j2:
                columns <= 4 and lanes * columns * block_size <= max_size_t and
                idx < columns // 4 and i < lanes and j < columns and
                j > 2 if t == 0 else True and j == segment *
                (columns // 4) + idx,
                lambda t, segment, lanes, columns, idx, i, j, j1, j2, res:
                res[0] < lanes and res[1] < columns):
    segment_length = columns // 4
    if t == 0 and segment == 0:
        i_prime = i
    else:
        i_prime = uint32.to_int(j2) % lanes
    if t == 0:
        if segment == 0 or i == i_prime:
            r_size = j - 1
        elif idx == 0:
            r_size = segment * segment_length - 1
        else:
            r_size = segment * segment_length
    elif i == i_prime:  # same_lane
        r_size = columns - segment_length + idx - 1
    elif idx == 0:
        r_size = columns - segment_length - 1
    else:
        r_size = columns - segment_length
    if t != 0 and segment != 3:
        r_start = (segment + 1) * segment_length
    else:
        r_start = 0
    j_prime_tmp = pseudo_random_generation(uint32.to_int(j1), r_size)
    j_prime = (r_start + j_prime_tmp) % columns
    return (i_prime, j_prime)


def fill_segment(h0: bytes_t(64), iterations: size_nat, segment: segment_t, t_len: t_len_t,
                 lanes: lanes_t, columns: size_nat, t: size_nat, i: size_nat, memory: vlbytes_t) \
    -> contract(vlbytes_t,
                lambda h0, iterations, segment, t_len, lanes, columns, t, i, memory:
                columns <= 4 and lanes * columns * block_size <= max_size_t and
                i < lanes and j < columns and
                array.length(memory) == lanes * columns * block_size,
                lambda h0, iterations, segment, t_len, lanes, columns, t, i, memory, res:
                array.length(res) == lanes * columns * block_size):
    output = array.copy(memory)
    segment_length = columns // 4
    counter = 0
    pseudo_rands_size = seeds_length(lanes, columns)
    pseudo_rands = generate_seeds(lanes, columns, i, iterations, t, segment)
    for idx in range(segment_length):
        j = segment * segment_length + idx
        if t == 0 and j < 2:
            h0_i_j = array.create(72, uint8(0))
            h0_i_j[0:64] = h0
            h0_i_j[64:68] = vlbytes.from_uint32_le(uint32(j))
            h0_i_j[68:72] = vlbytes.from_uint32_le(uint32(i))
            new_block = h_prime(block_size, h0_i_j)
            offset = block_offset(lanes, columns, i, j)
            output[offset:offset + block_size] = new_block
        else:
            j1 = pseudo_rands[2 * idx]
            j2 = pseudo_rands[2 * idx + 1]
            (i_prime, j_prime) = map_indexes(
                t, segment, lanes, columns, idx, i, j, j1, j2)
            offset = block_offset(lanes, columns, i, (j - 1) % columns)
            arg1 = output[offset:offset + block_size]
            offset = block_offset(lanes, columns, i_prime, j_prime)
            arg2 = output[offset:offset + block_size]
            new_block = G(arg1, arg2)
            if t != 0:
                offset = block_offset(lanes, columns, i, j)
                old_block = output[offset:offset + block_size]
                output[offset:offset +
                       block_size] = xor_blocks(new_block, old_block)
            else:
                offset = block_offset(lanes, columns, i, j)
                output[offset:offset + block_size] = new_block
    return output


def argon2i(p: vlbytes, s: vlbytes, lanes: lanes_t, t_len: t_len_t, m: size_nat,
            iterations: size_nat, x: vlbytes, k: vlbytes) \
    -> contract(vlbytes_t,
                lambda p, s, lanes, t_len, m, iterations, x, k: array.length(s >= 8) and
                m >= 8 * lanes and (m + 4 * lanes) * block_size <= max_size_t and
                iterations >= 1 and array.length(x) + 4 <= max_size_t - 2 * line_size and
                array.length(p) + array.length(s) + array.length(x) +
                array.length(k) + 11 * 4 <= max_size_t - 2 * line_size,
                lambda p, s, lanes, t_len, m, iterations, x, k, res:
                array.length(res) == compute_variable_length_output_size(t_len)):
    h0_arg = array.create(10 * 4 + array.length(p) +
                          array.length(k) + array.length(s) + array.length(x), uint8(0))
    h0_arg[0:4] = vlbytes.from_uint32_le(uint32(lanes))
    h0_arg[4:8] = vlbytes.from_uint32_le(uint32(t_len))
    h0_arg[8:12] = vlbytes.from_uint32_le(uint32(m))
    h0_arg[12:16] = vlbytes.from_uint32_le(uint32(iterations))
    h0_arg[16:20] = vlbytes.from_uint32_le(uint32(version_number))
    h0_arg[20:24] = vlbytes.from_uint32_le(uint32(argon_type))
    h0_arg[24:28] = vlbytes.from_uint32_le(uint32(array.length(p)))
    offset = 28 + array.length(p)
    h0_arg[28:offset] = p
    h0_arg[offset:offset +
           4] = vlbytes.from_uint32_le(uint32(array.length(s)))
    h0_arg[offset + 4:offset + 4 + array.length(s)] = s
    offset = offset + 4 + array.length(s)
    h0_arg[offset:offset +
           4] = vlbytes.from_uint32_le(uint32(array.length(k)))
    h0_arg[offset + 4:offset + 4 + array.length(k)] = k
    offset = offset + 4 + array.length(k)
    h0_arg[offset:offset +
           4] = vlbytes.from_uint32_le(uint32(array.length(x)))
    h0_arg[offset + 4:offset + 4 + array.length(x)] = x
    offset = offset + 4 + array.length(x)
    h0 = h(h0_arg, 64)
    columns = 4 * (m // (4 * lanes))
    number_of_blocks = lanes * columns
    memory_size = block_size * number_of_blocks
    memory = array.create(memory_size, uint8(0))
    for t in range(iterations):
        for segment in range(4):
            for i in range(lanes):
                memory = fill_segment(h0, iterations, segment,
                                      t_len, lanes, columns, t, i, memory)
    final_block = xor_last_column(lanes, columns, memory)
    return h_prime(t_len, final_block)
