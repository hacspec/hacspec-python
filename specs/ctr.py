from typing import Callable, List, Iterator, Tuple
from functools import reduce
from speclib import *

block_t = array[uint8]     #length <= blocksize
key_t = array[uint8]       #length = keysize
nonce_t = array[uint8]     #length = noncesize
bytes_t = array[uint8]     #length arbitrary

def block_encrypt(block_cipher:Callable[[key_t,int,nonce_t],block_t],
                  key:key_t,counter:int,nonce:nonce_t,msg:block_t) -> block_t:
    keyblock = block_cipher(key,counter,nonce)
    cipherblock = array([x ^ y for (x,y) in array.zip(keyblock,msg)])
    return (cipherblock)

# First version: using list comprehensions to map encryption
def counter_mode(blocksize:int,block_cipher:Callable[[key_t,int,nonce_t],block_t],
                 key:key_t,counter:int,nonce:nonce_t,msg:bytes_t) -> bytes_t :
    msg_blocks = array.split_blocks(msg,blocksize)
    cipherblocks = array ([block_encrypt(block_cipher,key,counter+i,nonce,b) for (i,b) in array.enumerate(msg_blocks)])
    return array.concat_blocks(cipherblocks)

# Second version: using map
def counter_mode_map(blocksize:int,block_cipher:Callable[[key_t,int,nonce_t],block_t],
                     key:key_t,counter:int,nonce:nonce_t,msg:bytes_t) -> bytes_t :
    msg_blocks = array.split_blocks(msg,blocksize)
    def enc(x:Tuple[int,block_t]) -> block_t:
        return block_encrypt(block_cipher,key,counter+x[0],nonce,x[1])
    cipherblocks = array.map(enc, array.enumerate(msg_blocks))
    return array.concat_blocks(cipherblocks)

# Third version: using a local loop
def counter_mode_iter(blocksize:int,block_cipher:Callable[[key_t,int,nonce_t],block_t],
                      key:key_t,counter:int,nonce:nonce_t,msg:bytes_t) -> bytes_t :
    ciphertext = array.create(uint8(0),len(msg))
    nblocks = len(msg) // blocksize;
    last = len(msg) % blocksize
    for i in range(nblocks):
        keyblock = block_cipher(key,counter+i,nonce)
        start = i * blocksize
        for j in range(blocksize):
            ciphertext[start+j] ^= keyblock[j]
    if last > 0:
        keyblock = block_cipher(key,counter+nblocks,nonce)
        start = len(msg) - last
        for j in range(last):
            ciphertext[start+j] ^= keyblock[j]
    return (ciphertext)

