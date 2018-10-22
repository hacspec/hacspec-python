(* Generated from hacspec module ../../../specs/aes.py *)
module Aes
open Speclib
let blocksize: int = 16
let block_t: Type0 = array_t uint8_t 16
let subblock_t: Type0 = (x: vlbytes_t{(array_length x) <=. blocksize})
let rowindex_t: Type0 = range_t 0 4
let expindex_t: Type0 = range_t 0 48
let word_t: Type0 = array_t uint8_t 4
let key_t: Type0 = array_t uint8_t 16
let nonce_t: Type0 = array_t uint8_t 12
let bytes_144_t: Type0 = array_t uint8_t 144
let bytes_176_t: Type0 = array_t uint8_t 176
let index_t: Type0 = range_t 0 16
let rotval_t: Type0 = range_t 1 32
let state_t: Type0 = array_t uint32_t 16
let sbox_t: Type0 = array_t uint8_t 256
let sbox: sbox_t =
  array (array_createL [
          uint8 99; uint8 124; uint8 119; uint8 123; uint8 242; uint8 107; uint8 111; uint8 197;
          uint8 48; uint8 1; uint8 103; uint8 43; uint8 254; uint8 215; uint8 171; uint8 118;
          uint8 202; uint8 130; uint8 201; uint8 125; uint8 250; uint8 89; uint8 71; uint8 240;
          uint8 173; uint8 212; uint8 162; uint8 175; uint8 156; uint8 164; uint8 114; uint8 192;
          uint8 183; uint8 253; uint8 147; uint8 38; uint8 54; uint8 63; uint8 247; uint8 204;
          uint8 52; uint8 165; uint8 229; uint8 241; uint8 113; uint8 216; uint8 49; uint8 21;
          uint8 4; uint8 199; uint8 35; uint8 195; uint8 24; uint8 150; uint8 5; uint8 154; uint8 7;
          uint8 18; uint8 128; uint8 226; uint8 235; uint8 39; uint8 178; uint8 117; uint8 9;
          uint8 131; uint8 44; uint8 26; uint8 27; uint8 110; uint8 90; uint8 160; uint8 82;
          uint8 59; uint8 214; uint8 179; uint8 41; uint8 227; uint8 47; uint8 132; uint8 83;
          uint8 209; uint8 0; uint8 237; uint8 32; uint8 252; uint8 177; uint8 91; uint8 106;
          uint8 203; uint8 190; uint8 57; uint8 74; uint8 76; uint8 88; uint8 207; uint8 208;
          uint8 239; uint8 170; uint8 251; uint8 67; uint8 77; uint8 51; uint8 133; uint8 69;
          uint8 249; uint8 2; uint8 127; uint8 80; uint8 60; uint8 159; uint8 168; uint8 81;
          uint8 163; uint8 64; uint8 143; uint8 146; uint8 157; uint8 56; uint8 245; uint8 188;
          uint8 182; uint8 218; uint8 33; uint8 16; uint8 255; uint8 243; uint8 210; uint8 205;
          uint8 12; uint8 19; uint8 236; uint8 95; uint8 151; uint8 68; uint8 23; uint8 196;
          uint8 167; uint8 126; uint8 61; uint8 100; uint8 93; uint8 25; uint8 115; uint8 96;
          uint8 129; uint8 79; uint8 220; uint8 34; uint8 42; uint8 144; uint8 136; uint8 70;
          uint8 238; uint8 184; uint8 20; uint8 222; uint8 94; uint8 11; uint8 219; uint8 224;
          uint8 50; uint8 58; uint8 10; uint8 73; uint8 6; uint8 36; uint8 92; uint8 194; uint8 211;
          uint8 172; uint8 98; uint8 145; uint8 149; uint8 228; uint8 121; uint8 231; uint8 200;
          uint8 55; uint8 109; uint8 141; uint8 213; uint8 78; uint8 169; uint8 108; uint8 86;
          uint8 244; uint8 234; uint8 101; uint8 122; uint8 174; uint8 8; uint8 186; uint8 120;
          uint8 37; uint8 46; uint8 28; uint8 166; uint8 180; uint8 198; uint8 232; uint8 221;
          uint8 116; uint8 31; uint8 75; uint8 189; uint8 139; uint8 138; uint8 112; uint8 62;
          uint8 181; uint8 102; uint8 72; uint8 3; uint8 246; uint8 14; uint8 97; uint8 53; uint8 87;
          uint8 185; uint8 134; uint8 193; uint8 29; uint8 158; uint8 225; uint8 248; uint8 152;
          uint8 17; uint8 105; uint8 217; uint8 142; uint8 148; uint8 155; uint8 30; uint8 135;
          uint8 233; uint8 206; uint8 85; uint8 40; uint8 223; uint8 140; uint8 161; uint8 137;
          uint8 13; uint8 191; uint8 230; uint8 66; uint8 104; uint8 65; uint8 153; uint8 45;
          uint8 15; uint8 176; uint8 84; uint8 187; uint8 22
        ])
let subBytes (state: block_t) : block_t =
  let st = bytes (array_copy state) in
  let st = repeati 16 (fun i st -> st.[ i ] <- sbox.[ uintn_to_int state.[ i ] ]) st in
  st
let shiftRow (i: rowindex_t) (shift: rowindex_t) (state: block_t) : block_t =
  let out = bytes (array_copy state) in
  let out = out.[ i ] <- state.[ i +. (4 *. (shift % 4)) ] in
  let out = out.[ i +. 4 ] <- state.[ i +. (4 *. ((shift +. 1) % 4)) ] in
  let out = out.[ i +. 8 ] <- state.[ i +. (4 *. ((shift +. 2) % 4)) ] in
  let out = out.[ i +. 12 ] <- state.[ i +. (4 *. ((shift +. 3) % 4)) ] in
  out
let shiftRows (state: block_t) : block_t =
  let state = shiftRow 1 1 state in
  let state = shiftRow 2 2 state in
  let state = shiftRow 3 3 state in
  state
let xtime (x: uint8_t) : uint8_t =
  let x1 = x <<. 1 in
  let x7 = x >>. 7 in
  let x71 = x7 &. (uint8 1) in
  let x711b = x71 *. (uint8 27) in
  x1 ^. x711b
let mixColumn (c: rowindex_t) (state: block_t) : block_t =
  let i0 = 4 *. c in
  let s0 = state.[ i0 ] in
  let s1 = state.[ i0 +. 1 ] in
  let s2 = state.[ i0 +. 2 ] in
  let s3 = state.[ i0 +. 3 ] in
  let st = bytes (array_copy state) in
  let tmp = ((s0 ^. s1) ^. s2) ^. s3 in
  let st = st.[ i0 ] <- (s0 ^. tmp) ^. (xtime (s0 ^. s1)) in
  let st = st.[ i0 +. 1 ] <- (s1 ^. tmp) ^. (xtime (s1 ^. s2)) in
  let st = st.[ i0 +. 2 ] <- (s2 ^. tmp) ^. (xtime (s2 ^. s3)) in
  let st = st.[ i0 +. 3 ] <- (s3 ^. tmp) ^. (xtime (s3 ^. s0)) in
  st
let mixColumns (state: block_t) : block_t =
  let state = mixColumn 0 state in
  let state = mixColumn 1 state in
  let state = mixColumn 2 state in
  let state = mixColumn 3 state in
  state
let addRoundKey (state: block_t) (key: block_t) : block_t =
  let out = bytes (array_copy state) in
  let out = repeati 16 (fun i out -> out.[ i ] <- out.[ i ] ^. key.[ i ]) out in
  out
let aes_enc (state: block_t) (round_key: block_t) : block_t =
  let state = subBytes state in
  let state = shiftRows state in
  let state = mixColumns state in
  let state = addRoundKey state round_key in
  state
let aes_enc_last (state: block_t) (round_key: block_t) : block_t =
  let state = subBytes state in
  let state = shiftRows state in
  let state = addRoundKey state round_key in
  state
let rounds (state: block_t) (key: bytes_144_t) : block_t =
  let out = bytes (array_copy state) in
  let out =
    repeati 9 (fun i out -> aes_enc out (array_slice key (16 *. i) ((16 *. i) +. 16))) out
  in
  out
let block_cipher (input: block_t) (key: bytes_176_t) : block_t =
  let state = bytes (array_copy input) in
  let k0 = array_slice key 0 16 in
  let k = array_slice key 16 (10 *. 16) in
  let kn = array_slice key (10 *. 16) (11 *. 16) in
  let state = addRoundKey state k0 in
  let state = rounds state k in
  let state = aes_enc_last state kn in
  state
let rotate_word (w: word_t) : word_t =
  let out = bytes (array_copy w) in
  let out = out.[ 0 ] <- w.[ 1 ] in
  let out = out.[ 1 ] <- w.[ 2 ] in
  let out = out.[ 2 ] <- w.[ 3 ] in
  let out = out.[ 3 ] <- w.[ 0 ] in
  out
let sub_word (w: word_t) : word_t =
  let out = bytes (array_copy w) in
  let out = out.[ 0 ] <- sbox.[ uintn_to_int w.[ 0 ] ] in
  let out = out.[ 1 ] <- sbox.[ uintn_to_int w.[ 1 ] ] in
  let out = out.[ 2 ] <- sbox.[ uintn_to_int w.[ 2 ] ] in
  let out = out.[ 3 ] <- sbox.[ uintn_to_int w.[ 3 ] ] in
  out
let rcon_t: Type0 = array_t uint8_t 11
let rcon: rcon_t =
  array (array_createL [
          uint8 141; uint8 1; uint8 2; uint8 4; uint8 8; uint8 16; uint8 32; uint8 64; uint8 128;
          uint8 27; uint8 54
        ])
let aes_keygen_assist (w: word_t) (rcon: uint8_t) : word_t =
  let k = rotate_word w in
  let k = sub_word k in
  let k = k.[ 0 ] <- k.[ 0 ] ^. rcon in
  k
let key_expansion_word (w0: word_t) (w1: word_t) (i: expindex_t) : word_t =
  let k = bytes (array_copy w1) in
  let k = if (i % 4) = 0 then aes_keygen_assist k rcon.[ i /. 4 ] else k in
  let k = repeati 4 (fun i k -> k.[ i ] <- k.[ i ] ^. w0.[ i ]) k in
  k
let key_expansion (key: block_t) : array_t uint8_t 176 =
  let key_ex = bytes (array_create (11 *. 16) (uint8 0)) in
  let key_ex = array_update_slice key_ex 0 16 (key) in
  let i = 0 in
  let i, key_ex =
    repeati 40
      (fun j (i, key_ex) ->
          let i = j +. 4 in
          let key_ex =
            array_update_slice key_ex
              (4 *. i)
              ((4 *. i) +. 4)
              (key_expansion_word (array_slice key_ex ((4 *. i) -. 16) ((4 *. i) -. 12))
                  (array_slice key_ex ((4 *. i) -. 4) (4 *. i))
                  i)
          in
          (i, key_ex))
      (i, key_ex)
  in
  key_ex
let aes128_encrypt_block (k: key_t) (input: array_t uint8_t 16) : block_t =
  let key_ex = key_expansion k in
  let out = block_cipher input key_ex in
  out
let aes128_ctr_keyblock (k: key_t) (n: nonce_t) (c: uint32_t) : block_t =
  let input = bytes (array_create 16 (uint8 0)) in
  let input = array_update_slice input 0 12 (n) in
  let input = array_update_slice input 12 16 (bytes_from_uint32_be c) in
  aes128_encrypt_block k input
let xor_block (block: block_t) (keyblock: block_t) : block_t =
  let out = bytes_copy block in
  let out = repeati blocksize (fun i out -> out.[ i ] <- out.[ i ] ^. keyblock.[ i ]) out in
  out
let aes128_counter_mode (key: key_t) (nonce: nonce_t) (counter: uint32_t) (msg: vlbytes_t)
  : vlbytes_t =
  let blocks, last = array_split_blocks msg blocksize in
  let keyblock = array_create blocksize (uint8 0) in
  let last_block = array_create blocksize (uint8 0) in
  let ctr = counter in
  let blocks, ctr, keyblock =
    repeati (array_length blocks)
      (fun i (blocks, ctr, keyblock) ->
          let keyblock = aes128_ctr_keyblock key nonce ctr in
          let blocks = blocks.[ i ] <- xor_block blocks.[ i ] keyblock in
          let ctr = ctr +. uint32 1 in
          (blocks, ctr, keyblock))
      (blocks, ctr, keyblock)
  in
  let keyblock = aes128_ctr_keyblock key nonce ctr in
  let last_block = array_update_slice last_block 0 (array_length last) (last) in
  let last_block = xor_block last_block keyblock in
  let last = array_slice last_block 0 (array_length last) in
  array_concat_blocks blocks last
let aes128_encrypt (key: key_t) (nonce: nonce_t) (counter: uint32_t) (msg: vlbytes_t) : vlbytes_t =
  aes128_counter_mode key nonce counter msg
let aes128_decrypt (key: key_t) (nonce: nonce_t) (counter: uint32_t) (msg: vlbytes_t) : vlbytes_t =
  aes128_counter_mode key nonce counter msg

