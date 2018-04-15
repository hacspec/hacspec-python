#!/usr/bin/python3

from speclib import *
from chacha20 import chacha20_block, chacha20_encrypt, chacha20_decrypt
from poly1305 import poly1305_mac

key_t    = bytes_t('key_t', 32)
nonce_t  = bytes_t('nonce_t', 12)
tag_t    = bytes_t('tag_t', 16)

@typechecked
def padded_aad_msg(aad:vlbytes_t,msg:vlbytes_t) -> Tuple[int,vlbytes_t]:
    laad = len(aad)
    lmsg = len(msg)
    pad_aad = 16 * (laad // 16 + 1)
    if laad % 16 == 0:
        pad_aad = laad
    pad_msg = 16 * (lmsg // 16 + 1)
    if lmsg % 16 == 0:
        pad_msg = lmsg
    to_mac = bytes(array.create(pad_aad + pad_msg + 16,uint8(0)));
    to_mac[0:laad] = aad
    to_mac[pad_aad:pad_aad+lmsg] = msg
    to_mac[pad_aad+pad_msg:pad_aad+pad_msg+8] = bytes.from_uint64_le(uint64(laad))
    to_mac[pad_aad+pad_msg+8:pad_aad+pad_msg+16] = bytes.from_uint64_le(uint64(lmsg))
    return pad_aad+pad_msg+16, to_mac

@typechecked
def aead_chacha20poly1305_encrypt(key:key_t,nonce:nonce_t,aad:vlbytes_t,msg:vlbytes_t) -> Tuple[vlbytes_t,tag_t]:
    keyblock0 = chacha20_block(key,uint32(0),nonce)
    mac_key = keyblock0[0:32]
    ciphertext = chacha20_encrypt(key,uint32(1),nonce,msg)
    len, to_mac = padded_aad_msg(aad,ciphertext)
    mac = poly1305_mac(to_mac,mac_key)
    return ciphertext, mac

@typechecked
def aead_chacha20poly1305_decrypt(key:key_t,nonce:bytes_t,
                                  aad:vlbytes_t,
                                  ciphertext:vlbytes_t,
                                  tag:tag_t) -> bytes_t:
    keyblock0 = chacha20_block(key, uint32(0), nonce)
    mac_key = keyblock0[0:32]
    _, to_mac = padded_aad_msg(aad,ciphertext)
    mac = poly1305_mac(to_mac,mac_key)
    if mac == tag:
        msg = chacha20_decrypt(key, uint32(1), nonce, ciphertext)
        return msg
    else:
        fail("mac failed")
