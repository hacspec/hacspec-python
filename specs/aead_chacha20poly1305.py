#!/usr/bin/python3

from speclib import *
from typing import Tuple
from chacha20 import chacha20_block, chacha20_encrypt, chacha20_decrypt
from poly1305 import poly1305_mac

def padded_aad_msg(aad:bytes,msg:bytes) -> Tuple[int,bytes]:
    laad = len(aad)
    lmsg = len(msg)
    pad_aad = laad if laad % 16 == 0 else 16 * (laad // 16 + 1)
    pad_msg = lmsg if lmsg % 16 == 0 else 16 * (lmsg // 16 + 1)
    to_mac = array.create(0,pad_aad + pad_msg + 16);
    to_mac[0:laad] = aad
    to_mac[pad_aad:pad_aad+lmsg] = msg
    to_mac[pad_aad+pad_msg:pad_aad+pad_msg+8] = uint64.to_bytes_le(uint64(laad))
    to_mac[pad_aad+pad_msg+8:pad_aad+pad_msg+16] = uint64.to_bytes_le(uint64(lmsg))
    return pad_aad+pad_msg+16, bytes(to_mac)

def aead_chacha20poly1305_encrypt(key:bytes,nonce:bytes,aad:bytes,msg:bytes) -> Tuple[bytes,bytes]:
    keyblock0 = chacha20_block(key,0,nonce)
    mac_key = keyblock0[0:32]
    ciphertext = chacha20_encrypt(key,1,nonce,msg)
    len, to_mac = padded_aad_msg(aad,ciphertext)
    mac = poly1305_mac(to_mac,mac_key)
    return ciphertext, mac

def aead_chacha20poly1305_decrypt(key:bytes,nonce:bytes,
                                  aad:bytes,
                                  ciphertext:bytes,
                                  tag:bytes) -> bytes:
    keyblock0 = chacha20_block(key,0,nonce)
    mac_key = keyblock0[0:32]
    len, to_mac = padded_aad_msg(aad,ciphertext)
    mac = poly1305_mac(to_mac,mac_key)
    if mac == tag:
        msg = chacha20_decrypt(key,1,nonce,ciphertext)
        return msg
    else:
        raise Error("mac failed")
