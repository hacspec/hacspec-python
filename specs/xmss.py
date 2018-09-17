
from lib.speclib import *
from specs.wots import *
from specs.sha2 import sha256

h : int = 2 # height -> number of signatures
n_keys : int = 2**h

key2_t = bytes_t(2*n)
key3_t = bytes_t(3*n)
wots_keys_t = array_t(sk_t, n_keys)

# Private key:
# 2^h  WOTS+ private keys,
# idx (next WOTS+ sk),
# SK_PRF (n-bytes),
# root (n-bytes),
# public seed (n-bytes)
SK_t = tuple_t(wots_keys_t, nat_t, key_t, key_t, seed_t)

# Public key:
# algorithm oid (uint32_t),
# root node (n-bytes),
# seed (n-bytes)
PK_t = tuple_t(uint32_t, key_t, seed_t)

@typechecked
def get_seed(sk: SK_t) -> seed_t:
    sks : wots_keys_t
    idx : nat_t
    prf_sk : key_t
    root : key_t
    public_seed : seed_t
    sks, idx, prf_sk, root, public_seed = sk
    return public_seed

# H: SHA2-256(toByte(1, 32) || KEY || M),
# H_msg: SHA2-256(toByte(2, 32) || KEY || M),

@typechecked
def H_msg(key: key_t, m: vlbytes_t) -> digest_t:
    return hash(bytes.from_nat_be(nat(2), nat(n)), key, m)


@typechecked
def H(key: key_t, m: key2_t) -> digest_t:
    return hash(bytes.from_nat_be(nat(1), nat(n)), key, m)

@typechecked
def get_wots_sk(k: SK_t, i: nat_t) -> sk_t:
    sks : wots_keys_t
    idx : nat_t
    prf_sk : key_t
    root : key_t
    public_seed : key_t
    sks, idx, prf_sk, root, public_seed = k
    return sks[i]

# Algorithm 7: RAND_HASH
#   Input:  n-byte value LEFT, n-byte value RIGHT, seed SEED,
#           address ADRS
#   Output: n-byte randomized hash
#
#   ADRS.setKeyAndMask(0);
#   KEY = PRF(SEED, ADRS);
#   ADRS.setKeyAndMask(1);
#   BM_0 = PRF(SEED, ADRS);
#   ADRS.setKeyAndMask(2);
#   BM_1 = PRF(SEED, ADRS);
#   return H(KEY, (LEFT XOR BM_0) || (RIGHT XOR BM_1));
@typechecked
def rand_hash(left: key_t, right: key_t, seed: seed_t, adr: address_t) -> digest_t:
    adr : address_t = set_key_and_mask(adr, uint32(0))
    key : digest_t = PRF(seed, adr)
    adr : address_t = set_key_and_mask(adr, uint32(1))
    bm_0 : digest_t = PRF(seed, adr)
    adr : address_t = set_key_and_mask(adr, uint32(2))
    bm_1 : digest_t = PRF(seed, adr)
    left_bm_o : digest_t = array.create(n, uint8(0))
    right_bm_1 : digest_t = array.create(n, uint8(0))
    for i in range(0,n):
        left_bm_o[i] = left[i] ^ bm_0[i]
        right_bm_1[i] = right[i] ^ bm_1[i]
    m = bytes.concat(left_bm_o, right_bm_1)
    r : digest_t = H(key, m)
    return r

# Algorithm 8: ltree
#   Input: WOTS+ public key pk, address ADRS, seed SEED
#   Output: n-byte compressed public key value pk[0]
#
#   unsigned int len' = len;
#   ADRS.setTreeHeight(0);
#   while ( len' > 1 ) {
#     for ( i = 0; i < floor(len' / 2); i++ ) {
#       ADRS.setTreeIndex(i);
#       pk[i] = RAND_HASH(pk[2i], pk[2i + 1], SEED, ADRS);
#     }
#     if ( len' % 2 == 1 ) {
#       pk[floor(len' / 2)] = pk[len' - 1];
#     }
#     len' = ceil(len' / 2);
#     ADRS.setTreeHeight(ADRS.getTreeHeight() + 1);
#   }
#   return pk[0];

@typechecked
def ltree(pk: pk_t, adr: address_t, seed: seed_t) -> key_t:
    l : int = uintn.to_int(length)
    l_half : int = l//2
    adr : address_t = set_tree_height(adr, uint32(0))
    pk_i : vlbytes_t
    for _ in range(0,l):
        for i in range(0,l_half):
            adr = set_tree_index(adr, uint32(i))
            pk[i] = rand_hash(pk[2*i], pk[2*i+1], seed, adr)
        if l % 2 == 1:
            pk[l_half] = pk[l-1]
        l = speclib.ceil(l/2)
        adr = set_tree_height(get_tree_height(adr)+1)
        if l <= 1:
            break
    return pk[0]

# Algorithm 9: treeHash
#   Input: XMSS private key SK, start index s, target node height t,
#          address ADRS
#   Output: n-byte root node - top node on Stack
#
#   if( s % (1 << t) != 0 ) return -1;
#   for ( i = 0; i < 2^t; i++ ) {
#     SEED = getSEED(SK);
#     ADRS.setType(0);   // Type = OTS hash address
#     ADRS.setOTSAddress(s + i);
#     pk = WOTS_genPK (getWOTS_SK(SK, s + i), SEED, ADRS);
#     ADRS.setType(1);   // Type = L-tree address
#     ADRS.setLTreeAddress(s + i);
#     node = ltree(pk, SEED, ADRS);
#     ADRS.setType(2);   // Type = hash tree address
#     ADRS.setTreeHeight(0);
#     ADRS.setTreeIndex(i + s);
#     while ( Top node on Stack has same height t' as node ) {
#        ADRS.setTreeIndex((ADRS.getTreeIndex() - 1) / 2);
#        node = RAND_HASH(Stack.pop(), node, SEED, ADRS);
#        ADRS.setTreeHeight(ADRS.getTreeHeight() + 1);
#     }
#     Stack.push(node);
#   }
#   return Stack.pop();

@typechecked
def tree_hash(sk: SK_t, s: uint32_t, t: uint32_t, adr: address_t) -> key_t:
    x = uint32.to_int(s) % (1 << uintn.to_int(t))
    if x != 0:
        # TODO: handle this in the caller
        return key_t.create(n, uint8(0))
    offset: int = 0
    stack: array_t = array.create(2**uint32.to_int(t), array.create(n, uint8(0)))
    for i in range(0, 2**uint32.to_int(t)):
        seed: seed_t = get_seed(sk) # FIXME
        adr: address_t = set_type(adr, uint32(0))
        a: uint32_t = s + uint32(i)
        adr = set_ots_address(adr, a)
        pk: pk_t
        pk, _ = key_gen_pk(adr, seed, get_wots_sk(sk, uint32.to_int(a)))
        adr = set_type(adr, uint32(1))
        adr = set_ltree_address(adr, a)
        node: key_t = ltree(pk, seed, adr)
        adr = set_type(adr, uint32(2))
        adr = set_tree_height(adr, uint32(0))
        adr = set_tree_index(adr, a)
        if offset > 1:
            for _ in range(0,t): # The stack has at most t-1 elements.
                adr = set_tree_index(adr, uint32(get_tree_index(adr) - 1 // 2))
                node = rand_hash(stack[offset-1], node, seed, adr)
                adr = set_tree_height(adr, get_tree_height(adr) + 1)
        stack[offset] = node
        offset += 1

# Algorithm 10: XMSS_keyGen - Generate an XMSS key pair
#   Input: No input
#   Output: XMSS private key SK, XMSS public key PK
#
#   // Example initialization for SK-specific contents
#   idx = 0;
#   for ( i = 0; i < 2^h; i++ ) {
#     wots_sk[i] = WOTS_genSK();
#   }
#   initialize SK_PRF with a uniformly random n-byte string;
#   setSK_PRF(SK, SK_PRF);
#
#   // Initialization for common contents
#   initialize SEED with a uniformly random n-byte string;
#   setSEED(SK, SEED);
#   setWOTS_SK(SK, wots_sk));
#   ADRS = toByte(0, 32);
#   root = treeHash(SK, 0, h, ADRS);
#
#   SK = idx || wots_sk || SK_PRF || root || SEED;
#   PK = OID || root || SEED;
#   return (SK || PK);

@typechecked
def key_gen_xmss() -> tuple_t(SK_t, PK_t):
    zero_key: sk_t = sk_t.create(uintn.to_int(length), key_t.create(n, uint8(0)))
    wots_keys: wots_keys_t = wots_keys_t.create(n_keys, zero_key)
    for i in range(0, n_keys):
        wots_sk : sk_t = key_gen_sk()
        wots_keys[i] = wots_sk
    idx: nat_t = 0
    SK_PRF: key_t = bytes.create_random_bytes(n)
    seed: seed_t = bytes.create_random_bytes(n)
    adr: address_t = array.create(8, uint32(0))
    dummy_root: key_t = array.create(n, uint8(0))
    xmss_sk_tmp: SK_t = (wots_keys, idx, SK_PRF, dummy_root, seed)
    root : key_t = tree_hash(xmss_sk_tmp, uint32(0), uint32(h), adr)
    xmss_sk: SK_t = (wots_keys, idx, SK_PRF, root, seed)
    xmss_pk: PK_t = (uint32(0), root, seed)
    return xmss_sk, xmss_pk
