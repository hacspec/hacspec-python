module Speclib
open Spec.Lib.IntSeq
open Spec.Lib.IntTypes

let range_t min max = n:nat{n >= min /\ n < max}
let array_t t len = lseq t len
let vlarray_t t = seq t
let uint32_t = uint32
let uint8_t = uint8
let bytes_t len = lbytes len
let vlbytes_t = bytes

let vlcopy (s:seq 'a) = to_lseq s
let copy #len (s:lseq 'a len) = s

let uint32_v x = uint_v #U32 x
let range i = i

let split_blocks (a:seq 'a) (bs:size_nat{bs > 0}) = 
  let (bl,l) = split_blocks (to_lseq a) bs in
  (to_seq bl, to_seq l)

let concat_blocks #a (#len:size_nat) (#bs:size_nat{bs > 0}) (bl:seq (lseq 'a bs){length bl = len / bs}) (l:seq 'a{length l = len % bs}) = 
  concat_blocks #_ #len #bs (to_lseq bl) (to_lseq l)

let rec exp (x:nat) (y:nat) = 
    if y = 0 then 1
    else x `op_Multiply` (exp x (y-1))
let ( **. ) x y = 
  if x = 2 then pow2 y
  else exp x y
type pfelem_t (p:nat) = x:nat{x < p}
let pfelem (p:pos) (x:nat): pfelem_t p = x % p
let pfelem_to_int x = x
let pfadd #p (x:pfelem_t p) (y:pfelem_t p) : pfelem_t p = pfelem p (x + y) 
let ( -. ) x y = x - y
