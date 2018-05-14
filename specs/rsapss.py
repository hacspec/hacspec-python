#!/usr/bin/python3

from hacspec.speclib import *
from sha2 import sha256

max_size_t = 2 ** 32 - 1
size_nat_t = refine3(nat, lambda x: x <= max_size_t)

@typechecked
def blocks(x:size_nat_t, m:size_nat_t) \
    -> contract(size_nat_t,
                lambda x, m: x > 0 and m > 0,
                lambda x, m, res: res > 0 and x <= m * r):
    return size_nat_t(nat((x - 1) // m + 1))

@typechecked
def xor_bytes(b1:vlbytes_t, b2:vlbytes_t) -> vlbytes_t:
    res = vlbytes.copy(b1)
    for i in range(array.length(b1)):
        res[i] ^= b2[i]
    return res

@typechecked
def eq_bytes(b1:vlbytes_t, b2:vlbytes_t) -> bool:
    return (b1 == b2)

# Hash function

max_input_len_sha256 = 2 ** 61
hLen = nat(32)

@typechecked
def hash_sha256(msg:vlbytes_t) \
    -> contract(bytes_t(hLen),
                lambda msg: array.length(msg) < max_input_len_sha256,
                lambda msg, res: True):
    return sha256(msg)

# Mask Generation Function

@typechecked
def mgf_sha256(mgfseed:vlbytes_t, maskLen:size_nat_t) \
    -> contract(vlbytes_t,
                lambda mgfseed, maskLen: maskLen < (2 ** 32) * hLen and maskLen > 0
                and array.length(mgfseed) + 4 < max_size_t,
                lambda mgfseed, maskLen, res: array.length(res) == maskLen):
    counter_max = blocks(maskLen, hLen)
    accLen = counter_max * hLen
    acc = array.create(accLen, uint8(0))
    mgfseedLen = array.length(mgfseed)
    mgfseed_counter = array.create(mgfseedLen + 4, uint8(0))
    mgfseed_counter[0:mgfseedLen] = mgfseed

    for i in range(counter_max):
        c = vlbytes.from_uint32_be(uint32(i))
        mgfseed_counter[mgfseedLen:(mgfseedLen + 4)] = c
        mHash = hash_sha256(mgfseed_counter)
        acc[(hLen * i):(hLen * i + hLen)] = mHash

    return acc[0:maskLen]

# Convert functions

@typechecked
def os2ip(b:vlbytes_t) -> nat:
    return bytes.to_nat_be(b)

@typechecked
def i2osp(n:nat) -> vlbytes_t:
    return bytes.from_nat_be(nat(n))

# RSA-PSS

rsa_pubkey = tuple2(nat, nat) #(n, e)
rsa_privkey = tuple2(rsa_pubkey, nat) #((n, e), d)

# EMSA-PSS encoding

@typechecked
def pss_encode(salt:vlbytes_t, msg:vlbytes_t, emBits:size_nat_t) \
    -> contract(vlbytes_t,
                lambda salt, msg, emBits: array.length(msg) < max_input_len_sha256 and
                hLen + array.length(salt) + 2 <= blocks(emBits, nat(8)) and
                array.length(salt) + hLen + 8 < max_size_t and emBits > 0,
                lambda salt, msg, emBits, res: array.length(res) == blocks(emBits, nat(8))):
    sLen = array.length(salt)
    emLen = blocks(emBits, size_nat_t(nat(8)))
    msBits = emBits % 8

    mHash = hash_sha256(msg)
    m1Len = 8 + hLen + sLen
    #m1 = [8 * 0x00; mHash; salt]
    m1 = array.create(m1Len, uint8(0))
    m1[8:(8 + hLen)] = mHash
    m1[(8 + hLen):m1Len] = salt
    m1Hash = hash_sha256(m1)

    dbLen = size_nat_t(nat(emLen - hLen - 1))
    #db = [0x00; ..; 0x00; 0x01; salt]
    db = array.create(dbLen, uint8(0))
    last_before_salt = dbLen - sLen - 1
    db[last_before_salt] = uint8(0x01)
    db[(last_before_salt + 1):dbLen] = salt

    dbMask = mgf_sha256(m1Hash, dbLen)
    maskedDB = xor_bytes(db, dbMask)
    if msBits > 0:
        maskedDB[0] = maskedDB[0] & (uint8(0xff) >> (8 - msBits))

    em = array.create(emLen, uint8(0))
    #em = [maskedDB; m1Hash; 0xbc]
    em[0:dbLen] = maskedDB
    em[dbLen:(dbLen + hLen)] = m1Hash
    em[emLen - 1] = uint8(0xbc)
    return em

# EMSA-PSS verification

@typechecked
def pss_verify(sLen:size_nat_t, msg:vlbytes_t, em:vlbytes_t, emBits:size_nat_t) \
    -> contract(bool,
                lambda sLen, msg, em, emBits: array.length(msg) < max_input_len_sha256 and
                array.length(em) == blocks(emBits, nat(8)) and emBits > 0 and
                array.length(salt) + hLen + 8 < max_size_t,
                lambda sLen, msg, em, emBits, res: True):
    emLen = blocks(emBits, nat(8))
    msBits = emBits % 8
    mHash = hash_sha256(msg)

    if msBits > 0:
        em_0 = em[0] & (uint8(0xff) << msBits)
    else:
        em_0 = uint8(0)

    if emLen < sLen + hLen + 2:
        res = False
    else:
        if not (em[emLen - 1] == uint8(0xbc) and em_0 == uint8(0)):
            res = False
        else:
            dbLen = size_nat_t(nat(emLen - hLen - 1))
            maskedDB = em[0:dbLen]
            m1Hash = em[dbLen:(dbLen + hLen)]

            dbMask = mgf_sha256(m1Hash, dbLen)
            db = xor_bytes(maskedDB, dbMask)
            if msBits > 0:
                db[0] = db[0] & (uint8(0xff) >> (8 - msBits))

            padLen = emLen - sLen - hLen - 1
            pad2 = array.create(padLen, uint8(0))
            pad2[padLen - 1] = uint8(0x01)

            pad = db[0:padLen]
            salt = db[padLen:(padLen + sLen)]

            if (eq_bytes(pad, pad2)):
                m1Len = 8 + hLen + sLen
                m1 = array.create(m1Len, uint8(0))
                m1[8:(8 + hLen)] = mHash
                m1[(8 + hLen):m1Len] = salt
                m1Hash0 = hash_sha256(m1)
                res = eq_bytes(m1Hash, m1Hash0)
            else:
                res = False
    return res

@typechecked
def rsapss_sign(modBits:size_nat_t, skey:rsa_privkey, salt:vlbytes_t, msg:vlbytes_t) \
    -> contract(vlbytes_t,
                lambda modBits, skey, salt, msg: array.length(msg) < max_input_len_sha256 and modBits > 1 and
                array.length(salt) + hLen + 8 < max_size_t and array.length(salt) + hLen + 2 <= blocks(modBits - 1, nat(8)),
                lambda modBits, skey, salt, msg, res: array.length(res) == blocks(modBits, nat(8))):
    (pkey, d) = skey
    (n, e) = pkey
    em = pss_encode(salt, msg, nat(modBits - 1))
    m = os2ip(em)
    s = pow(m, d, n)
    sgnt = i2osp(s)
    return sgnt

@typechecked
def rsapss_verify(modBits:size_nat_t, pkey:rsa_pubkey, sLen:size_nat_t, msg:vlbytes_t, sgnt: vlbytes_t) \
    -> contract(bool,
                lambda modBits, pkey, sLen, msg, sgnt: array.length(msg) < max_input_len_sha256 and
                modBits > 1 and array.length(sgnt) == blocks(modBits, 8) and sLen + hLen + 8 < max_size_t,
                lambda modBits, pkey, sLen, msg, sgnt, res: True):
    (n, e) = pkey
    s = os2ip(sgnt)
    if s < n:
        m = pow(s, e, n)
        em = i2osp(m)
        res = pss_verify(sLen, msg, em, size_nat_t(nat(modBits - 1)))
    else:
        res = False
    return res
