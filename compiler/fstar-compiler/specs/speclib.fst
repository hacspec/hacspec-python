module Speclib
open Lib.IntTypes
open Lib.Sequence
open Lib.ByteSequence
open Lib.LoopCombinators
open FStar.Mul
inline_for_extraction type nat_t = nat
inline_for_extraction type pos_t = pos

type numeric = 
  | Word of inttype
  | BV of n:size_nat{n > 0}
  | NATm of n:nat{n > 1}
  | Int 

inline_for_extraction let numeric_t (n:numeric) : Type0 = 
  match n with
  | Word i -> uint_t i PUB
  | BV n -> x:nat{x < pow2 n}
  | NATm n -> x:nat{x < n}
  | Int -> int

inline_for_extraction let numeric_v (#n:numeric)  (x:numeric_t n) : int = 
  match n with
  | Word i -> uint_v (x <: uint_t i PUB)
  | BV n -> x
  | NATm n -> x
  | Int -> x

inline_for_extraction let zero (n:numeric) : numeric_t n = 
  match n with
  | Word t -> nat_to_uint #t #PUB 0
  | BV n -> 0
  | NATm n -> 0
  | Int -> 0

inline_for_extraction let one (n:numeric) : numeric_t n = 
  match n with
  | Word t -> nat_to_uint #t #PUB 1
  | BV n -> 1
  | NATm n -> 1
  | Int -> 1

inline_for_extraction let bitvector (n:numeric) = 
  match n with
  | Word i -> True
  | BV n -> True
  | NATm n -> False
  | Int -> False

inline_for_extraction let comparable (n:numeric) = 
  match n with
  | Word i -> True
  | BV _ -> True
  | NATm _ -> True
  | Int -> True

inline_for_extraction let divisible (n:numeric) = 
  match n with
  | Word U128 -> False
  | Word _ -> True
  | BV n -> True
  | NATm n -> True
  | Int -> True

inline_for_extraction let shiftval (n:numeric{bitvector n}) =
  match n with
  | Word t -> shiftval t
  | BV n -> x:size_t{uint_v x < n}

inline_for_extraction let rotval (n:numeric{bitvector n}) =
  match n with
  | Word t -> rotval t
  | BV n -> x:size_t{uint_v x > 0 /\ uint_v x < n}

inline_for_extraction let (+.) (#n:numeric) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB)  +. b
  | BV n -> (a + b) % pow2 n
  | NATm n -> (a + b) % n
  | Int -> a + b

inline_for_extraction let (-.) (#n:numeric) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB) -. b
  | BV n -> (n + a - b) % pow2 n
  | NATm n -> (n + a - b) % n
  | Int -> a - b

inline_for_extraction let ( *. ) (#n:numeric{n <> Word U128}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB) *. b
  | BV n -> (a `op_Multiply` b) % pow2 n
  | NATm n -> (a `op_Multiply` b) % n
  | Int -> a `op_Multiply` b

#reset-options "--z3rlimit 30"

inline_for_extraction let (/.) (#n:numeric{divisible n}) (a:numeric_t n) (b:numeric_t n{numeric_v b > 0}) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB) /. b
  | BV n -> a / b
  | NATm n -> a / b
  | Int -> a / b

inline_for_extraction let (%.) (#n:numeric{divisible n}) (a:numeric_t n) (b:numeric_t n{numeric_v b > 0}) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB) %. b
  | BV n -> a % b
  | NATm n -> a % b
  | Int -> a % b


inline_for_extraction let ( <<. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:shiftval n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB) <<. b
  | BV n -> (a `op_Multiply` pow2 (uint_v #U32 #PUB b)) % pow2 n


#set-options "--z3rlimit 200 --max_fuel 3 --max_ifuel 5"
inline_for_extraction let ( >>. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:shiftval n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB) >>. b
  | BV n -> let a : (x:nat{x < pow2 n}) = a in
	   let mv = uint_v #U32 #PUB b in
           let x = a / pow2 mv in
	   Math.Lemmas.lemma_div_lt a n mv;
	   x

let natm_to_bv (#n:size_nat{n > 0}) (x:nat{x < pow2 n}) : lseq bit_t n =  
  createi n (fun i -> uint ((x / pow2 i) % 2)) 

let bv_to_natm (#n:size_nat{n > 0}) (x:lseq bit_t n) : (x:nat{x < pow2 n}) = 
  repeati_inductive #nat n 
    (fun i a -> a < pow2 i)
    (fun i a -> a + uint_v x.[i] * pow2 i) 0

inline_for_extraction let ( &. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB) &. b
  | BV n -> let a_bv = natm_to_bv #n a in
	   let b_bv = natm_to_bv #n b in
	   let c_bv = map2 ( &. ) a_bv b_bv in
	   bv_to_natm #n c_bv
    
inline_for_extraction let ( |. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB) |. b
  | BV n -> bv_to_natm #n (map2 ( |. ) (natm_to_bv a) (natm_to_bv b))
  
inline_for_extraction let ( ^. ) (#n:numeric{bitvector n}) (a:numeric_t n) (b:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> (a <: uint_t t PUB) ^. b
  | BV n -> bv_to_natm #n (map2 ( ^. ) (natm_to_bv a) (natm_to_bv b))

inline_for_extraction let ( ~. ) (#n:numeric{bitvector n}) (a:numeric_t n) : numeric_t n = 
  match n with
  | Word t -> ~. (a <: uint_t t PUB) 
  | BV n -> bv_to_natm #n (map ( ~. ) (natm_to_bv a))

inline_for_extraction let ( <. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t PUB) <. b
  | BV n -> a < b
  | NATm m -> a < b
  | Int -> a < b

inline_for_extraction let ( <=. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t PUB) <=. b
  | BV n -> a <= b
  | NATm m -> a <= b
  | Int -> a <= b

inline_for_extraction let ( =. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t PUB) =. b
  | BV m -> a = b
  | NATm m -> a = b
  | Int -> a = b

inline_for_extraction let ( >. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t PUB) >. b
  | BV m -> a > b
  | NATm m -> a > b
  | Int -> a > b

inline_for_extraction let ( >=. ) (#n:numeric{comparable n}) (a:numeric_t n) (b:numeric_t n) : bool = 
  match n with
  | Word t -> (a <: uint_t t PUB) >=. b
  | BV m -> a >= b
  | NATm m -> a >= b
  | Int -> a >= b

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

inline_for_extraction let natmod_t (n:nat{n > 1}) = numeric_t (NATm n)
inline_for_extraction let natmod n p : natmod_t p = n % p
inline_for_extraction let natmod_to_nat (#m:nat{m > 1}) (a:natmod_t m) : x:nat{x < m}  = a
inline_for_extraction let natmod_to_int (#m:nat{m > 1}) (a:natmod_t m) : x:nat{x < m}  = a

inline_for_extraction let uintn_t (n:pos) = numeric_t (NATm (pow2 n))
inline_for_extraction let uint1_t = numeric_t (Word U1)
inline_for_extraction let uint8_t = numeric_t (Word U8)
inline_for_extraction let uint16_t = numeric_t (Word U16)
inline_for_extraction let uint32_t = numeric_t (Word U32)
inline_for_extraction let uint64_t = numeric_t (Word U64)
inline_for_extraction let uint128_t = numeric_t (Word U128)

inline_for_extraction let uintn n p : uintn_t p = natmod n (pow2 p)
inline_for_extraction let bit x : bit_t = uint #U1 #PUB (x % 2)
inline_for_extraction let uint8 x : uint8_t = uint #U8 #PUB  (x % pow2 8)
inline_for_extraction let uint16 x : uint16_t = uint #U16 #PUB  (x % pow2 16)
inline_for_extraction let uint32 x : uint32_t = uint #U32 #PUB  (x % pow2 32)
inline_for_extraction let uint64 x : uint64_t = uint #U64 #PUB  (x % pow2 64)
inline_for_extraction let uint128 x : uint128_t = uint #U128 #PUB  (x % pow2 128)

inline_for_extraction let uintn_to_int #n (a:numeric_t n) : int =
  match n with
  | Word t -> pub_int_v #t a
  | BV m -> a
  | NATm m -> a
  | Int -> a
  
inline_for_extraction let uintn_to_nat #n (a:numeric_t n{numeric_v a >= 0}) : nat = uintn_to_int #n a

inline_for_extraction let uintn_get_bit #n (x:numeric_t n) (i:size_nat) : bit_t = 
  match n with
  | Word t -> if i < bits t then bit ((uintn_to_nat (x >>. size i)) % 2) else bit 0
  | BV m ->  bit (((uintn_to_nat #n x) / pow2 i) % 2)
  | NATm m ->  bit (((uintn_to_nat #n x) / pow2 i) % 2)
  | Int -> bit ((x % pow2 i) % 2)
  
inline_for_extraction let uintn_rotate_left (#t:inttype) (a:uint_t t PUB) (b:nat{b > 0 /\ b < bits t}) : uint_t t PUB = a <<<. size b

inline_for_extraction let uintn_rotate_right (#t:inttype) (a:uint_t t PUB) (b:nat{b > 0 /\ b < bits t}) : uint_t t PUB = a >>>. size b


type result_t (t:Type0) = 
  | Retval of t
  | Error of string
inline_for_extraction let result_retval #t (x:t) : result_t t = Retval x
inline_for_extraction let result_error #t (x:string) : result_t t = Error x

inline_for_extraction let range_t min max = n:nat{n >= min /\ n < max}
unfold let range i = i
inline_for_extraction let repeati = repeati

unfold inline_for_extraction let array_t t len = lseq t len
unfold inline_for_extraction let vlarray_t t = seq t
inline_for_extraction let array x = x
inline_for_extraction let array_length a : numeric_t Int = length a
inline_for_extraction let array_copy #a #l (x:array_t a l) : array_t a l = x
inline_for_extraction let op_String_Access #a #len = index #a #len
inline_for_extraction let op_String_Assignment #a #len = upd #a #len
inline_for_extraction let array_createL l = createL l
inline_for_extraction let array_create x y = create x y
inline_for_extraction let array_slice #l (x:lseq 'a l) y z = slice x y z
inline_for_extraction let array_update_slice #l (x:lseq 'a l) y z w = update_slice x y z w


inline_for_extraction val array_split_blocks: #a:Type -> 
  s:seq a -> bs:nat{bs > 0 /\ bs <= max_size_t /\ length s / bs <= max_size_t} -> 
  (lseq (lseq a bs) (length s / bs) & lseq a (length s % bs))
inline_for_extraction let array_split_blocks #a s bs = 
    let len = length s in
    let nblocks : size_nat = len / bs in
    let rem : size_nat = len % bs in
    assert (nblocks * bs <= len);
    let blocks = createi #(lseq a bs) nblocks
      (fun i -> assert (i + 1 <= nblocks);
	     assert ((i + 1) * bs <= len); 
	     assert (i * bs <= (i + 1) * bs); 
	     let j:n:nat{i * bs <= n /\ n <= len} = (i+1) * bs in
	     Seq.slice s (i * bs) j) in //(i*bs + bs)) in
    let last : lseq a rem = Seq.slice s (len - rem) len  in
    (blocks, last)
    
    
inline_for_extraction val array_concat_blocks: 
  #a:Type -> #n:size_nat -> #bs:size_nat{bs > 0} -> #rem:size_nat{n * bs + rem <= max_size_t} -> 
  bl:lseq (lseq a bs) n -> 
  l:lseq a rem -> 
  r:lseq a (n * bs + rem)
inline_for_extraction let array_concat_blocks #a #n #bs #rem bl l = 
  createi (n * bs + rem) 
    (fun i -> if i < n * bs then 
	      (bl.[i / bs]).[i % bs]
	   else l.[i - (n * bs)])
    

unfold inline_for_extraction let bytes_t len = lseq uint8_t len
unfold inline_for_extraction let vlbytes_t = seq uint8_t
inline_for_extraction let bytes x = x
inline_for_extraction let bytes_copy x = x
inline_for_extraction let bytes_length (x:vlbytes_t) : numeric_t Int = length x
inline_for_extraction let bytes_to_nat_le #l (b:bytes_t l) = nat_from_bytes_le b
inline_for_extraction let bytes_from_nat_le (n:nat) (l:nat{n < pow2 (8 * l)}) = nat_to_bytes_le #PUB l n

inline_for_extraction let bytes_to_uint32s_le (#l:size_nat{l * 4 <= max_size_t})
		      (b:bytes_t (l * 4)) = uints_from_bytes_le #U32 #PUB #l b
inline_for_extraction let bytes_from_uint32s_le (#l:size_nat{l * 4 <= max_size_t}) (b:lseq uint32_t l) : bytes_t (l*4) = uints_to_bytes_le #U32 b 
inline_for_extraction let bytes_to_uint32s_be (#l:size_nat{l * 4 <= max_size_t})
		      (b:bytes_t (l * 4)) = uints_from_bytes_be #U32 #PUB #l b
inline_for_extraction let bytes_from_uint32s_be (#l:size_nat{l * 4 <= max_size_t}) (b:lseq uint32_t l) : bytes_t (l*4) = uints_to_bytes_be #U32 b 

inline_for_extraction let bytes_to_uint64s_le (#l:size_nat{l * 8 <= max_size_t})
		      (b:bytes_t (l * 8)) = uints_from_bytes_le #U64 #PUB #l b
inline_for_extraction let bytes_from_uint64s_le (#l:size_nat{l * 8 <= max_size_t}) (b:lseq uint64_t l) : bytes_t (l*8) = uints_to_bytes_le #U64 b 
inline_for_extraction let bytes_to_uint64s_be (#l:size_nat{l * 8 <= max_size_t})
		      (b:bytes_t (l * 8)) = uints_from_bytes_be #U64 #PUB #l b
inline_for_extraction let bytes_from_uint64s_be (#l:size_nat{l * 8 <= max_size_t}) (b:lseq uint64_t l) : bytes_t (l*8) = uints_to_bytes_be #U64 b 

inline_for_extraction let bytes_to_uint128_le (b:bytes_t 16) = uint_from_bytes_le #U128 #PUB b
inline_for_extraction let bytes_from_uint128_le (u:uint128_t) = uint_to_bytes_le #U128 #PUB u

inline_for_extraction let bytes_to_uint128s_le (#l:size_nat{l * 16 <= max_size_t})
		      (b:bytes_t (l * 16)) = uints_from_bytes_le #U128 #PUB #l b
inline_for_extraction let bytes_from_uint128s_le (#l:size_nat{l * 16 <= max_size_t}) (b:lseq uint128_t l) : bytes_t (l*16) = uints_to_bytes_le #U128 b 
inline_for_extraction let bytes_to_uint128s_be (#l:size_nat{l * 16 <= max_size_t})
		      (b:bytes_t (l * 16)) = uints_from_bytes_be #U128 #PUB #l b
inline_for_extraction let bytes_from_uint128s_be (#l:size_nat{l * 16 <= max_size_t}) (b:lseq uint128_t l) : bytes_t (l*16) = uints_to_bytes_be #U128 b 

