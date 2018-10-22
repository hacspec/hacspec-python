#!/usr/bin/python3

from lib.speclib import *
from specs.sha2 import sha256

max_size_t : int = 2 ** 32 - 1
size_nat_t = refine_t(nat_t, lambda x: x <= max_size_t)
max_input_len_sha256 : nat_t = nat(2 ** 61)
hLen : nat_t = nat(32)


@typechecked
def blocks(x: size_nat_t, m: size_nat_t) -> size_nat_t:
    return nat((x - 1) // m + 1)


@typechecked
def xor_bytes(b1: vlbytes_t, b2: vlbytes_t) -> vlbytes_t:
    res : vlbytes_t = bytes.copy(b1)
    for i in range(array.length(b1)):
        res[i] ^= b2[i]
    return res


@typechecked
def eq_bytes(b1: vlbytes_t, b2: vlbytes_t) -> bool:
    return (b1 == b2)


@typechecked
def hash_sha256(msg: vlbytes_t) -> bytes_t(32):
    return sha256(msg)

# Mask Generation Function


@typechecked
def mgf_sha256(mgfseed: vlbytes_t, maskLen: size_nat_t) -> vlbytes_t:
    counter_max : size_nat_t = blocks(maskLen, hLen)
    accLen : size_nat_t = counter_max * hLen
    acc = array.create(accLen, uint8(0))
    mgfseedLen : int = array.length(mgfseed)
    mgfseed_counter = array.create(mgfseedLen + 4, uint8(0))
    mgfseed_counter[0:mgfseedLen] = mgfseed

    for i in range(counter_max):
        c : bytes_t = bytes.from_uint32_be(uint32(i))
        mgfseed_counter[mgfseedLen:(mgfseedLen + 4)] = c
        mHash : bytes_t = hash_sha256(mgfseed_counter)
        acc[(hLen * i):(hLen * i + hLen)] = mHash

    return acc[0:maskLen]

# Convert functions


@typechecked
def os2ip(b: vlbytes_t) -> nat_t:
    return bytes.to_nat_be(b)


@typechecked
def i2osp(n: nat_t) -> vlbytes_t:
    return bytes.from_nat_be(nat(n))

# RSA-PSS


rsa_pubkey_t = tuple_t(nat_t, nat_t)  # (n, e)
rsa_privkey_t = tuple_t(rsa_pubkey_t, nat_t)  # ((n, e), d)


@contract3(lambda salt, msg, emBits: array.length(msg) < max_input_len_sha256 and
           hLen + array.length(salt) + nat(2) <= blocks(emBits, nat(8)) and
           array.length(salt) + hLen + nat(8) < max_size_t and emBits > 0,
           lambda salt, msg, emBits, res: array.length(res) == blocks(emBits, nat(8)))
@typechecked
def pss_encode(salt: vlbytes_t, msg: vlbytes_t, emBits: size_nat_t) -> vlbytes_t:
    sLen : int = array.length(salt)
    emLen : size_nat_t = blocks(emBits, size_nat(nat(8)))
    msBits : size_nat_t = emBits % 8

    mHash : bytes_t = hash_sha256(msg)
    m1Len : size_nat_t = 8 + hLen + sLen
    # m1 = [8 * 0x00; mHash; salt]
    m1 = array.create(m1Len, uint8(0))
    m1[8:(8 + hLen)] = mHash
    m1[(8 + hLen):m1Len] = salt
    m1Hash : size_nat_t = hash_sha256(m1)

    dbLen : size_nat_t = size_nat(nat(emLen - hLen - 1))
    # db = [0x00; ..; 0x00; 0x01; salt]
    db = array.create(dbLen, uint8(0))
    last_before_salt : size_nat_t = dbLen - sLen - 1
    db[last_before_salt] = uint8(0x01)
    db[(last_before_salt + 1):dbLen] = salt

    dbMask : vlbytes_t = mgf_sha256(m1Hash, dbLen)
    maskedDB : vlbytes_t = xor_bytes(db, dbMask)
    if msBits > 0:
        maskedDB[0] = maskedDB[0] & (uint8(0xff) >> (8 - msBits))

    em = array.create(emLen, uint8(0))
    # em = [maskedDB; m1Hash; 0xbc]
    em[0:dbLen] = maskedDB
    em[dbLen:(dbLen + hLen)] = m1Hash
    em[emLen - 1] = uint8(0xbc)
    return em


@contract3(lambda sLen, msg, em, emBits: array.length(msg) < max_input_len_sha256 and
           array.length(em) == blocks(emBits, nat(8)) and emBits > 0 and
           sLen + hLen + 8 < max_size_t,
           lambda sLen, msg, em, emBits, res: True)
@typechecked
def pss_verify(sLen: size_nat_t, msg: vlbytes_t, em: vlbytes_t, emBits: size_nat_t) -> bool:
    emLen : size_nat_t = blocks(emBits, nat(8))
    msBits : size_nat_t = emBits % 8
    mHash : size_nat_t = hash_sha256(msg)

    em_0 : uint8_t
    if msBits > 0:
        em_0 = em[0] & (uint8(0xff) << msBits)
    else:
        em_0 = uint8(0)

    res : bool
    if emLen < sLen + hLen + nat(2):
        res = False
    else:
        if not (em[emLen - 1] == uint8(0xbc) and em_0 == uint8(0)):
            res = False
        else:
            dbLen : size_nat_t = size_nat(nat(emLen - hLen - 1))
            maskedDB : uint8_t = em[0:dbLen]
            m1Hash :vlbytes_t = em[dbLen:(dbLen + hLen)]

            dbMask : vlbytes_t = mgf_sha256(m1Hash, dbLen)
            db : vlbytes_t = xor_bytes(maskedDB, dbMask)
            if msBits > 0:
                db[0] = db[0] & (uint8(0xff) >> (8 - msBits))

            padLen : size_nat_t = emLen - sLen - hLen - 1
            pad2 = array.create(padLen, uint8(0))
            pad2[padLen - 1] = uint8(0x01)

            pad : vlbytes_t = db[0:padLen]
            salt : vlbytes_t = db[padLen:(padLen + sLen)]

            if (eq_bytes(pad, pad2)):
                m1Len : size_nat_t = 8 + hLen + sLen
                m1 = array.create(m1Len, uint8(0))
                m1[8:(8 + hLen)] = mHash
                m1[(8 + hLen):m1Len] = salt
                m1Hash0 : vlbytes_t = hash_sha256(m1)
                res = eq_bytes(m1Hash, m1Hash0)
            else:
                res = False
    return res


@contract3(lambda modBits, skey, salt, msg:
                array.length(msg) < max_input_len_sha256 and modBits > nat(1) and
                array.length(salt) + hLen + nat(8) < max_size_t and array.length(salt) +
                hLen + nat(2) <= blocks(nat(modBits - nat(1)), nat(8)),
           lambda modBits, skey, salt, msg, res: array.length(res) == blocks(modBits, nat(8)))
@typechecked
def rsapss_sign(modBits: size_nat_t, skey: rsa_privkey_t, salt: vlbytes_t, msg: vlbytes_t) -> vlbytes_t:
    pkey : rsa_pubkey_t
    d : nat_t
    n : nat_t
    e : nat_t
    (pkey, d) = skey
    (n, e) = pkey
    felem_t = natmod_t(n)
    em : vlbytes_t = pss_encode(salt, msg, nat(modBits - 1))
    m : nat_t = os2ip(em)
    mmod: felem_t = natmod(m,n)
    smod: felem_t = mmod ** d
    s : nat_t = natmod.to_int(smod)
    sgnt : vlbytes_t = i2osp(s)
    return sgnt


@contract3(lambda modBits, pkey, sLen, msg, sgnt:
                array.length(msg) < max_input_len_sha256 and
                modBits > 1 and array.length(sgnt) == blocks(modBits, nat(8)) and
                sLen + hLen + nat(8) < max_size_t,
           lambda modBits, pkey, sLen, msg, sgnt, res: True)
@typechecked
def rsapss_verify(modBits: size_nat_t, pkey: rsa_pubkey_t, sLen: size_nat_t, msg: vlbytes_t, sgnt: vlbytes_t) -> bool:
    n : nat_t
    e : nat_t
    (n, e) = pkey
    felem_t = natmod_t(n)
    s : nat_t = os2ip(sgnt)
    smod: felem_t = natmod(s,n)
    mmod: felem_t
    m: nat_t
    em: vlbytes_t
    res : bool
    if s < n:
        mmod = smod ** e
        m = natmod.to_int(mmod)
        em = i2osp(m)
        res = pss_verify(sLen, msg, em, size_nat(nat(modBits - 1)))
    else:
        res = False
    return res
