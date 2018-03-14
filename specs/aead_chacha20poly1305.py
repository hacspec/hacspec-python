#!/usr/bin/python3

from speclib import *
from typing import Tuple
from chacha20 import chacha20_block, chacha20_encrypt, chacha20_decrypt
from poly1305 import poly1305_mac

bytes_t = array[uint8] #length: arbitrary

def padded_aad_msg(aad:bytes_t,msg:bytes_t) -> Tuple[int,bytes_t]:
    laad = len(aad)
    lmsg = len(msg)
    pad_aad = 0
    if laad % 16 == 0:
        pad_aad = laad
    else:
        pad_aad = 16 * (laad // 16 + 1)
    if lmsg % 16 == 0:
        pad_msg = lmsg
    else:
        pad_msg = 16 * (lmsg // 16 + 1)
    to_mac = array.create(uint8(0),pad_aad + pad_msg + 16);
    to_mac = to_mac.set((0, laad), aad)
    to_mac = to_mac.set((pad_aad, pad_aad+lmsg), msg)
    to_mac = to_mac.set((pad_aad+pad_msg, pad_aad+pad_msg+8), bytes.from_uint64_le(uint64(laad)))
    to_mac = to_mac.set((pad_aad+pad_msg+8, pad_aad+pad_msg+16), bytes.from_uint64_le(uint64(lmsg)))
    return pad_aad+pad_msg+16, to_mac

def aead_chacha20poly1305_encrypt(key:bytes_t,nonce:bytes_t,aad:bytes_t,msg:bytes_t) -> Tuple[bytes_t,bytes_t]:
    keyblock0 = chacha20_block(key,0,nonce)
    mac_key = keyblock0[0:32]
    ciphertext = chacha20_encrypt(key,1,nonce,msg)
    len, to_mac = padded_aad_msg(aad,ciphertext)
    mac = poly1305_mac(to_mac,mac_key)
    return ciphertext, mac

def aead_chacha20poly1305_decrypt(key:bytes_t,nonce:bytes_t,
                                  aad:bytes_t,
                                  ciphertext:bytes_t,
                                  tag:bytes_t) -> bytes_t:
    keyblock0 = chacha20_block(key,0,nonce)
    mac_key = keyblock0[0:32]
    len, to_mac = padded_aad_msg(aad,ciphertext)
    mac = poly1305_mac(to_mac,mac_key)
    if mac == tag:
        msg = chacha20_decrypt(key,1,nonce,ciphertext)
        return msg
    else:
        raise Error("mac failed")
