
from lib.speclib import *
from specs.wots import *
from specs.sha2 import sha256

h : int = 4 # height -> number of signatures
n_keys : int = 2**h

key2_t = bytes_t(2*n)
key3_t = bytes_t(3*n)
wots_keys_t = array_t(sk_t, n_keys)

# Private Key:
# 2^h  WOTS+ private keys,
# idx (next WOTS+ sk),
# SK_PRF (n-bytes),
# root (n-bytes)
# public seed (n-bytes)
SK_t = tuple_t(wots_keys_t, nat_t, key_t, key_t, key_t)


# H: SHA2-256(toByte(1, 32) || KEY || M),
# H_msg: SHA2-256(toByte(2, 32) || KEY || M),

@typechecked
def H_msg(key: key_t, m: vlbytes_t) -> digest_t:
    return hash(bytes.from_nat_be(nat(2), nat(n)), key, m)


@typechecked
def H(key: key_t, m: key2_t) -> digest_t:
    return hash(bytes.from_nat_be(nat(1), nat(n)), key, m)

@typechecked
def key_gen_xmss() -> SK_t:
    zero_key : sk_t = sk_t.create(uintn.to_int(length), key_t.create(n, uint8(0)))
    wots_keys : wots_keys_t = wots_keys_t.create(n_keys, zero_key)
    for i in range(0, n_keys):
        wots_sk : sk_t = key_gen_sk()
        wots_keys[i] = wots_sk
    idx : nat_t = 0
    SK_PRF : key_t = bytes.create_random_bytes(n)
    root : key_t
    seed : key_t = bytes.create_random_bytes(n)

@typechecked
def get_sk(k: SK_t, i: nat_t) -> sk_t:
    sks : wots_keys_t
    idx : nat_t
    prf_sk : key_t
    root : key_t
    public_seed : key_t
    sks, idx, prf_sk, root, public_seed = k
    return sks[i]

@typechecked
def rand_hash(left: key_t, right: key_t, seed: seed_t, adr: address_t) -> digest_t:
    adr : address_t = set_key_and_mask(adr, uint32(0))
    key : digest_t = PRF(seed, adr)
    adr : address_t = set_key_and_mask(adr, uint32(1))
    bm_0 : digest_t = PRF(seed, adr)
    adr : address_t = set_key_and_mask(adr, uint32(2))
    bm_1 : digest_t = PRF(seed, adr)
    left_bm_o : digest_t = array.create(n)
    right_bm_1 : digest_t = array.create(n)
    for i in range(0,n):
        left_bm_o[i] = left[i] ^ bm_0[i]
        right_bm_1[i] = right[i] ^ bm_1[i]
    m = bytes.concat(left_bm_o, right_bm_1)
    r : digest_t = H(key, m)
    return r
