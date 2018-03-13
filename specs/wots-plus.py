#!/usr/bin/env python3

from speclib import *
import sha2
import math

# Influences signature length, not security
w_four = uint32(4)
w_sixteen = uint32(16)

# F: SHA2-256(toByte(0, 32) || KEY || M),
# H: SHA2-256(toByte(1, 32) || KEY || M),
# H_msg: SHA2-256(toByte(2, 32) || KEY || M),
# PRF: SHA2-256(toByte(3, 32) || KEY || M).


def hash(prefix: array[uint8], key: array[uint8], m: array[uint8]) -> array[uint8]:
    h_in = array.create(uint8(0), 0)
    h_in.extend(prefix)
    h_in.extend(key)
    h_in.extend(m)
    h = sha2.sha256(h_in)
    return array.uint32s_to_uint8s_be(h)


def F(key: array[uint8], m: array[uint8]) -> array[uint8]:
    return hash(array.create(uint8(0), 32), key, m)


def H(key: array[uint8], m: array[uint8]) -> array[uint8]:
    return hash(array.create(uint8(1), 32), key, m)


def H_msg(key: array[uint8], m: array[uint8]) -> array[uint8]:
    return hash(array.create(uint8(2), 32), key, m)


def PRF(key: array[uint8], m: array[uint8]) -> array[uint8]:
    return hash(array.create(uint8(3), 32), key, m)


# Parameters
# n := length (message, signature, key), SHA2 output length
n = 32  # type: int
w = w_four

length1 = uint32(int(math.ceil(8*n / math.log(uint32.int_value(w), 2))))
tmp = uint32.int_value(length1) * (uint32.int_value(w) - 1)
length2 = uint32(int(math.log(tmp, 2) // math.log(uint32.int_value(w), 2) + 1))
length = length1 + length2

# Address is a 32-byte array with the following definition
# 4-byte: layer address
# 8-byte: tree address
# 4-byte: type: 0 for OTS, 1 for L-tree, 2 for hash tree
# 4-byte: OTS address, L-tree address, padding (0)
# 4-byte: chain address, tree height, tree height
# 4-byte: hash address, tree index, tree index
# 4-byte: key and mask
address = NewType('address', array[uint8])

# key pair type
# I can't get mypy to handle these types :(
SecretKey = NewType('SecretKey', array[array[uint8]])
PublicKey = NewType('PublicKey', array[array[uint8]])
KeyPair = NewType('KeyPair', Tuple[SecretKey, PublicKey])


def set_chain_address(adr: address, h_adr: uint32) -> address:
    result = adr[:]
    result[20] = uint8((h_adr.as_int() & 0xFF000000) >> 24)
    result[21] = uint8((h_adr.as_int() & 0xFF0000) >> 16)
    result[22] = uint8((h_adr.as_int() & 0xFF00) >> 8)
    result[23] = uint8(h_adr.as_int() & 0xFF)
    return result


def set_hash_address(adr: address, h_adr: uint32) -> address:
    result = adr[:]
    result[24] = uint8((h_adr.as_int() & 0xFF000000) >> 24)
    result[25] = uint8((h_adr.as_int() & 0xFF0000) >> 16)
    result[26] = uint8((h_adr.as_int() & 0xFF00) >> 8)
    result[27] = uint8(h_adr.as_int() & 0xFF)
    return result


def set_key_and_mask(adr: address, kam: uint32) -> address:
    result = adr[:]
    result[28] = uint8((kam.as_int() & 0xFF000000) >> 24)
    result[29] = uint8((kam.as_int() & 0xFF0000) >> 16)
    result[30] = uint8((kam.as_int() & 0xFF00) >> 8)
    result[31] = uint8(kam.as_int() & 0xFF)
    return result

# Input: Input string X, start index i, number of steps s, seed SEED, address ADRS
# Output: value of F iterated s times on X


def wots_chain(x: array[uint8], index: int, steps: int, seed: array[uint8], adr: address) -> array[uint8]:
    if steps == 0:
        return x
    if index + steps > (w.as_int() - 1):
        return array([])
    tmp = wots_chain(x, index, steps - 1, seed, adr)

    adr = set_hash_address(adr,  uint32(index + steps - 1))
    adr = set_key_and_mask(adr, uint32(0))
    key = PRF(seed, adr)
    adr = set_key_and_mask(adr, uint32(1))
    bm = PRF(seed, adr)

    tmp2 = array([])  # type: array[uint8]
    for (a, b) in zip(tmp, bm):
        tmp2.append(a ^ b)
    tmp2 = F(key, tmp2)
    return tmp2

def key_gen(adr: address, seed: array[uint8]) -> Tuple[array[array[uint8]], array[array[uint8]], address]:
    # TODO: we need separate functions here for xmss later.
    sk = array([])  # type: array[array[uint8]]
    pk = array([])  # type: array[array[uint8]]
    for i in range(0, uint32.int_value(length)):
        sk_i = array.create_random_bytes(n)
        adr = set_chain_address(adr, uint32(i))
        pk_i = wots_chain(sk_i, 0, w.as_int()-1, seed, adr)
        sk.append(sk_i)
        pk.append(pk_i)
    return (sk, pk, adr)

def base_w(msg: array[uint8], l: uint32) -> array[uint8]:
    i = 0 # type: int
    out = 0 # type: int
    total = 0 # type: int
    bits = 0 # type: int
    basew = array([]) # type: array[uint8]
    for consumed in range(0, l.as_int()):
        if bits == 0:
            total = msg[i]
            i = i + 1
            bits = bits + 8
        bits = bits - int(math.log(w.as_int(), 2))
        # This is broken ... total and bits are ints but python things they are uint8
        bw = (total >> bits).as_int() & (w.as_int() - 1)
        basew.append(uint8(bw))
        out = out + 1
    return basew


def wots_sign(msg: array[uint8], sk: array[array[uint8]], adr: address, seed: array[uint8]) -> array[array[uint8]]:
    csum = 0
    m = base_w(msg, length1)
    for i in range(0, length1.as_int()):
        csum = csum + w.as_int() - 1 - m[i].as_int()
    w_lg = math.log(w.as_int(), 2);
    csum = csum << int(8 - ((length2.as_int() * w_lg) % 8))
    length2_bytes = math.ceil((length2.as_int() * w_lg) / 8)
    csum_bytes = array.create(uint8(csum), length2_bytes)
    tmp = base_w(csum_bytes, length2)
    m.extend(tmp)
    sig = array([]) # type: array[array[uint8]]
    for i in range(0, length.as_int()):
        adr = set_chain_address(adr, uint32(i))
        sig_i = wots_chain(sk[i], 0, m[i].as_int(), seed, adr)
        sig.append(sig_i)
    return sig

def wots_verify(pk: array[uint8], msg: array[uint8], sig: array[array[uint8]], adr: address, seed: array[uint8]) -> array[array[uint8]]:
    csum = 0
    m = base_w(msg, length1)
    for i in range(0, length1.as_int()):
        csum = csum + w.as_int() - 1 - m[i].as_int()
    w_lg = math.log(w.as_int(), 2);
    csum = csum << int(8 - ((length2.as_int() * w_lg) % 8))
    length2_bytes = math.ceil((length2.as_int() * w_lg) / 8)
    csum_bytes = array.create(uint8(csum), length2_bytes)
    tmp = base_w(csum_bytes, length2)
    m.extend(tmp)
    pk2 = array([]) # type: array[array[uint8]]
    for i in range(0, length.as_int()):
        adr = set_chain_address(adr, uint32(i))
        pk_i = wots_chain(sig[i], m[i].as_int(), w.as_int() - 1 - m[i].as_int(), seed, adr)
        pk2.append(pk_i)
    # Check pk
    verified = True
    if len(pk) != len(pk2):
        verified = False
    for (k1, k2) in zip(pk, pk2):
        if k1 != k2:
            verified = False
            break
    if verified:
        print("Signature verified")
    else:
        print("Verification error :(")
    return pk2



def main(x: int) -> None:
    adr = array.create_random_bytes(32*8) # type: 'address'
    seed = array.create_random_bytes(n)

    sk, pk, adr = key_gen(adr, seed)
    print("WOTS+ sk")
    for k in sk:
        print(k)
    print("WOTS+ pk")
    for k in pk:
        print(k)

    msg = array([uint8(0xFF), uint8(0xFF), uint8(0xFF), uint8(0xFF), uint8(0xFF)])
    msg_h = array.uint32s_to_uint8s_be(sha2.sha256(msg))
    sig = wots_sign(msg_h, sk, adr, seed)
    print("WOTS+ sig")
    print(sig)
    wots_verify(pk, msg_h, sig, adr, seed)

if __name__ == "__main__":
    main(0)
