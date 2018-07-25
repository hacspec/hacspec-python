module Speclib
open Lib.IntTypes
open Lib.Sequence
open Lib.ByteSequence

type numeric = 
  | Word of inttype
  | Int 

let numeric_t (n:numeric) = 
  match n with
  | Word i -> uint_t i
  | Int -> int

let zero (n:numeric) : numeric_t n = 
  match n with
  | Word t -> nat_to_uint #t 0
  | Int -> 0

let one (n:numeric) : numeric_t n = 
  match n with
  | Word t -> nat_to_uint #t 1
  | Int -> 1

let machineint (n:numeric) = 
  match n with
  | Word i -> machineint i
  | Int -> False

let comparable (n:numeric) = 
  match n with
  | Word SIZE -> True
  | Word (NATm _) -> True
  | Int -> True
  | _ -> False

let (+.) (#n:numeric) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) +. b
  | Int -> a + b

let (-.) (#n:numeric) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) -. b
  | Int -> a - b

let ( *. ) (#n:numeric{n <> Word U128}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) *. b
  | Int -> a `op_Multiply` b

let ( &. ) (#n:numeric{machineint n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) &. b

let ( <=. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t) <=. b
  | Int -> a <= b

let ( >. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t) >. b
  | Int -> a > b

let rec exp  (#n:numeric{n <> Word U128}) (x:numeric_t n) (y:nat) : numeric_t n = 
    if y = 0 then one n
    else x *. (exp x (y-1))

let ( **. ) (#n:numeric{n <> Word U128}) (x:numeric_t n) (y:nat) : numeric_t n = 
    if n = Int && x = 2 then pow2 y
    else exp #n x y

  
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

let uintn_rotate_left (#t:m_inttype) (a:uint_t t) b = a <<<. (u32 b)
let uintn_rotate_right (#t:m_inttype) (a:uint_t t) b = a >>>. (u32 b)
let uint8 x = u8 x
let uint32 x = u32 x
let uint128 x = u128 x
let array_createL l = createL l
let array_create x y = create x y
let array_slice #l (x:lseq 'a l) y z = slice x y z
let array_update_slice #l (x:lseq 'a l) y z w = update_slice x y z w

let natmod_t (n:pos) = numeric_t (Word (NATm n))
let natmod n p : natmod_t p = n % p

let uintn_to_nat #t (a:uint_t t) : nat = Lib.RawIntTypes.uint_to_nat a
let natmod_to_nat (#m:pos) (a:natmod_t m) : x:nat{x < m}  = a

let bytes_copy x = x
let bytes_length x = length x
let bytes_to_uint32s_le #l (b:lbytes (l `op_Multiply` 4)) = uints_from_bytes_le #U32 #l b
let bytes_from_uint32s_le #l (b:lseq uint32_t l) = uints_to_bytes_le #U32 b 
let bytes_to_nat_le #l (b:lbytes l) = nat_from_bytes_le #l b
let bytes_from_nat_le l n = nat_to_bytes_le l n 
let bytes_to_uint128_le #l (b:lbytes l) = uint_from_bytes_le #U128 b
let bytes_from_uint128_le n = uint_to_bytes_le #U128 n

assume val array_split_blocks: #a:Type -> s:seq a -> bs:size_nat{bs > 0} -> (bl:lseq (lseq a bs) (length s / bs) * l:lseq a (length s % bs))
assume val array_concat_blocks: #a:Type -> #len:size_nat -> #bs:size_nat{bs > 0} -> 
  bl:seq (lseq a bs){length bl == len / bs} -> l:seq a{length l == len % bs} ->
  r:seq a{length r == len}

type pfelem_t (p:nat) = x:nat{x < p}
let pfelem (p:pos) (x:nat): pfelem_t p = x % p
let pfelem_to_int x = x
let pfadd #p (x:pfelem_t p) (y:pfelem_t p) : pfelem_t p = pfelem p (x + y) 

