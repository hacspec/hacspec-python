#!/usr/bin/python3

from hacspec.speclib import *
from aes import aes128_block, aes128_encrypt, aes128_decrypt, xor_block
from gf128 import gmac

key_t    = bytes_t(16)
nonce_t  = bytes_t(12)
tag_t    = bytes_t(16)

@typechecked
def padded_aad_msg(aad:vlbytes_t,msg:vlbytes_t) -> Tuple[int,vlbytes_t]:
    laad = len(aad)
    lmsg = len(msg)
    pad_aad = laad
    if laad % 16 > 0:
        pad_aad = laad + (16 - (laad % 16))
    pad_msg = lmsg
    if lmsg % 16 > 0:
        pad_msg = lmsg + (16 - (lmsg % 16))
    to_mac = bytes(array.create(pad_aad + pad_msg + 16,uint8(0)))
    to_mac[0:laad] = aad
    to_mac[pad_aad:pad_aad+lmsg] = msg
    to_mac[pad_aad+pad_msg:pad_aad+pad_msg+8] = bytes.from_uint64_be(uint64(laad * 8))
    to_mac[pad_aad+pad_msg+8:pad_aad+pad_msg+16] = bytes.from_uint64_be(uint64(lmsg * 8))
    return pad_aad+pad_msg+16, to_mac

@typechecked
def aead_aes128gcm_encrypt(key:key_t,nonce:nonce_t,aad:vlbytes_t,msg:vlbytes_t) -> Tuple[vlbytes_t,tag_t]:
    nonce0 = bytes(array.create(12,uint8(0)))
    mac_key = aes128_block(key,nonce0,uint32(0))
    tag_mix = aes128_block(key,nonce,uint32(1))
    ciphertext = aes128_encrypt(key,nonce,uint32(2),msg)
    len, to_mac = padded_aad_msg(aad,ciphertext)
    mac = gmac(to_mac,mac_key)
    mac = xor_block(mac,tag_mix)
    return ciphertext, mac

@typechecked
def aead_aes128gcm_decrypt(key:key_t,nonce:nonce_t,aad:vlbytes_t,
                           ciphertext:vlbytes_t,tag:tag_t) -> vlbytes_t:
    nonce0 = bytes(array.create(12,uint8(0)))
    mac_key = aes128_block(key,nonce0,uint32(0))
    tag_mix = aes128_block(key,nonce,uint32(1))
    _, to_mac = padded_aad_msg(aad,ciphertext)
    mac = gmac(to_mac,mac_key)
    mac = xor_block(mac,tag_mix)
    if mac == tag:
        msg = aes128_decrypt(key,nonce,uint32(2),ciphertext)
        return msg
    else:
        fail("mac failed")
        
