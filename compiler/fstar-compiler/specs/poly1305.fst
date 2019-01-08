(* Generated from hacspec module ../../../specs/poly1305.py *)
module Poly1305
open Speclib
#reset-options "--z3rlimit 60"
let blocksize: nat_t = 16

let block_t: Type0 = array_t uint8_t 16

let key_t: Type0 = array_t uint8_t 32

let tag_t: Type0 = array_t uint8_t 16

let subblock_t: Type0 = (x: vlbytes_t{(array_length x) <=. 16})

let p130m5: int = op_Subtraction (pow2 130) 5

let felem_t: Type0 = natmod_t p130m5

let felem (n: nat_t) : felem_t = natmod n p130m5

let from_elem (x: felem_t) : nat_t = x

let update1 (block: subblock_t) (acc: felem_t) (r: felem_t) : felem_t =
  let b = array_create 16 (uint8 0) in
  let b = array_update_slice b 0 (bytes_length block) (block) in
  let n = (felem (pow2 (8 *. (array_length block)))) +. (felem (bytes_to_nat_le b)) in
  let acc = (n +. acc) *. r in
  acc

let encode (block: subblock_t) : felem_t =
  let b = array_create 16 (uint8 0) in
  let b = array_update_slice b 0 (bytes_length block) (block) in
  let n = (felem (pow2 (8 *. (array_length block)))) +. (felem (bytes_to_nat_le b)) in
  n

let poly (text: vlbytes_t) (acc: felem_t) (r: felem_t) : felem_t =
  let blocks, last = array_split_blocks text blocksize in
  let acc = repeati (array_length blocks) (fun i acc -> update1 blocks.[ i ] acc r) acc in
  let acc = if (array_length last) >. 0 then update1 last acc r else acc in
  acc

let finish (acc: felem_t) (selem: uint128_t) : vlbytes_t =
  let n = (uint128 (natmod_to_nat acc)) +. selem in
  bytes_from_uint128_le n

let encode_r (r: block_t) : felem_t =
  let r = r.[ 3 ] <- r.[ 3 ] &. (uint8 15) in
  let r = r.[ 7 ] <- r.[ 7 ] &. (uint8 15) in
  let r = r.[ 11 ] <- r.[ 11 ] &. (uint8 15) in
  let r = r.[ 15 ] <- r.[ 15 ] &. (uint8 15) in
  let r = r.[ 4 ] <- r.[ 4 ] &. (uint8 252) in
  let r = r.[ 8 ] <- r.[ 8 ] &. (uint8 252) in
  let r = r.[ 12 ] <- r.[ 12 ] &. (uint8 252) in
  let ruint = bytes_to_uint128_le r in
  let r_nat = uintn_to_nat ruint in
  felem r_nat

let poly1305_init (k: key_t) : (felem_t * uint128_t * felem_t) =
  let r = array_slice k 0 blocksize in
  let s = array_slice k blocksize (op_Multiply 2 blocksize) in
  let relem = encode_r r in
  let selem = bytes_to_uint128_le s in
  let acc = felem 0 in
  (relem, selem, acc)

let poly1305_mac (text: vlbytes_t) (k: key_t) : tag_t =
  let relem = felem 0 in
  let selem = uint128 0 in
  let acc = felem 0 in
  let relem, selem, acc = poly1305_init k in
  let a = poly text acc relem in
  finish a selem

