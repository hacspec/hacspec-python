module Speclib
open Spec.Lib.IntSeq
open Spec.Lib.IntTypes

let range_t min max = n:nat{n >= min /\ n < max}
let array_t t len = lseq t len
let vlarray_t t = seq t
let uint32_t = uint32
let uint8_t = uint8
let uint128_t = uint128
let uint64_t = uint64
let bytes_t len = lbytes len
let vlbytes_t = bytes

let vlcopy (s:seq 'a) = to_lseq s
let copy #len (s:lseq 'a len) = s

let uint32_v x = uint_v #U32 x
unfold let range i = i

val split_blocks: #a:Type -> s:seq a -> bs:size_nat{bs > 0} -> (bl:seq (lseq a bs){length bl == length s / bs} * l:seq a{length l == length s % bs})
let split_blocks #a (s:seq a) (bs:size_nat{bs > 0}) = 
  let (bl,l) = split_blocks (to_lseq s) bs in
  (to_seq bl, to_seq l)

val concat_blocks: #a:Type -> #len:size_nat -> #bs:size_nat{bs > 0} -> 
  bl:seq (lseq a bs){length bl == len / bs} -> l:seq a{length l == len % bs} ->
  r:seq a{length r == len}
let concat_blocks #_ #len #bs bl l =
  to_seq (concat_blocks #_ #len #bs (to_lseq bl) (to_lseq l))

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

