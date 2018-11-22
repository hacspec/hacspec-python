module Speclib
open Lib.IntTypes
open Lib.Sequence
open Lib.ByteSequence

inline_for_extraction type nat_t = nat
inline_for_extraction type pos_t = pos

type numeric = 
  | Word of inttype
  | Int 

inline_for_extraction let numeric_t (n:numeric) = 
  match n with
  | Word i -> uint_t i
  | Int -> int

inline_for_extraction let zero (n:numeric) : numeric_t n = 
  match n with
  | Word t -> nat_to_uint #t 0
  | Int -> 0

inline_for_extraction let one (n:numeric) : numeric_t n = 
  match n with
  | Word t -> nat_to_uint #t 1
  | Int -> 1

inline_for_extraction let bitvector (n:numeric) = 
  match n with
  | Word i -> machineint i
  | Int -> False

inline_for_extraction let comparable (n:numeric) = 
  match n with
  | Word SIZE -> True
  | Word (NATm _) -> True
  | Int -> True
  | _ -> False

inline_for_extraction let divisible (n:numeric) = 
  match n with
  | Word SIZE -> True
  | Word (NATm _) -> True
  | Int -> True
  | _ -> False

inline_for_extraction let shiftval (n:numeric{bitvector n}) =
  match n with
  | Word t -> n:nat{n < bits t} //shiftval t

inline_for_extraction let rotval (n:numeric{bitvector n}) =
  match n with
  | Word t -> n:nat{n > 0 /\ n < bits t} //rotval t

inline_for_extraction let (+.) (#n:numeric) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) +. b
  | Int -> a + b

inline_for_extraction let (-.) (#n:numeric) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) -. b
  | Int -> a - b

inline_for_extraction let ( *. ) (#n:numeric{n <> Word U128}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) *. b
  | Int -> a `op_Multiply` b

inline_for_extraction let (/.) (#n:numeric{divisible n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) /. b
  | Int -> a / b

inline_for_extraction let (%.) (#n:numeric{divisible n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) %. b
  | Int -> a % b


inline_for_extraction let ( <<. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:shiftval n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) <<. u32 b

inline_for_extraction let ( >>. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:shiftval n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) >>. u32 b

inline_for_extraction let ( &. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) &. b

inline_for_extraction let ( |. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) |. b

inline_for_extraction let ( ^. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t) ^. b

inline_for_extraction let ( <=. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t) <=. b
  | Int -> a <= b

inline_for_extraction let ( =. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t) =. b
  | Int -> a = b

inline_for_extraction let ( >. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t) >. b
  | Int -> a > b

inline_for_extraction let rec exp  (#n:numeric{n <> Word U128}) (x:numeric_t n) (y:nat) : numeric_t n = 
    if y = 0 then one n 
    else if y = 1 then x
    else 
      let xn = exp x (y / 2) in
      let xn2 = xn *. xn in
      if y % 2 = 0 then xn2
      else xn2 *. x

inline_for_extraction let ( **. ) (#n:numeric{n <> Word U128}) (x:numeric_t n) (y:nat) : numeric_t n = 
    if n = Int && x = 2 then pow2 y
    else exp #n x y

inline_for_extraction let natmod_t (n:pos) = numeric_t (Word (NATm n))
inline_for_extraction let natmod n p : natmod_t p = n % p
inline_for_extraction let natmod_to_nat (#m:pos) (a:natmod_t m) : x:nat{x < m}  = a
inline_for_extraction let natmod_to_int (#m:pos) (a:natmod_t m) : x:nat{x < m}  = a

inline_for_extraction let uintn_t (n:nat) = numeric_t (Word (NATm (pow2 n)))
inline_for_extraction let bit_t:eqtype = numeric_t (Word (NATm 2))
inline_for_extraction let uint8_t = numeric_t (Word U8)
inline_for_extraction let uint32_t = numeric_t (Word U32)
inline_for_extraction let uint64_t = numeric_t (Word U64)
inline_for_extraction let uint128_t = numeric_t (Word U128)

inline_for_extraction let uintn n p : uintn_t p = natmod n (pow2 p)
inline_for_extraction let bit x : bit_t = modulo x 2
inline_for_extraction let uint8 x : uint8_t = u8 (x % (pow2 8))
inline_for_extraction let uint32 x : uint32_t = u32 (x % (pow2 32))
inline_for_extraction let uint64 x : uint64_t = u64 (x % (pow2 64))
inline_for_extraction let uint128 x : uint128_t = u128 (x % (pow2 128))

inline_for_extraction let uintn_to_nat #n (a:numeric_t n) : nat =
  match n with
  | Word t -> Lib.RawIntTypes.uint_to_nat #t a
  | Int -> a
  
inline_for_extraction let uintn_to_int #n (a:numeric_t n) : nat = uintn_to_nat #n a
inline_for_extraction let uintn_get_bit #n (x:numeric_t n) (i:nat) : bit_t = 
  match n with
  | Word (NATm m) ->  bit (((uintn_to_nat #n x) / pow2 i) % 2)
  | Word _ -> bit ((uintn_to_nat (x >>. i)) % 2)
  | Int -> bit ((x % pow2 i) % 2)
  
inline_for_extraction let uintn_rotate_left (#t:m_inttype) (a:uint_t t) b = a <<<. (u32 b)
inline_for_extraction let uintn_rotate_right (#t:m_inttype) (a:uint_t t) b = a >>>. (u32 b)

type result_t (t:Type0) = 
  | Retval of t
  | Error of string
inline_for_extraction let result_retval #t (x:t) : result_t t = Retval x
inline_for_extraction let result_error #t (x:string) : result_t t = Error x

inline_for_extraction let range_t min max = n:nat{n >= min /\ n < max}
unfold let range i = i
inline_for_extraction let repeati = repeati

inline_for_extraction let array_t t len = lseq t len
inline_for_extraction let vlarray_t t = seq t
inline_for_extraction let array x = x
inline_for_extraction let array_length a = length a
inline_for_extraction let array_copy #a #l (x:array_t a l) : array_t a l = x
inline_for_extraction let op_String_Access #a #len = index #a #len
inline_for_extraction let op_String_Assignment #a #len = upd #a #len
inline_for_extraction let array_createL l = createL l
inline_for_extraction let array_create x y = create x y
inline_for_extraction let array_slice #l (x:lseq 'a l) y z = slice x y z
inline_for_extraction let array_update_slice #l (x:lseq 'a l) y z w = update_slice x y z w
inline_for_extraction val array_split_blocks: #a:Type -> s:seq a -> bs:size_nat{bs > 0} -> (bl:lseq (lseq a bs) (length s / bs) * l:lseq a (length s % bs))
inline_for_extraction let array_split_blocks #a s bs = 
    let nblocks = length s / bs in
    let rem = length s % bs in
    let blocks = create nblocks (create bs (u8 0)) in
    repeati nblocks (fun i blocks -> blocks.[i] <- sub (to_lseq s) (i `op_Multiply` bs) bs) blocks,
    sub (to_lseq s) (length s - rem) rem 
    
inline_for_extraction val array_concat_blocks: #a:Type -> #n:size_nat -> #bs:size_nat{bs > 0} -> bl:lseq (lseq a bs) n -> l:seq a -> r:lseq a (n `op_Multiply` bs + length l)
inline_for_extraction let array_concat_blocks #a #n #bs bl l = 
    let msg = create (n `op_Multiply` bs + length l) (u8 0) in
    let msg = repeati n (fun i msg -> update_sub msg (i `op_Multiply` bs) bs bl.[i]) msg in
    update_sub msg (n `op_Multiply` bs) (length l) l


inline_for_extraction let bytes_t len = lbytes len
inline_for_extraction let vlbytes_t = bytes
inline_for_extraction let bytes x = x
inline_for_extraction let bytes_copy x = x
inline_for_extraction let bytes_length x = length x
inline_for_extraction let bytes_to_uint32s_le #l (b:lbytes (l `op_Multiply` 4)) = uints_from_bytes_le #U32 #l b
inline_for_extraction let bytes_from_uint32s_le #l (b:lseq uint32_t l) = uints_to_bytes_le #U32 b 
inline_for_extraction let bytes_to_nat_le #l (b:lbytes l) = nat_from_bytes_le #l b
inline_for_extraction let bytes_from_nat_le (n:nat) l = nat_to_bytes_le l n
inline_for_extraction let bytes_to_uint64_le #l (b:lbytes l) = uint_from_bytes_le #U64 b
inline_for_extraction let bytes_from_uint64_le (n:uint64_t) = uint_to_bytes_le #U64 n
inline_for_extraction let bytes_to_uint128_le #l (b:lbytes l) = uint_from_bytes_le #U128 b
inline_for_extraction let bytes_from_uint128_le (n:uint128_t) = uint_to_bytes_le #U128 n
inline_for_extraction let bytes_to_uint128_be #l (b:lbytes l) = uint_from_bytes_be #U128 b
inline_for_extraction let bytes_from_uint128_be (n:uint128_t) = uint_to_bytes_be #U128 n
inline_for_extraction let bytes_to_uint32_be #l (b:lbytes l) = uint_from_bytes_be #U32 b
inline_for_extraction let bytes_from_uint32_be (n:uint32_t) = uint_to_bytes_be #U32 n

