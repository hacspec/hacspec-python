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

### setup

* A 256-bit one-time key
* The output is a 128-bit tag.
* set the constant prime "P" be `2^130-5: 3fffffffffffffffffffffffffffffffb`.
* divide the message into 16-byte blocks

This is translated into the following hacspec definition.

---

### setup hacspec & F\*

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

```ocaml
let blocksize: int = 16
let block_t: Type0 = array_t uint8_t 16
let key_t: Type0 = array_t uint8_t 32
let tag_t: Type0 = array_t uint8_t 16
let subblock_t: Type0 = (x: vlbytes_t{(bytes_length x) <=. 16})
let p130m5: nat_t = (2 **. 130) -. 5

let felem_t: Type0 = natmod_t p130m5
let felem (n: nat_t) : felem_t = natmod n p130m5
```

---

## bytes to int rfc

```
le_bytes_to_num(msg[((i-1)*16)..(i*16)] | [0x01])
```

---

### bytes to int hacspec & F\*

```python
def encode(block: subblock_t) -> felem_t:
    b : block_t = array.create(16, uint8(0))
    b[0:bytes.length(block)] = block
    welem : felem_t = felem(bytes.to_nat_le(b))
    lelem : felem_t = felem(2 ** (8 * array.length(block)))
    return lelem + welem
```

```ocaml
let encode (block: subblock_t) : felem_t =
  let b = array_create 16 (uint8 0) in
  let b = array_update_slice b 0 (bytes_length block) (block) in
  let welem = felem (bytes_to_nat_le b) in
  let lelem = felem (2 **. (8 *. (array_length block))) in
  lelem +. welem
```

---

## clamp rfc

```
clamp(r): r &= 0x0ffffffc0ffffffc0ffffffc0fffffff
```

---

### clamp hacspec & F\*

```python
def encode_r(r: block_t) -> felem_t:
    ruint : uint128_t = bytes.to_uint128_le(r)
    ruint = ruint & uint128(0x0ffffffc0ffffffc0ffffffc0fffffff)
    r_nat : nat_t = uintn.to_nat(ruint)
    return felem(r_nat)
```

```ocaml
let encode_r (r: block_t) : felem_t =
  let ruint = bytes_to_uint128_le r in
  let ruint = ruint &. (uint128 21267647620597763993911028882763415551) in
  let r_nat = uintn_to_nat ruint in
  felem r_nat
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

### poly hacspec & F\*


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

```ocaml
let poly (text: vlbytes_t) (r: felem_t) : felem_t =
  let blocks, last = array_split_blocks text blocksize in
  let acc = felem 0 in
  let acc = repeati (array_length blocks)
    (fun i acc -> (acc +. (encode blocks.[ i ])) *. r) acc in
  let acc = if (array_length last) >. 0 then
    (acc +. (encode last)) *. r else acc in
  acc
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

## poly mac hacspec & F\*

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

```ocaml
let poly1305_mac (text: vlbytes_t) (k: key_t) : tag_t =
  let r = array_slice k 0 blocksize in
  let s = array_slice k blocksize (2 *. blocksize) in
  let relem = encode_r r in
  let selem = bytes_to_uint128_le s in
  let a = poly text relem in
  let n = (uint128 ((natmod_to_nat a) % (2 **. 128))) +. selem in
  bytes_from_uint128_le n
```

---

## Test and check hacspec

```
λ make poly1305-test
PYTHONPATH=. python tests/poly1305_test.py
Poly1305 Test  0 passed.
Poly1305 Test  1  passed.
...
```

```
λ make poly1305-check
PYTHONPATH=. python lib/check.py specs/poly1305.py
specs/poly1305.py is a valid hacspec.
```

---

## Compile to F\*

Assume `HACL_HOME` and `FSTAR_HOME` are set.

---

## Compile to F\*

```
make -C fstar-compiler/specs/ poly1305.fst
```

```
../../to_fstar.native ../../../specs/poly1305.py > poly1305_pre.fst
/home/franziskus/Code/hacl-star/dependencies/FStar//bin/fstar.exe --include /home/franziskus/Code/hacl-star//lib --include /home/franziskus/Code/hacl-star//lib/fst --expose_interfaces --indent poly1305_pre.fst > poly1305.fst
rm poly1305_pre.fst
```

---

## Run tests in ocaml

```
make -C fstar-compiler/specs/ poly1305.exe
```

```
mkdir -p poly1305-ml
/home/franziskus/Code/hacl-star/dependencies/FStar//bin/fstar.exe --include /home/franziskus/Code/hacl-star//lib --include /home/franziskus/Code/hacl-star//lib/fst --expose_interfaces --lax --codegen OCaml --extract_module Speclib --extract_module Lib.IntTypes --extract_module Lib.RawIntTypes  --extract_module Lib.Sequence --extract_module Lib.ByteSequence --extract_module poly1305 --odir poly1305-ml /home/franziskus/Code/hacl-star//lib/fst/Lib.IntTypes.fst /home/franziskus/Code/hacl-star//lib/fst/Lib.RawIntTypes.fst /home/franziskus/Code/hacl-star//lib/fst/Lib.Sequence.fst /home/franziskus/Code/hacl-star//lib/fst/Lib.ByteSequence.fst speclib.fst /home/franziskus/Code/hacl-star//lib/fst/Lib.IntTypes.fst /home/franziskus/Code/hacl-star//lib/fst/Lib.RawIntTypes.fst /home/franziskus/Code/hacl-star//lib/fst/Lib.Sequence.fst /home/franziskus/Code/hacl-star//lib/fst/Lib.ByteSequence.fst speclib.fst poly1305.fst
Extracted module IntTypes
Extracted module RawIntTypes
Extracted module Sequence
Extracted module ByteSequence
Extracted module Speclib
Extracted module Poly1305
All verification conditions discharged successfully
touch poly1305-ml
cp tests/testutil.ml poly1305-ml/
cp tests/poly1305_test.ml poly1305-ml/
OCAMLPATH="/home/franziskus/Code/hacl-star/dependencies/FStar//bin" ocamlfind opt -package fstarlib -linkpkg -g
  -w -8 -w -20 -g -I poly1305-ml poly1305-ml/Lib_IntTypes.ml poly1305-ml/Lib_RawIntTypes.ml poly1305-ml/Lib_Sequence.ml poly1305-ml/Lib_ByteSequence.ml poly1305-ml/Speclib.ml  poly1305-ml/Poly1305.ml poly1305-ml/testutil.ml poly1305-ml/poly1305_test.ml -o poly1305.exe
File "poly1305-ml/Lib_Sequence.ml", line 356, characters 16-19:
Warning 26: unused variable len.
./poly1305.exe
Poly1305 Test 0 passed.
Poly1305 Test 1 passed.
```

---

## Typecheck

```
make -C fstar-compiler/specs/ poly1305.fst.checked
```

```
make: Entering directory '/mnt/c/Users/Franziskus/Code/hacspec/compiler/fstar-compiler/specs'
/home/franziskus/Code/hacl-star/dependencies/FStar//bin/fstar.exe --include /home/franziskus/Code/hacl-star//lib --include /home/franziskus/Code/hacl-star//lib/fst --expose_interfaces poly1305.fst
Verified module: Poly1305 (10932 milliseconds)
All verification conditions discharged successfully
make: Leaving directory '/mnt/c/Users/Franziskus/Code/hacspec/compiler/fstar-compiler/specs'
```
