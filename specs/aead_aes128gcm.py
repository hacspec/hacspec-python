#!/usr/bin/python3

from lib.speclib import *
from specs.aes import aes128_ctr_keyblock, aes128_encrypt, aes128_decrypt, xor_block
from specs.gf128 import gmac

key_t    = bytes_t(16)
nonce_t  = bytes_t(12)
tag_t    = bytes_t(16)

@typechecked
def padded_aad_msg(aad:vlbytes_t,msg:vlbytes_t) -> tuple_t(int,vlbytes_t):
    laad : int = len(aad)
    lmsg : int = len(msg)
    pad_aad : int = laad
    if laad % 16 > 0:
        pad_aad = laad + (16 - (laad % 16))
    pad_msg : int = lmsg
    if lmsg % 16 > 0:
        pad_msg = lmsg + (16 - (lmsg % 16))
    to_mac = bytes(array.create(pad_aad + pad_msg + 16,uint8(0)))
    to_mac[0:laad] = aad
    to_mac[pad_aad:pad_aad+lmsg] = msg
    to_mac[pad_aad+pad_msg:pad_aad+pad_msg+8] = bytes.from_uint64_be(uint64(laad * 8))
    to_mac[pad_aad+pad_msg+8:pad_aad+pad_msg+16] = bytes.from_uint64_be(uint64(lmsg * 8))
    return pad_aad+pad_msg+16, to_mac

@typechecked
def aead_aes128gcm_encrypt(key:key_t,nonce:nonce_t,aad:vlbytes_t,msg:vlbytes_t) -> tuple_t(vlbytes_t,tag_t):
    nonce0 = bytes(array.create(12,uint8(0)))
    mac_key : block_t = aes128_ctr_keyblock(key,nonce0,uint32(0))
    tag_mix : block_t = aes128_ctr_keyblock(key,nonce,uint32(1))
    ciphertext : vlbytes_t = aes128_encrypt(key,nonce,uint32(2),msg)
    to_mac : vlbytes_t
    _, to_mac = padded_aad_msg(aad,ciphertext)
    mac : tag_t = gmac(to_mac,mac_key)
    mac = xor_block(mac,tag_mix)
    return ciphertext, mac

@typechecked
def aead_aes128gcm_decrypt(key:key_t,nonce:nonce_t,aad:vlbytes_t,
                           ciphertext:vlbytes_t,tag:tag_t) -> vlbytes_t:
    nonce0 = bytes(array.create(12,uint8(0)))
    mac_key : block_t = aes128_ctr_keyblock(key,nonce0,uint32(0))
    tag_mix : block_t = aes128_ctr_keyblock(key,nonce,uint32(1))
    to_mac : vlbytes_t
    _, to_mac = padded_aad_msg(aad,ciphertext)
    mac : tag_t = gmac(to_mac,mac_key)
    mac = xor_block(mac,tag_mix)
    if mac == tag:
        msg : vlbytes_t = aes128_decrypt(key,nonce,uint32(2),ciphertext)
        return msg
    else:
        fail("mac failed")
        
