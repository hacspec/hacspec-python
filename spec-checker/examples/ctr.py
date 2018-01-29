from typing import Callable

def counter_mode(blocksize:int,block_cipher:Callable[[bytes,int,bytes],bytes],
                key:bytes,counter:int,nonce:bytes,len:int,msg:bytes) :
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
            
