module Speclib
open Lib.IntTypes
open Lib.Sequence
open Lib.ByteSequence

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

let array x = x
let array_length a = length a
let array_copy a = a
let op_String_Access #a #len = index #a #len
let op_String_Assignment #a #len = upd #a #len
let repeati = repeati

let op_Plus_Dot #t a b = op_Plus_Dot #t a b
let op_Hat_Dot #t a b = op_Plus_Dot #t a b

let uintn_rotate_left #t (a:uint_t t) b = a <<<. (u32 b)
let uintn_rotate_right #t (a:uint_t t) b = a >>>. (u32 b)
let uint8 x = u8 x
let uint32 x = u32 x
let array_createL l = createL l
let array_create x y = create x y
let array_slice #l (x:lseq 'a l) y z = slice x y z
let array_update_slice #l (x:lseq 'a l) y z w = update_slice x y z w

let bytes_copy x = x
let bytes_to_uint32s_le #l (b:lbytes (l `op_Multiply` 4)) = uints_from_bytes_le #U32 #l b
let bytes_from_uint32s_le #l (b:lseq uint32_t l) = uints_to_bytes_le #U32 b 

assume val array_split_blocks: #a:Type -> s:seq a -> bs:size_nat{bs > 0} -> (bl:lseq (lseq a bs) (length s / bs) * l:lseq a (length s % bs))
assume val array_concat_blocks: #a:Type -> #len:size_nat -> #bs:size_nat{bs > 0} -> 
  bl:seq (lseq a bs){length bl == len / bs} -> l:seq a{length l == len % bs} ->
  r:seq a{length r == len}

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

