from typing import Callable, List, Iterator, Tuple
from functools import reduce

def separate_blocks(blocksize:int,len:int,msg:bytes) -> List[bytes]:
    return [msg[x:x+blocksize] for x in range(0,len,blocksize)]

def concat_blocks(blocks:List[bytes]) -> bytes:
    concat = [b for block in blocks for b in block]
    return bytes(concat)

def block_encrypt(block_cipher:Callable[[bytes,int,bytes],bytes],
                  key:bytes,counter:int,nonce:bytes,len:int,msg:bytes) -> bytes:
    keyblock = block_cipher(key,counter,nonce)
    cipherblock = [x ^ y for (x,y) in zip(keyblock,msg)]
    return bytes(cipherblock)

def counter_mode(blocksize:int,block_cipher:Callable[[bytes,int,bytes],bytes],
                 key:bytes,counter:int,nonce:bytes,len:int,msg:bytes) -> bytes :
    msg_blocks = separate_blocks(blocksize,len,msg)
    cipherblocks = [block_encrypt(block_cipher,key,counter+i,nonce,64,b) for (i,b) in enumerate(msg_blocks)]
    return concat_blocks(cipherblocks)
                                               
def counter_mode_iter(blocksize:int,block_cipher:Callable[[bytes,int,bytes],bytes],
                    key:bytes,counter:int,nonce:bytes,len:int,msg:bytes) -> bytes :               
    ciphertext = list(msg)
    nblocks = len // blocksize;
    last = len % blocksize
    for i in range(nblocks):
        keyblock = block_cipher(key,counter+i,nonce)
        start = i * blocksize
        for j in range(blocksize):
            ciphertext[start+j] ^= keyblock[j]
    if last > 0:
        keyblock = block_cipher(key,counter+nblocks,nonce)
        start = len - last
        for j in range(last):
            ciphertext[start+j] ^= keyblock[j]
    return bytes(ciphertext)
            
def mapi_blocks(blocksize:int,
                func:Callable[[Tuple[int,bytes]],bytes],
                len:int,msg:bytes) -> bytes:
    msg_blocks = separate_blocks(blocksize,len,msg)
    map_blocks = [func(x) for x in enumerate(msg_blocks)]
    return concat_blocks(map_blocks)

def reduce_blocks(blocksize:int, default: bytes,
                  func:Callable[[bytes,bytes],bytes],
                  len:int,msg:bytes) -> bytes:
    msg_blocks = separate_blocks(blocksize,len,msg)
    acc = reduce(func, msg_blocks, default)
    return acc

        
