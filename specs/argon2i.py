from speclib import *
from blake2b import blake2b
from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple, Callable, Type

version_number = uint8(0x13)
argon_type = 1
block_size = 1024
line_size = 128

max_size_t = 2**64 - 1
size_nat = refine(nat, lambda x: x <= max_size_t)

output_size_t = refine(nat, lambda x: x <= 64)


def contract(T: Type[T], pre: Callable[[List[Type]], bool], post: Callable[[List[Type], T], bool]):
    return T


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


def h_prime(t_len: refine(size_nat, lambda x: 1 <= t_len and t_len + 64 <= max_size_t),
            x: refine(vlbytes_t, lambda x: vlbytes.length(x) + 4 <= max_size_t - 2 * line_size)) \
        -> refine(vlbytes_t, lambda x: vlbytes.length(x) == compute_variable_length_output_size(t_len)):
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


working_vector_t = array_t(uint64_t, 16)


def g(v: working_vector_t, a: idx_t, b: idx_t, c: idx_t, i4: idx_t) -> working_vector_t:
    v_res = array.copy(v)
    v_res[a] = v[a] + v[b] + uint64(2) * low_bits(v[a]) * low_bits(v[b])
    v_res[d] = uint64_t.rotate_right(v[d] ^ v[a], 32)
    v_res[c] = v[c] + v[d] + uint64(2) * low_bits(v[c]) * low_bits(v[d])
    v_res[b] = uint64_t.rotate_right(v[b] ^ v[c], 24)
    v_res[a] = v[a] + v[b] + uint64(2) * low_bits(v[a]) * low_bits(v[b])
    v_res[d] = uint64_t.rotate_right(v[d] ^ v[a], 16)
    v_res[c] = v[c] + v[d] + uint64(2) * low_bits(v[c]) * low_bits(v[d])
    v_res[b] = uint64_t.rotate_right(v[b] ^ v[c], 63)
    return v_res


def P(input: bytes_t(line_size)) -> bytes_t(line_size):
    v = array.create(16, uint64(0))
    for i in range(8):
        v[2 * i] = vlbytes.to_uint64_le(input[i * 16:i * 16 + 8])
        v[2 * i + 1] = vlbytes.to_uint64_le(v[i * 16 + 8:(i + 1) * 16])
    v = g(v, 0, 4, 8, 12)
    v = g(v, 1, 5, 9, 13)
    v = g(v, 2, 6, 10, 14)
    v = g(v, 3, 7, 11, 15)
    v = g(v, 0, 5, 10, 15)
    v = g(v, 1, 6, 11, 12)
    v = g(v, 2, 7, 8, 13)
    v = g(v, 3, 4, 9, 14)
    return v


def xor_blocks(X: bytes_t(block_size), Y: bytes_t(block_size)) -> bytes_t(block_size):
    output = array.create(block_size, uint8(0))
    for i in range(block_size // 8):
        output[i * 8:(i + 1) * 8] = vlbytes.from_uint64_be(vlbytes.to_uint64_be(
            X[8 * i:8 * (i + 1)]) ^ vlbytes.to_uint64_be(Y[8 * i:8 * (i + 1)]))
    return output


def extract_block_column(j: range_t(0, 8), block: bytes_t(block_size)) -> bytes_t(line_size):
    col = array.create(line_size, uint8(0))
    for i in range(8):
        offset = i * line_size + j * 16
        col[i * 16:(i + 1) * 16] = block[offset:offset + 16]
    return col


def update_block_column(j: range_t(0, 8), col: bytes_t(line_size), block: bytes_t(block_size)) -> bytes_t(block_size):
    output = array.copy(block)
    for i in range(8):
        offset = i * line_size + j * 16
        output[offset:offset + 16] = col[i * 16:(i + 1) * 16]
    return block


def G(X: bytes_t(block_size), Y: bytes_t(block_size)) -> bytes_t(block_size):
    R = array.create(block_size, uint8(0))
    R[:] = xor_blocks(X, Y)
    Q = array.copy(R)
    for i in range(8):
        row = array.copy(Q[i * line_size:(i + 1) * line_size])
        row = P(row)
        Q[line_size * i:line_size * (i + 1)] = row
    for j in range(8):
        col = extract_block_column(j, block)
        col = P(col)
        Q = update_block_column(j, col, Q)
    return xor_blocks(Q, R)


def extend_to_block(input: refine(vlbytes_t, lambda x: vlbytes.length(x) <= block_size)) -> bytes_t(block_size):
    output = array.create(block_size, uint8(0))
    output[:vlbytes.length(intput)] = input
    return output


lanes_t = range_t(1, 2**24)


def block_offset(lanes: lanes_t, columns: size_nat, i: size_nat, j: size_nat) \
    -> contract(size_nat,
                lambda args: args[1] <= 4 and args[0] *
                args[1] * block_size <= max_size_t and
                args[2] < args[0] and args[3] < args[1],
                lambda args, res: res <= (args[1] * args[2] - 1) * block_size):
    block_size * (columns * i + j)


def xor_last_column(lanes: lanes_t, columns: size_nat, memory: vlbytes) \
    -> contract(vlbytes,
                lambda args: args[1] <= 4 and args[0] *
                args[1] * block_size <= max_size_t and
                vlbytes.length(args[2]) == args[0] * args[1] * block_size,
                lambda args, res: vlbytes.length(res) == args[0] * args[1] * block_size):
    output = array.create(block_size, uint8(0))
    block_offset = block_offset(lanes, columns, 0, columns - 1)
    output = memory[block_offset:block_offset + block_size]
    for i in range(lanes - 1):
        block_offset = block_offset(lanes, columns, 0, columns - 1)
        output = xor_blocks(
            block, memory[block_offset:block_offset + block_size])
    return output


def pseudo_random_generation(j1: size_nat, r_size: size_nat) \
    -> contract(size_nat,
                lambda args: args[1] != 0,
                lambda args, res: res < args[1]):
    tmp = (j1 * j1) // (2**32)
    tmp = (tmp * r_size) // (2**32)
    return r_size - 1 - tmp


def seeds_length(lanes: lanes_t, columns: size_nat) \
    -> contract(size_nat,
                lambda args: args[1] <= 4 and args[0] *
                args[1] * block_size <= max_size_t,
                lambda args, res: True):
    segment_length = columns // 4
    tmp = segment_length // line_size + 1
    return tmp * line_size * 2


segment_t = range_t(0, 4)


def generate_seeds(lanes: lanes_t, columns: size_nat, i: size_nat, iterations: size_nat, t: size_nat, segment: segment_t) \
    -> contract(vlarray_t(uint32),
                lambda args: args[1] <= 4 and args[0] *
                args[1] * block_size <= max_size_t and i < args[0] and
                args[4] < args[3],
                lambda args, res: vlarray.length(res) == seeds_length(args[0], args[1])):
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
        concat_block[48:56] = vlbytes.from_uint64_le(uint64(ctr))
        arg_block = G(zero_block, concat_block)
        adress_block = G(zero_block, arg_block)
        adresses_list = vlbytes.to_uint32s_le(address_block)
        pseudo_rands[ctr * line_size *
                     2:(ctr + 1) * line_size * 2] = addresses_list
    return pseudo_rands


def map_indexes(t: size_nat, segment: segment_t, lanes: lanes_t, columns: size_nat, idx: size_nat, i: size_nat, j: size_nat, j1: uint32_t, j2: uint32_t) \
    -> contract(Tuple[size_nat, size_nat],
                lambda args: args[3] <= 4 and args[2] * args[3] * block_size <= max_size_t and
                args[4] < args[3] // 4 and args[5] < args[2] and args[6] < args[3] and
                args[6] > 2 if args[0] == 0 else True and args[6] == args[1] *
                (args[3] // 4) + args[4],
                lambda args, res: res[0] < args[2] and res[1] < args[3]):
    segment_length = columns // 4
    if t == 0 and segment == 0:
        i_prime = i
    else:
        i_prime = uint32.to_int(j2) % lanes
    if t == 0:
        if segment == 0 or i == i_prime:
            r_size = j - 1
        else:
            if idx == 0:
                r_size = segment * segment_length - 1
            else:
                r_size = segment * segment_length
    else:
        if i == i_prime:
            r_size = columns - segment_length + idx - 1
        else:
            if idx == 0:
                r_size = columns - segment_length + 1
            else:
                r_size = columns - segment_length
    if t != 0 and segment != 3:
        r_start = (segment + 1) * segment_length
    else:
        r_start = 0
    j_prime_tmp = pseudo_random_generation(uint32.to_int(j1), r_size)
    j_prime = (r_start + j_prime_tmp) % columns
    return (i_prime, j_prime)


t_len_t = range(1, max_size_t - 65)


def fill_segment(h0: bytes_t(64), iterations: size_nat, segment:segment_t, t_len: t_len_t, lanes: lanes_t, columns: size_nat, t: size_nat, i: size_nat, memory: vlbytes_t) \
    -> contract(vlbytes_t,
                lambda args: args[6] <= 4 and args[5] * args[6] * block_size <= max_size_t and
                args[7] < args[1] and args[8] < args[5] and
                vlbytes.length(args[9]) == args[5] * args[6] * block_size,
                lambda args, res: vlbytes.length(res) == args[5] * args[6] * block_size):
    output = array.copy(memory)
    segment_length = columns // 4
    counter = 0
    pseudo_rands_size = seeds_length(lanes, columns)
    pseudo_rands = generate_seeds(lanes, columns, i, iterations, t, segment)
    for idx in range(segment_length):
        j = segment * segment_length + idx
        if t == 0 and j < 2:
            h0_i_j = array.create(72)
            h0_i_j[0:64] = h0
            h0_i_j[64:68] = vlbytes.from_uint32_le(uint32(i))
            h0_i_j[68:72] = vlbytes.from_uint32_le(uint32(i))
            new_block = h_prime(block_size, h0_i_j)
            block_offset = block_offset(lanes, columns, i, j)
            output[block_offset:block_offset + block_size] = new_block
        else:
            j1 = pseudo_rands[2 * idx]
            j2 = pseudo_rands[2 * idx + 1]
            (i_prime, j_prime) = map_indexes(
                t, segment, lanes, columns, i, j, j1, j2)
            block_offset = block_offset(lanes, columns, i, (j - 1) % columns)
            arg1 = memory[block_offset:block_offset + block_size]
            block_offset = block_offset(lanes, columns, i_prime, j_prime)
            arg2 = memory[block_offset:block_offset + block_size]
            new_block = G(arg1, arg2)
            if t != 0:
                block_offset = block_offset(lanes, columns, i, j)
                old_block = memory[block_offset:block_offset + block_size]
                output[block_offset:block_offset +
                       block_size] = xor_blocks(new_block, old_blocks)
            else:
                block_offset = block_offset(lanes, columns, i, j)
                output[block_offset:block_offset + block_size] = new_block
    return output


def argon2i(p: vlbytes, s: vlbytes, lanes: lanes_t, t_len: t_len_t, m: size_nat, iterations: size_nat, x: vlbytes, k: vlbytes) \
    -> contract(vlbytes_t,
                lambda args: vlbytes.length(args[1] >= 8) and
                args[4] >= 8 * args[2] and (args[4] + 4 * args[2]) * block_size <= max_size_t and
                args[5] >= 1 and vlbytes.length(args[6]) + 4 <= max_size_t - 2 * line_size and
                vlbytes.length(args[7]) + vlbytes.length(args[0]) + vlbytes.length(args[1]) +
                vlbytes.length(args[6]) + 11 * 4 <= max_size_t - 2 * line_size,
                lambda args, res: vlbytes.length(res) == compute_variable_length_output_size(args[3])):
    h0_arg = array.create(10 * 4 + vlbytes.length(p) +
                          vlbytes.length(k) + vlbytes.length(s) + vlbytes.length(x), uint8(0))
    h0_arg[0:4] = vlbytes.from_uint32_le(uint32(lanes))
    h0_arg[4:8] = vlbytes.from_uint32_le(uint32(t_len))
    h0_arg[8:12] = vlbytes.from_uint32_le(uint32(m))
    h0_arg[12:16] = vlbytes.from_uint32_le(uint32(iterations))
    h0_arg[16:20] = vlbytes.from_uint32_le(uint32(version_number))
    h0_arg[20:24] = vlbytes.from_uint32_le(uint32(argon_type))
    h0_arg[24:28] = vlbytes.from_uint32_le(uint32(vlbytes.length(p)))
    offset = 28 + vlbytes.length(p)
    h0_arg[28:offset] = p
    h0_arg[offset:offset +
           4] = vlbytes.from_uint32_le(uint32(vlbytes.length(s)))
    h0_arg[offset + 4:offset + 4 + vlbytes.length(s)] = s
    offset = offset + 4 + vlbytes.length(s)
    h0_arg[offset:offset +
           4] = vlbytes.from_uint32_le(uint32(vlbytes.length(k)))
    h0_arg[offset + 4:offset + 4 + vlbytes.length(k)] = k
    offset = offset + 4 + vlbytes.length(k)
    h0_arg[offset:offset +
           4] = vlbytes.from_uint32_le(uint32(vlbytes.length(x)))
    h0_arg[offset + 4:offset + 4 + vlbytes.length(x)] = x
    offset = offset + 4 + vlbytes.length(x)
    h0 = h(h0_arg, 64)
    columns = 4 * (m // (4 * lanes))
    number_of_blocks = lanes * columns
    memory_size = block_size * number_of_blocks
    print(memory_size)
    memory = array.create(memory_size, uint8(0))
    for t in range(iterations):
        for segment in range(4):
            for i in range(lanes):
                memory = fill_segment(h0, iterations, segment,
                                      t_len, lanes, columns, t, i, memory)
    final_block = xor_last_column(lanes, columns, memory)
    return h_prime(t_len, final_block)
