from typing import Callable, List, Iterator, Tuple
from functools import reduce
from speclib import *

def block_encrypt(block_cipher:Callable[[bytes,int,bytes],bytes],
                  key:bytes,counter:int,nonce:bytes,msg:bytes) -> bytes:
    keyblock = block_cipher(key,counter,nonce)
    cipherblock = [x ^ y for (x,y) in zip(keyblock,msg)]
    return bytes(cipherblock)

# First version: using list comprehensions to map encryption
def counter_mode(blocksize:int,block_cipher:Callable[[bytes,int,bytes],bytes],
                 key:bytes,counter:int,nonce:bytes,msg:bytes) -> bytes :
    msg_blocks = split_blocks(msg,blocksize)
    cipherblocks = array ([block_encrypt(block_cipher,key,counter+i,nonce,b) for (i,b) in enumerate(msg_blocks)])
    return concat_blocks(cipherblocks)

# Second version: using map
def counter_mode_map(blocksize:int,block_cipher:Callable[[bytes,int,bytes],bytes],
                 key:bytes,counter:int,nonce:bytes,msg:bytes) -> bytes :
    msg_blocks = split_blocks(msg,blocksize)
    cipherblocks = map(lambda x: block_encrypt(block_cipher,key,counter+x[0],nonce,x[1]), enumerate(msg_blocks))
    return concat_blocks(array(cipherblocks))

# Third version: using a local loop
def counter_mode_iter(blocksize:int,block_cipher:Callable[[bytes,int,bytes],bytes],
                      key:bytes,counter:int,nonce:bytes,msg:bytes) -> bytes :               
    ciphertext = list(msg)
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
    return bytes(ciphertext)

