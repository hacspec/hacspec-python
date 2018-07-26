module Speclib
open Lib.IntTypes
open Lib.Sequence
open Lib.ByteSequence

type nat_t = nat
type pos_t = pos

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

let bitvector (n:numeric) = 
  match n with
  | Word i -> machineint i
  | Int -> False

let comparable (n:numeric) = 
  match n with
  | Word SIZE -> True
  | Word (NATm _) -> True
  | Int -> True
  | _ -> False

let divisible (n:numeric) = 
  match n with
  | Word SIZE -> True
  | Word (NATm _) -> True
  | Int -> True
  | _ -> False

let shiftval (n:numeric{bitvector n}) =
  match n with
  | Word t -> n:nat{n < bits t} //shiftval t

let rotval (n:numeric{bitvector n}) =
  match n with
  | Word t -> n:nat{n > 0 /\ n < bits t} //rotval t

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

let (/.) (#n:numeric{divisible n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) /. b
  | Int -> a / b

let (%.) (#n:numeric{divisible n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) %. b
  | Int -> a % b


let ( <<. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:shiftval n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) <<. u32 b

let ( >>. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:shiftval n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) >>. u32 b

let ( &. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) &. b

let ( |. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) |. b

let ( ^. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) ^. b

let ( <=. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t) <=. b
  | Int -> a <= b

let ( =. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t) =. b
  | Int -> a = b

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

let natmod_t (n:pos) = numeric_t (Word (NATm n))
let natmod n p : natmod_t p = n % p
let natmod_to_nat (#m:pos) (a:natmod_t m) : x:nat{x < m}  = a
let natmod_to_int (#m:pos) (a:natmod_t m) : x:nat{x < m}  = a

let uintn_t (n:nat) = numeric_t (Word (NATm (pow2 n)))
let uint32_t = numeric_t (Word U32)
let bit_t = numeric_t (Word (NATm 2))
let uint8_t = numeric_t (Word U8)
let uint128_t = numeric_t (Word U128)
let uint64_t = numeric_t (Word U64)

let uintn n p : uintn_t p = natmod n (pow2 p)
let bit x : bit_t = modulo x 2
let uint8 x : uint8_t = u8 x
let uint32 x : uint32_t = u32 x
let uint128 x : uint128_t = u128 x

let uintn_to_nat #t (a:uint_t t) : nat = Lib.RawIntTypes.uint_to_nat a
let uintn_to_int #t (a:uint_t t) : nat = Lib.RawIntTypes.uint_to_nat a
let uintn_get_bit #b (x:uintn_t b) (i:nat) : bit_t  = bit (((uintn_to_nat x) / pow2 i) % 2)
let uintn_rotate_left (#t:m_inttype) (a:uint_t t) b = a <<<. (u32 b)
let uintn_rotate_right (#t:m_inttype) (a:uint_t t) b = a >>>. (u32 b)

type result_t (t:Type0) = 
  | Retval of t
  | Error of string
let result_retval #t (x:t) : result_t t = Retval x
let result_error #t (x:string) : result_t t = Error x

let range_t min max = n:nat{n >= min /\ n < max}
unfold let range i = i
let repeati = repeati

let array_t t len = lseq t len
let vlarray_t t = seq t
let array x = x
let array_length a = length a
let array_copy #a #l (x:array_t a l) : array_t a l = x
let op_String_Access #a #len = index #a #len
let op_String_Assignment #a #len = upd #a #len
let array_createL l = createL l
let array_create x y = create x y
let array_slice #l (x:lseq 'a l) y z = slice x y z
let array_update_slice #l (x:lseq 'a l) y z w = update_slice x y z w
val array_split_blocks: #a:Type -> s:seq a -> bs:size_nat{bs > 0} -> (bl:lseq (lseq a bs) (length s / bs) * l:lseq a (length s % bs))
let array_split_blocks #a s bs = 
    let nblocks = length s / bs in
    let rem = length s % bs in
    let blocks = create nblocks (create bs (u8 0)) in
    repeati nblocks (fun i blocks -> blocks.[i] <- sub (to_lseq s) (i `op_Multiply` bs) bs) blocks,
    sub (to_lseq s) (length s - rem) rem 
    
val array_concat_blocks: #a:Type -> #n:size_nat -> #bs:size_nat{bs > 0} -> bl:lseq (lseq a bs) n -> l:seq a -> r:lseq a (n `op_Multiply` bs + length l)
let array_concat_blocks #a #n #bs bl l = 
    let msg = create (n `op_Multiply` bs + length l) (u8 0) in
    let msg = repeati n (fun i msg -> update_sub msg (i `op_Multiply` bs) bs bl.[i]) msg in
    update_sub msg (n `op_Multiply` bs) (length l) l


let bytes_t len = lbytes len
let vlbytes_t = bytes
let bytes x = x
let bytes_copy x = x
let bytes_length x = length x
let bytes_to_uint32s_le #l (b:lbytes (l `op_Multiply` 4)) = uints_from_bytes_le #U32 #l b
let bytes_from_uint32s_le #l (b:lseq uint32_t l) = uints_to_bytes_le #U32 b 
let bytes_to_nat_le #l (b:lbytes l) = nat_from_bytes_le #l b
let bytes_from_nat_le n l = nat_to_bytes_le l n 
let bytes_to_uint128_le #l (b:lbytes l) = uint_from_bytes_le #U128 b
let bytes_from_uint128_le n = uint_to_bytes_le #U128 n
let bytes_to_uint32_be #l (b:lbytes l) = uint_from_bytes_be #U32 b
let bytes_from_uint32_be n = uint_to_bytes_be #U32 n

