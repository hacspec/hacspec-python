#!/usr/bin/env python3

from hacspec.speclib import *
from sha2 import sha256

# Influences signature length, not security
w_four = uint32(4)
w_sixteen = uint32(16)


# Parameters
# n := length (message, signature, key), SHA2 output length
n = 32
w = w_sixteen
log_w = 4

length1 = uint32(int(speclib.ceil(8*n // log_w)))
tmp = uint32.to_int(length1) * (uint32.to_int(w) - 1)
tmp = speclib.log(tmp, 2)
length2 = uint32(int(tmp // log_w + 1))
length = length1 + length2

# Types


key_t = bytes_t(n)
sk_t = array_t(key_t, uint32.to_int(length))
pk_t = array_t(key_t, uint32.to_int(length))
sig_t = array_t(key_t, uint32.to_int(length))
address_t = array_t(uint32_t, 8)
key_pair_t = Tuple[sk_t, pk_t, address_t]
digest_t = bytes_t(32)
seed_t = bytes_t(n)
chain_t = Tuple[address_t, vlbytes_t]

# F: SHA2-256(toByte(0, 32) || KEY || M),
# H: SHA2-256(toByte(1, 32) || KEY || M),
# H_msg: SHA2-256(toByte(2, 32) || KEY || M),
# PRF: SHA2-256(toByte(3, 32) || KEY || M).


@typechecked
def hash(prefix: key_t, key: key_t, m: vlbytes_t) -> digest_t:
    h_in = bytes.concat(prefix, key)
    h_in = bytes.concat(h_in, m)
    return sha256(bytes(h_in))


@typechecked
def F(key: key_t, m: vlbytes_t) -> digest_t:
    return hash(bytes.from_nat_be(nat(0), nat(32)), key, m)


@typechecked
def H(key: key_t, m: vlbytes_t) -> digest_t:
    return hash(bytes.from_nat_be(nat(1), nat(32)), key, m)


@typechecked
def H_msg(key: key_t, m: vlbytes_t) -> digest_t:
    return hash(bytes.from_nat_be(nat(2), nat(32)), key, m)


@typechecked
def PRF(key: key_t, m: address_t) -> digest_t:
    m_ = vlbytes.from_uint32_be(m[0])
    m_ = vlbytes.concat(m_, vlbytes.from_uint32_be(m[1]))
    m_ = vlbytes.concat(m_, vlbytes.from_uint32_be(m[2]))
    m_ = vlbytes.concat(m_, vlbytes.from_uint32_be(m[3]))
    m_ = vlbytes.concat(m_, vlbytes.from_uint32_be(m[4]))
    m_ = vlbytes.concat(m_, vlbytes.from_uint32_be(m[5]))
    m_ = vlbytes.concat(m_, vlbytes.from_uint32_be(m[6]))
    m_ = vlbytes.concat(m_, vlbytes.from_uint32_be(m[7]))
    return hash(bytes.from_nat_be(nat(3), nat(32)), key, m_)


# Address is a 32-byte array with the following definition
# 4-byte: layer address
# 8-byte: tree address
# 4-byte: type: 0 for OTS, 1 for L-tree, 2 for hash tree
# 4-byte: OTS address, L-tree address, padding (0)
# 4-byte: chain address, tree height, tree height
# 4-byte: hash address, tree index, tree index
# 4-byte: key and mask

@typechecked
def set_chain_address(adr: address_t, h_adr: uint32_t) -> address_t:
    result = adr[:]
    result[-3] = h_adr
    return result


@typechecked
def set_hash_address(adr: address_t, h_adr: uint32_t) -> address_t:
    result = adr[:]
    result[-2] = h_adr
    return result


@typechecked
def set_key_and_mask(adr: address_t, kam: uint32_t) -> address_t:
    result = adr[:]
    result[-1] = kam
    return result

# Input: Input string X, start index i, number of steps s, seed SEED, address ADRS
# Output: value of F iterated s times on X


@typechecked
def wots_chain(x: bytes_t, start: int, steps: int, seed: seed_t, adr: address_t) -> chain_t:
    hmo = bytes.copy(x)
    for i in range(start, start + steps):
        adr = set_hash_address(adr, uint32(i))
        adr = set_key_and_mask(adr, uint32(0))
        key = PRF(seed, adr)
        adr = set_key_and_mask(adr, uint32(1))
        bm = PRF(seed, adr)
        fin = bytes([])
        for (a, b) in zip(hmo, bm):
            fin = bytes.concat(fin, bytes([a ^ b]))
        hmo = F(key, fin)
    return adr, hmo


@typechecked
def key_gen(adr: address_t, seed: seed_t) -> key_pair_t:
    # TODO: we need separate functions here for xmss later.
    sk = sk_t.create(length, key_t.create(n, uint8(0)))
    pk = pk_t.create(length, key_t.create(n, uint8(0)))
    for i in range(0, uint32.to_int(length)):
        sk_i: bytes_t = bytes.create_random_bytes(n)
        adr = set_chain_address(adr, uint32(i))
        adr, pk_i = wots_chain(sk_i, 0, uint32.to_int(w)-1, seed, adr)
        sk[i] = sk_i
        pk[i] = pk_i
    return (sk, pk, adr)


@typechecked
def base_w(msg: vlbytes_t, l: uint32_t) -> vlbytes_t:
    i = 0
    out = 0
    total = 0
    bits = 0
    basew = vlbytes([])
    for consumed in range(0, uint32.to_int(l)):
        if bits == 0:
            total = uint8.to_int(msg[i])
            i = i + 1
            bits = bits + 8
        bits = bits - int(log_w)
        bw = (total >> bits) & int(uint32.to_int(w) - 1)
        basew = array.concat(basew, bytes([uint8(bw)]))
        out = out + 1
    return basew

@typechecked
def wots_msg(msg: digest_t) -> vlbytes_t:
    csum = 0
    m = base_w(msg, length1)
    for i in range(0, uint32.to_int(length1)):
        csum = csum + uint32.to_int(w) - 1 - uint32.to_int(m[i])
    csum = nat(csum << int(8 - ((uint32.to_int(length2) * log_w) % 8)))
    length2_bytes = speclib.ceil((uint32.to_int(length2) * log_w) // 8)
    csum_bytes = bytes.from_nat_be(csum, length2_bytes)
    m = array.concat(m, base_w(csum_bytes, length2))
    return m


@typechecked
def wots_sign(msg: digest_t, sk: sk_t, adr: address_t, seed: seed_t) -> sig_t:
    m = wots_msg(msg)
    sig = sig_t.create(length, key_t.create(n, uint8(0)))
    for i in range(0, uint32.to_int(length)):
        adr = set_chain_address(adr, uint32(i))
        adr, sig_i = wots_chain(sk[i], 0, uint32.to_int(m[i]), seed, adr)
        sig[i] = sig_i
    return sig


@typechecked
def wots_verify(pk: pk_t, msg: digest_t, sig: sig_t, adr: address_t, seed: seed_t) -> Tuple[pk_t, address_t]:
    m = wots_msg(msg)
    pk2 = pk_t.create(length, key_t.create(n, uint8(0)))
    for i in range(0, uint32.to_int(length)):
        adr = set_chain_address(adr, uint32(i))
        m_i = uint32.to_int(m[i])
        adr, pk_i = wots_chain(sig[i], m_i, uint32.to_int(w) - 1 - m_i, seed, adr)
        pk2[i] = pk_i
    return (pk2, adr)
