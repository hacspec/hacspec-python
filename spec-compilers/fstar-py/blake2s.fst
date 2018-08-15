module Blake2S
#set-options "--z3rlimit 20 --max_fuel 0"
open Spec.Lib.IntTypes
open Spec.Lib.RawIntTypes
open Spec.Lib.IntSeq
open Speclib
let bits_in_word = 0x20 
let rounds_in_f = 0xa 
let block_bytes = 0x40 
let R1 = 0x10 
let R2 = 0xc 
let R3 = 0x8 
let R4 = 0x7 
let working_vector_t = array_t uint32_t 0x10 
let hash_vector_t = array_t uint32_t 0x8 
let index_t = range_t 0x0 0x10 
let SIGMA : array_t index_t (0x10 *. 0xc) = let l_ = [ 0x0; 0x1; 0x2; 0x3; 0x4; 0x5; 0x6; 0x7; 0x8; 0x9; 0xa; 0xb; 0xc; 0xd; 0xe; 0xf; 0xe; 0xa; 0x4; 0x8; 0x9; 0xf; 0xd; 0x6; 0x1; 0xc; 0x0; 0x2; 0xb; 0x7; 0x5; 0x3; 0xb; 0x8; 0xc; 0x0; 0x5; 0x2; 0xf; 0xd; 0xa; 0xe; 0x3; 0x6; 0x7; 0x1; 0x9; 0x4; 0x7; 0x9; 0x3; 0x1; 0xd; 0xc; 0xb; 0xe; 0x2; 0x6; 0x5; 0xa; 0x4; 0x0; 0xf; 0x8; 0x9; 0x0; 0x5; 0x7; 0x2; 0x4; 0xa; 0xf; 0xe; 0x1; 0xb; 0xc; 0x6; 0x8; 0x3; 0xd; 0x2; 0xc; 0x6; 0xa; 0x0; 0xb; 0x8; 0x3; 0x4; 0xd; 0x7; 0x5; 0xf; 0xe; 0x1; 0x9; 0xc; 0x5; 0x1; 0xf; 0xe; 0xd; 0x4; 0xa; 0x0; 0x7; 0x6; 0x3; 0x9; 0x2; 0x8; 0xb; 0xd; 0xb; 0x7; 0xe; 0xc; 0x1; 0x3; 0x9; 0x5; 0x0; 0xf; 0x4; 0x8; 0x6; 0x2; 0xa; 0x6; 0xf; 0xe; 0x9; 0xb; 0x3; 0x0; 0x8; 0xc; 0x2; 0xd; 0x7; 0x1; 0x4; 0xa; 0x5; 0xa; 0x2; 0x8; 0x4; 0x7; 0x6; 0x1; 0x5; 0xf; 0xb; 0x9; 0xe; 0x3; 0xc; 0xd; 0x0 ] in 
                                            assert_norm(List.Tot.length l_ == 160);
                                            createL l_ 
let IV = let l_ = [ u32 0x6a09e667; u32 0xbb67ae85; u32 0x3c6ef372; u32 0xa54ff53a; u32 0x510e527f; u32 0x9b05688c; u32 0x1f83d9ab; u32 0x5be0cd19 ] in 
         assert_norm(List.Tot.length l_ == 8);
         createL l_ 
let _G (v:working_vector_t) (a:index_t) (b:index_t) (c:index_t) (d:index_t) (x:uint32_t) (y:uint32_t) : working_vector_t =
  let v = v.[a] <- ((v.[a] +. v.[b]) +. x) in 
  let v = v.[d] <- uint32_t.rotate_right (v.[d] ^. v.[a]) R1 in 
  let v = v.[c] <- (v.[c] +. v.[d]) in 
  let v = v.[b] <- uint32_t.rotate_right (v.[b] ^. v.[c]) R2 in 
  let v = v.[a] <- ((v.[a] +. v.[b]) +. y) in 
  let v = v.[d] <- uint32_t.rotate_right (v.[d] ^. v.[a]) R3 in 
  let v = v.[c] <- (v.[c] +. v.[d]) in 
  let v = v.[b] <- uint32_t.rotate_right (v.[b] ^. v.[c]) R4 in 
  v 
let _F (h:hash_vector_t) (m:working_vector_t) (t:uint64_t) (flag:bool) : hash_vector_t =
  let v = create 0x10 (u32 0x0) in 
  let v = update_slice v 0x0 0x8 h in 
  let v = update_slice v 0x8 0x10 IV in 
  let v = v.[0xc] <- (v.[0xc] ^. u32 t) in 
  let v = v.[0xd] <- (v.[0xd] ^. u32 (t >>. 0x20)) in 
  let v = if ((flag = True)) then (let v = v.[0xe] <- (v.[0xe] ^. u32 0xffffffff) in v )else (v) in 
  let () = repeati (range rounds_in_f)
    (fun i () ->
      let s = slice SIGMA (i *. 0x10) ((i +. 0x1) *. 0x10) in 
      let v = _G v 0x0 0x4 0x8 0xc m.[s.[0x0]] m.[s.[0x1]] in 
      let v = _G v 0x1 0x5 0x9 0xd m.[s.[0x2]] m.[s.[0x3]] in 
      let v = _G v 0x2 0x6 0xa 0xe m.[s.[0x4]] m.[s.[0x5]] in 
      let v = _G v 0x3 0x7 0xb 0xf m.[s.[0x6]] m.[s.[0x7]] in 
      let v = _G v 0x0 0x5 0xa 0xf m.[s.[0x8]] m.[s.[0x9]] in 
      let v = _G v 0x1 0x6 0xb 0xc m.[s.[0xa]] m.[s.[0xb]] in 
      let v = _G v 0x2 0x7 0x8 0xd m.[s.[0xc]] m.[s.[0xd]] in 
      let v = _G v 0x3 0x4 0x9 0xe m.[s.[0xe]] m.[s.[0xf]] in 
      ())
    () in 
  let h = repeati (range 0x8)
    (fun i h ->
      let h = h.[i] <- ((h.[i] ^. v.[i]) ^. v.[(i +. 0x8)]) in 
      h)
    h in 
  h 
type data_internal_t = x:bytes_t{(length x < (0x2 **. 0x40)) && ((length x %. block_bytes) = 0x0)}

type key_t = x:vlbytes_t{(length x <= 0x20)}

type key_size_t = x:nat{(x <= 0x20)}

type out_size_t = x:nat{(x <= 0x20)}

let blake2s_internal (data:data_internal_t) (input_bytes:uint64_t) (kk:key_size_t) (nn:out_size_t) : contract vlbytes_t Lambda(args=arguments(args=arg(arg='data',
annotation=None,
type_comment=None)
arg(arg='input_bytes',
annotation=None,
type_comment=None)
arg(arg='kk',
annotation=None,
type_comment=None)
arg(arg='nn',
annotation=None,
type_comment=None),
vararg=None,
kwonlyargs=,
kw_defaults=,
kwarg=None,
defaults=),
body=True) Lambda(args=arguments(args=arg(arg='data',
annotation=None,
type_comment=None)
arg(arg='input_bytes',
annotation=None,
type_comment=None)
arg(arg='kk',
annotation=None,
type_comment=None)
arg(arg='nn',
annotation=None,
type_comment=None)
arg(arg='res',
annotation=None,
type_comment=None),
vararg=None,
kwonlyargs=,
kw_defaults=,
kwarg=None,
defaults=),
body=((length res) = nn)) =
  let h = copy IV in 
  let h = h.[0x0] <- (((h.[0x0] ^. u32 0x1010000) ^. (u32 kk <<. 0x8)) ^. u32 nn) in 
  let data_blocks = (length data /. block_bytes) in 
  let () = if ((data_blocks > 0x1)) then (let () = repeati (range (data_blocks -. 0x1))
      (fun i () ->
        let h = _F h (vlbytes.to_uint32s_le slice data (block_bytes *. i) (block_bytes *. (i +. 0x1))) (u64 ((i +. 0x1) *. block_bytes)) False in 
        ())
      () in () )else (()) in 
  let () = if ((kk = 0x0)) then (let h = _F h (vlbytes.to_uint32s_le slice data (block_bytes *. (data_blocks -. 0x1)) (block_bytes *. data_blocks)) (u64 input_bytes) True in () )else (let h = _F h (vlbytes.to_uint32s_le slice data (block_bytes *. (data_blocks -. 0x1)) (block_bytes *. data_blocks)) (u64 (input_bytes +. block_bytes)) True in ()) in 
  slice vlbytes.from_uint32s_le h None nn 
let max_size_t = ((0x2 **. 0x20) -. 0x1) 
type data_t = x:vlbytes_t{(vlbytes.lenght x < (max_size_t -. (0x2 *. block_bytes)))}

let blake2s (data:data_t) (key:key_t) (nn:out_size_t) : contract vlbytes_t Lambda(args=arguments(args=arg(arg='data',
annotation=None,
type_comment=None)
arg(arg='key',
annotation=None,
type_comment=None)
arg(arg='nn',
annotation=None,
type_comment=None),
vararg=None,
kwonlyargs=,
kw_defaults=,
kwarg=None,
defaults=),
body=True) Lambda(args=arguments(args=arg(arg='data',
annotation=None,
type_comment=None)
arg(arg='key',
annotation=None,
type_comment=None)
arg(arg='nn',
annotation=None,
type_comment=None)
arg(arg='res',
annotation=None,
type_comment=None),
vararg=None,
kwonlyargs=,
kw_defaults=,
kwarg=None,
defaults=),
body=((length res) = nn)) =
  let ll = length data in 
  let kk = length key in 
  let data_blocks = (((ll -. 0x1) /. block_bytes) +. 0x1) in 
  let padded_data_length = (data_blocks *. block_bytes) in 
  let padded_data = if ((kk = 0x0)) then (let padded_data = create padded_data_length (u8 0x0) in 
    let padded_data = update_slice padded_data None ll data in padded_data )else (let padded_data = create (padded_data_length +. block_bytes) (u8 0x0) in 
    let padded_data = update_slice padded_data 0x0 kk key in 
    let padded_data = update_slice padded_data block_bytes (block_bytes +. ll) key in padded_data) in 
  blake2s_internal padded_data ll kk nn 
