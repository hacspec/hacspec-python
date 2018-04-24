module Blake2
#set-options "--z3rlimit 20 --max_fuel 0"
open Spec.Lib.IntTypes
open Spec.Lib.RawIntTypes
open Spec.Lib.IntSeq
open Speclib
let variant = refine3 nat_t Lambda(args=arguments(args=arg(arg='x',
              annotation=None,
              type_comment=None),
              vararg=None,
              kwonlyargs=,
              kw_defaults=,
              kwarg=None,
              defaults=),
              body=(x = 0x0) || (x = 0x1)) 
let blake2 (v:variant) : None =
  let () = if ((v = 0x1)) then (let bits_in_word = 0x40 in 
    let rounds_in_f = 0xc in 
    let block_bytes = 0x80 in 
    let R1 = 0x20 in 
    let R2 = 0x18 in 
    let R3 = 0x10 in 
    let R4 = 0x3f in 
    let working_vector_t = array_t uint64_t 0x10 in 
    let hash_vector_t = array_t uint64_t 0x8 in 
    let index_t = range_t 0x0 0x10 in 
    let IV = let l_ = [ u64 0x6a09e667f3bcc908; u64 0xbb67ae8584caa73b; u64 0x3c6ef372fe94f82b; u64 0xa54ff53a5f1d36f1; u64 0x510e527fade682d1; u64 0x9b05688c2b3e6c1f; u64 0x1f83d9abfb41bd6b; u64 0x5be0cd19137e2179 ] in 
             assert_norm(List.Tot.length l_ == 8);
             createL l_ in 
    let to_word = uint64 in 
    let word_t = uint64_t in 
    let minus_one = u64 0xffffffffffffffff in 
    type data_internal_t = x:bytes_t{(length x < (0x2 **. 0x40)) && ((length x %. block_bytes) = 0x0)}

    type key_t = x:vlbytes_t{(length x <= 0x40)}

    type key_size_t = x:nat{(x <= 0x40)}

    type out_size_t = x:nat{(x <= 0x20)}

    let to_words_le = vlbytes.to_uint64s_le in 
    let from_words_le = vlbytes.from_uint64s_le in 
    let low_bits = to_word in 
    let high_bits = Lambda(args=arguments(args=arg(arg='x',
                    annotation=None,
                    type_comment=None),
                    vararg=None,
                    kwonlyargs=,
                    kw_defaults=,
                    kwarg=None,
                    defaults=),
                    body=to_word (x >>. 0x40)) in 
    let to_double_word = uint128 in 
    let max_size_t = ((0x2 **. 0x40) -. 0x1) in 
    type data_t = x:vlbytes_t{(vlbytes.lenght x < (max_size_t -. (0x2 *. block_bytes)))}
() )else (let bits_in_word = 0x20 in 
    let rounds_in_f = 0xa in 
    let block_bytes = 0x40 in 
    let R1 = 0x10 in 
    let R2 = 0xc in 
    let R3 = 0x8 in 
    let R4 = 0x7 in 
    let working_vector_t = array_t uint32_t 0x10 in 
    let hash_vector_t = array_t uint32_t 0x8 in 
    let index_t = range_t 0x0 0x10 in 
    let IV = let l_ = [ u32 0x6a09e667; u32 0xbb67ae85; u32 0x3c6ef372; u32 0xa54ff53a; u32 0x510e527f; u32 0x9b05688c; u32 0x1f83d9ab; u32 0x5be0cd19 ] in 
             assert_norm(List.Tot.length l_ == 8);
             createL l_ in 
    let to_word = uint32 in 
    let word_t = uint32_t in 
    let minus_one = u32 0xffffffff in 
    type data_internal_t = x:bytes_t{(length x < (0x2 **. 0x40)) && ((length x %. block_bytes) = 0x0)}

    type key_t = x:vlbytes_t{(length x <= 0x20)}

    type key_size_t = x:nat{(x <= 0x20)}

    type out_size_t = x:nat{(x <= 0x20)}

    let to_words_le = vlbytes.to_uint32s_le in 
    let from_words_le = vlbytes.from_uint32s_le in 
    let low_bits = to_word in 
    let high_bits = Lambda(args=arguments(args=arg(arg='x',
                    annotation=None,
                    type_comment=None),
                    vararg=None,
                    kwonlyargs=,
                    kw_defaults=,
                    kwarg=None,
                    defaults=),
                    body=to_word (x >>. 0x20)) in 
    let to_double_word = uint64 in 
    let max_size_t = ((0x2 **. 0x20) -. 0x1) in 
    type data_t = x:vlbytes_t{(vlbytes.lenght x < (max_size_t -. (0x2 *. block_bytes)))}
()) in 
  let SIGMA : array_t index_t (0x10 *. 0xc) = let l_ = [ 0x0; 0x1; 0x2; 0x3; 0x4; 0x5; 0x6; 0x7; 0x8; 0x9; 0xa; 0xb; 0xc; 0xd; 0xe; 0xf; 0xe; 0xa; 0x4; 0x8; 0x9; 0xf; 0xd; 0x6; 0x1; 0xc; 0x0; 0x2; 0xb; 0x7; 0x5; 0x3; 0xb; 0x8; 0xc; 0x0; 0x5; 0x2; 0xf; 0xd; 0xa; 0xe; 0x3; 0x6; 0x7; 0x1; 0x9; 0x4; 0x7; 0x9; 0x3; 0x1; 0xd; 0xc; 0xb; 0xe; 0x2; 0x6; 0x5; 0xa; 0x4; 0x0; 0xf; 0x8; 0x9; 0x0; 0x5; 0x7; 0x2; 0x4; 0xa; 0xf; 0xe; 0x1; 0xb; 0xc; 0x6; 0x8; 0x3; 0xd; 0x2; 0xc; 0x6; 0xa; 0x0; 0xb; 0x8; 0x3; 0x4; 0xd; 0x7; 0x5; 0xf; 0xe; 0x1; 0x9; 0xc; 0x5; 0x1; 0xf; 0xe; 0xd; 0x4; 0xa; 0x0; 0x7; 0x6; 0x3; 0x9; 0x2; 0x8; 0xb; 0xd; 0xb; 0x7; 0xe; 0xc; 0x1; 0x3; 0x9; 0x5; 0x0; 0xf; 0x4; 0x8; 0x6; 0x2; 0xa; 0x6; 0xf; 0xe; 0x9; 0xb; 0x3; 0x0; 0x8; 0xc; 0x2; 0xd; 0x7; 0x1; 0x4; 0xa; 0x5; 0xa; 0x2; 0x8; 0x4; 0x7; 0x6; 0x1; 0x5; 0xf; 0xb; 0x9; 0xe; 0x3; 0xc; 0xd; 0x0; 0x0; 0x1; 0x2; 0x3; 0x4; 0x5; 0x6; 0x7; 0x8; 0x9; 0xa; 0xb; 0xc; 0xd; 0xe; 0xf; 0xe; 0xa; 0x4; 0x8; 0x9; 0xf; 0xd; 0x6; 0x1; 0xc; 0x0; 0x2; 0xb; 0x7; 0x5; 0x3 ] in 
                                              assert_norm(List.Tot.length l_ == 192);
                                              createL l_ in 
  let _G (v:working_vector_t) (a:index_t) (b:index_t) (c:index_t) (d:index_t) (x:uint64_t) (y:uint64_t) : working_vector_t =
    let v = v.[a] <- ((v.[a] +. v.[b]) +. x) in 
    let v = v.[d] <- word_t.rotate_right (v.[d] ^. v.[a]) R1 in 
    let v = v.[c] <- (v.[c] +. v.[d]) in 
    let v = v.[b] <- word_t.rotate_right (v.[b] ^. v.[c]) R2 in 
    let v = v.[a] <- ((v.[a] +. v.[b]) +. y) in 
    let v = v.[d] <- word_t.rotate_right (v.[d] ^. v.[a]) R3 in 
    let v = v.[c] <- (v.[c] +. v.[d]) in 
    let v = v.[b] <- word_t.rotate_right (v.[b] ^. v.[c]) R4 in 
    v in 
  let _F (h:hash_vector_t) (m:working_vector_t) (t:uint128_t) (flag:bool) : hash_vector_t =
    let v = create 0x10 (to_word 0x0) in 
    let v = update_slice v 0x0 0x8 h in 
    let v = update_slice v 0x8 0x10 IV in 
    let v = v.[0xc] <- (v.[0xc] ^. low_bits t) in 
    let v = v.[0xd] <- (v.[0xd] ^. high_bits (t >>. 0x40)) in 
    let v = if ((flag = True)) then (let v = v.[0xe] <- (v.[0xe] ^. minus_one) in v )else (v) in 
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
    h in 
  let blake2_internal (data:data_internal_t) (input_bytes:uint128_t) (kk:key_size_t) (nn:out_size_t) : contract vlbytes_t Lambda(args=arguments(args=arg(arg='data',
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
    let h = h.[0x0] <- (((h.[0x0] ^. to_word 0x1010000) ^. (to_word kk <<. 0x8)) ^. to_word nn) in 
    let data_blocks = (length data /. block_bytes) in 
    let () = if ((data_blocks > 0x1)) then (let () = repeati (range (data_blocks -. 0x1))
        (fun i () ->
          let h = _F h (to_words_le slice data (block_bytes *. i) (block_bytes *. (i +. 0x1))) (to_double_word ((i +. 0x1) *. block_bytes)) False in 
          ())
        () in () )else (()) in 
    let () = if ((kk = 0x0)) then (let h = _F h (to_words_le slice data (block_bytes *. (data_blocks -. 0x1)) (block_bytes *. data_blocks)) (to_double_word input_bytes) True in () )else (let h = _F h (to_words_le slice data (block_bytes *. (data_blocks -. 0x1)) (block_bytes *. data_blocks)) (to_double_word (input_bytes +. block_bytes)) True in ()) in 
    slice from_words_le h None nn in 
  let blake2 (data:data_t) (key:key_t) (nn:out_size_t) : contract vlbytes_t Lambda(args=arguments(args=arg(arg='data',
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
    blake2_internal padded_data ll kk nn in 
  blake2 
let blake2s = blake2 (variant 0x0) 
let blake2b = blake2 (variant 0x1) 
