(* Generated from hacspec module ../specs/gf128.py *)
module Gf128
open Speclib
#reset-options "--z3rlimit 60"
let blocksize : int = 16

let block_t : Type0 = array_t uint8_t 16

let key_t : Type0 = array_t uint8_t 16

let tag_t : Type0 = array_t uint8_t 16

let subblock_t : Type0 = (x:vlbytes_t{(array_length x) <=. 16})

let subblock : Type0 = (x:vlbytes_t{(array_length x) <=. 16})

let elem_t : Type0 = uint128_t

let elem (x : nat_t) : elem_t = 
uint128 x

let irred : elem_t = elem 299076299051606071403356588563077529600

let load_elem (b : array_t uint8_t 16) : elem_t = 
bytes_to_uint128_be b

let store_elem (e : elem_t) : array_t uint8_t 16 = 
bytes_from_uint128_be e

let encode (block : subblock_t) : elem_t = 
let b = bytes (array_create 16 (uint8 0)) in 
let b = array_update_slice b 0 (array_length block) (block) in 
load_elem b

let decode (e : elem_t) : block_t = 
store_elem e

let fadd (x : elem_t) (y : elem_t) : elem_t = 
x ^. y

let fmul (x : elem_t) (y : elem_t) : elem_t = 
let res = elem 0 in 
let sh = x in 
let index = 0 in 
let (index,res,sh) = repeati 128 (fun i (index,res,sh) -> let index = op_Subtraction 127 i in 
let res = if (uintn_get_bit y index) <> (bit 0) then res ^. sh else res in 
let sh = if (uintn_get_bit sh 0) <> (bit 0) then (sh >>. 1) ^. irred else sh >>. 1 in 
(index,res,sh)) (index,res,sh) in 
res

let init (h : block_t) : (elem_t * elem_t) = 
let r = encode h in 
let acc = elem 0 in 
(r,acc)

let set_acc (st : (elem_t * elem_t)) (acc : elem_t) : (elem_t * elem_t) = 
let (r,accBefore) = st in 
(r,acc)

let update (r : elem_t) (block : subblock_t) (acc : elem_t) : elem_t = 
let accNew = fmul (fadd (encode block) acc) r in 
accNew

let poly (text : vlbytes_t) (acc : elem_t) (r : elem_t) : elem_t = 
let (blocks,last) = array_split_blocks text blocksize in 
let acc = repeati (array_length blocks) (fun i acc -> update r blocks.[i] acc) acc in 
let acc = if (array_length last) >. 0 then update r (bytes last) acc else acc in 
acc

let finish (acc : elem_t) (s : tag_t) : tag_t = 
decode (fadd acc (encode s))

let gmul (text : vlbytes_t) (h : block_t) : tag_t = 
let (r,acc) = init h in 
let acc = poly text acc r in 
decode acc

let gmac (text : vlbytes_t) (k : key_t) : tag_t = 
let s = bytes (array_create blocksize (uint8 0)) in 
let (r,acc) = init k in 
let a = poly text acc r in 
let m = finish a s in 
m
