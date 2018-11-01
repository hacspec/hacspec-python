---
title: "poly1305"
description: "how to write and use hacspec"
outputs: ["Reveal"]
---

[RFC 7539](https://tools.ietf.org/html/rfc7539) Section 2.5.1: Poly1305

```
clamp(r): r &= 0x0ffffffc0ffffffc0ffffffc0fffffff
poly1305_mac(msg, key):
   r = (le_bytes_to_num(key[0..15])
   clamp(r)
   s = le_num(key[16..31])
   accumulator = 0
   p = (1<<130)-5
   for i=1 upto ceil(msg length in bytes / 16)
      n = le_bytes_to_num(msg[((i-1)*16)..(i*16)] | [0x01])
      a += n
      a = (r * a) % p
      end
   a += s
   return num_to_16_le_bytes(a)
   end
```

---

## Translating RFC specification to hacpsec
The algorithm can be directly translated into hacspec.

---

## setup

* A 256-bit one-time key
* The output is a 128-bit tag.
* set the constant prime "P" be `2^130-5: 3fffffffffffffffffffffffffffffffb`.
* divide the message into 16-byte blocks

This is translated into the following hacspec definition.

---

## setup

```python
blocksize:int = 16
block_t = bytes_t(16)
key_t = bytes_t(32)
tag_t = bytes_t(16)
subblock_t = refine_t(vlbytes_t, lambda x: bytes.length(x) <= 16)
p130m5 : nat_t = (2 ** 130) - 5
felem_t = natmod_t(p130m5)

def felem(n:nat_t) -> felem_t:
    return natmod(n,p130m5)
```

---

## bytes to int rfc

```
le_bytes_to_num(msg[((i-1)*16)..(i*16)] | [0x01])
```

---

## bytes to int hacspec

```python
def encode(block: subblock_t) -> felem_t:
    b : block_t = array.create(16, uint8(0))
    b[0:bytes.length(block)] = block
    welem : felem_t = felem(bytes.to_nat_le(b))
    lelem : felem_t = felem(2 ** (8 * array.length(block)))
    return lelem + welem
```

---

## clamp rfc

```
clamp(r): r &= 0x0ffffffc0ffffffc0ffffffc0fffffff
```

---

## clamp hacspec

```python
def encode_r(r: block_t) -> felem_t:
    ruint : uint128_t = bytes.to_uint128_le(r)
    ruint = ruint & uint128(0x0ffffffc0ffffffc0ffffffc0fffffff)
    r_nat : nat_t = uintn.to_nat(ruint)
    return felem(r_nat)
```

---

## poly rfc

```
a = 0
for i=1 upto ceil(msg length in bytes / 16)
   n = le_bytes_to_num(msg[((i-1)*16)..(i*16)] | [0x01])
   a += n
   a = (r * a) % p
   end
```

---

## poly hacspec


```python
def poly(text: vlbytes_t, r: felem_t) -> felem_t:
    blocks : vlarray_t(block_t)
    last : subblock_t
    blocks, last = array.split_blocks(text, blocksize)
    acc : felem_t = felem(0)
    for i in range(array.length(blocks)):
        acc = (acc + encode(blocks[i])) * r
    if (array.length(last) > 0):
        acc = (acc + encode(last)) * r
    return acc
```

---

## poly mac rfc

```
poly1305_mac(msg, key):
   r = (le_bytes_to_num(key[0..15])
   clamp(r)
   s = le_num(key[16..31])
   p = (1<<130)-5
   a = poly(msg, r)
   a += s
   return num_to_16_le_bytes(a)
   end
```

---

## poly mac hacspec

```python
def poly1305_mac(text: vlbytes_t, k: key_t) -> tag_t:
    r : block_t = k[0:blocksize]
    s : block_t = k[blocksize:2*blocksize]
    relem : felem_t = encode_r(r) # clamp
    selem : uint128_t = bytes.to_uint128_le(s)
    a : felem_t   = poly(text, relem)
    n : uint128_t = uint128(natmod.to_nat(a)) + selem
    return bytes.from_uint128_le(n)
```
