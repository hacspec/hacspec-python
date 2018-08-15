(* Generated from hacspec module ../../../specs/poly1305.py *)
module Poly1305
open Speclib
let blocksize : int = 16
let block_t : Type0 = array_t uint8_t 16
let key_t : Type0 = array_t uint8_t 32
let tag_t : Type0 = array_t uint8_t 16
let subblock_t : Type0 = ((x:vlbytes_t{ (bytes_length x) <=. 16 }))
let p130m5 : nat_t = (2 **. 130) -. 5
let felem_t : Type0 = natmod_t p130m5
let felem (n:nat_t) : felem_t = natmod n p130m5
let encode (block:subblock_t) : felem_t =
  let b = array_create 16 (uint8 0) in
  let b = array_update_slice b 0 (bytes_length block) (block) in
  let welem = felem (bytes_to_nat_le b) in
  let lelem = felem (2 **. (8 *. (array_length block))) in
  lelem +. welem
let encode_r (r:block_t) : felem_t =
  let ruint = bytes_to_uint128_le r in
  let ruint = ruint &. (uint128 21267647620597763993911028882763415551) in
  let r_nat = uintn_to_nat ruint in
  felem r_nat
let poly (text:vlbytes_t) (r:felem_t) : felem_t =
  let blocks, last = array_split_blocks text blocksize in
  let acc = felem 0 in
  let acc = repeati (array_length blocks) (fun i acc -> (acc +. (encode blocks.[ i ])) *. r) acc in
  let acc = if (array_length last) >. 0 then (acc +. (encode last)) *. r else acc in
  acc
let poly1305_mac (text:vlbytes_t) (k:key_t) : tag_t =
  let r = array_slice k 0 blocksize in
  let s = array_slice k blocksize (2 *. blocksize) in
  let relem = encode_r r in
  let selem = bytes_to_uint128_le s in
  let a = poly text relem in
  let n = (uint128 ((natmod_to_nat a) % (2 **. 128))) +. selem in
  bytes_from_uint128_le n

