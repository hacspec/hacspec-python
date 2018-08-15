(* Generated from hacspec module ../../../specs/gf128.py *)
module Gf128
open Speclib
let blocksize : int = 16
let block_t : Type0 = array_t uint8_t 16
let key_t : Type0 = array_t uint8_t 16
let tag_t : Type0 = array_t uint8_t 16
let subblock_t : Type0 = ((x:vlbytes_t{ (array_length x) <=. 16 }))
let subblock : Type0 = ((x:vlbytes_t{ (array_length x) <=. 16 }))
let elem_t : Type0 = uint8_t
let elem (x:nat_t) : elem_t = uint128 x
let irred : elem_t = elem 299076299051606071403356588563077529600
let elem_from_bytes (b:array_t uint8_t 16) : elem_t = bytes_to_uint128_be b
let elem_to_bytes (e:elem_t) : array_t uint8_t 16 = bytes_from_uint128_be e
let fadd (x:elem_t) (y:elem_t) : elem_t = x ^. y
let fmul (x:elem_t) (y:elem_t) : elem_t =
  let res = elem 0 in
  let sh = x in
  let res, sh =
    repeati 128
      (fun i (res, sh) ->
          let res = if (uintn_get_bit y (127 -. i)) <> (bit 0) then res ^. sh else res in
          let sh = if (uintn_get_bit sh 0) <> (bit 0) then (sh >>. 1) ^. irred else sh >>. 1 in
          (res, sh))
      (res, sh)
  in
  res
let encode (block:subblock_t) : elem_t =
  let b = bytes (array_create 16 (uint8 0)) in
  let b = array_update_slice b 0 (array_length block) (block) in
  elem_from_bytes b
let decode (e:elem_t) : block_t = elem_to_bytes e
let update (r:elem_t) (block:subblock_t) (acc:elem_t) : elem_t = fmul (fadd (encode block) acc) r
let poly (text:vlbytes_t) (r:elem_t) : elem_t =
  let blocks, last = array_split_blocks text blocksize in
  let acc = elem 0 in
  let acc = repeati (array_length blocks) (fun i acc -> update r blocks.[ i ] acc) acc in
  let acc = if (array_length last) >. 0 then update r (bytes last) acc else acc in
  acc
let gmac (text:vlbytes_t) (k:key_t) : tag_t =
  let s = bytes (array_create blocksize (uint8 0)) in
  let r = encode k in
  let a = poly text r in
  let m = decode (fadd a (encode s)) in
  m

