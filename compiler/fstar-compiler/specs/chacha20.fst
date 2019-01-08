(* Generated from hacspec module ../../../specs/chacha20.py *)
module Chacha20
open Speclib
#reset-options "--z3rlimit 60"
let blocksize: nat_t = 64

let index_t: Type0 = range_t 0 16

let rotval_t: Type0 = range_t 1 32

let state_t: Type0 = array_t uint32_t 16

let key_t: Type0 = array_t uint8_t 32

let nonce_t: Type0 = array_t uint8_t 12

let block_t: Type0 = array_t uint8_t 64

let subblock_t: Type0 = (x: vlbytes_t{(array_length x) <=. blocksize})

let constants_t: Type0 = array_t uint32_t 4

let line (a: index_t) (b: index_t) (d: index_t) (s: rotval_t) (m: state_t) : state_t =
  let m = array_copy m in
  let m = m.[ a ] <- m.[ a ] +. m.[ b ] in
  let m = m.[ d ] <- m.[ d ] ^. m.[ a ] in
  let m = m.[ d ] <- uintn_rotate_left m.[ d ] s in
  m

let quarter_round (a: index_t) (b: index_t) (c: index_t) (d: index_t) (m: state_t) : state_t =
  let m = line a b d 16 m in
  let m = line c d b 12 m in
  let m = line a b d 8 m in
  let m = line c d b 7 m in
  m

let column_round (m: state_t) : state_t =
  let m = quarter_round 0 4 8 12 m in
  let m = quarter_round 1 5 9 13 m in
  let m = quarter_round 2 6 10 14 m in
  let m = quarter_round 3 7 11 15 m in
  m

let diagonal_round (m: state_t) : state_t =
  let m = quarter_round 0 5 10 15 m in
  let m = quarter_round 1 6 11 12 m in
  let m = quarter_round 2 7 8 13 m in
  let m = quarter_round 3 4 9 14 m in
  m

let double_round (m: state_t) : state_t =
  let m = column_round m in
  let m = diagonal_round m in
  m

let chacha20_core (st: state_t) : state_t =
  let working_state = array_copy st in
  let working_state =
    repeati 10 (fun x working_state -> double_round working_state) working_state
  in
  let working_state =
    repeati 16
      (fun i working_state -> working_state.[ i ] <- working_state.[ i ] +. st.[ i ])
      working_state
  in
  working_state

let c0: uint32_t = uint32 1634760805

let c1: uint32_t = uint32 857760878

let c2: uint32_t = uint32 2036477234

let c3: uint32_t = uint32 1797285236

let chacha20_set_counter (st: state_t) (c: uint32_t) : state_t =
  let st = st.[ 12 ] <- c in
  st

let setup (k: key_t) (nonce: nonce_t) (st: state_t) : state_t =
  let st = st.[ 0 ] <- c0 in
  let st = st.[ 1 ] <- c1 in
  let st = st.[ 2 ] <- c2 in
  let st = st.[ 3 ] <- c3 in
  let st = array_update_slice st 4 12 (bytes_to_uint32s_le k) in
  let st = array_update_slice st 13 16 (bytes_to_uint32s_le nonce) in
  st

let chacha20_init (k: key_t) (nonce: nonce_t) : state_t =
  let st = array_create 16 (uint32 0) in
  let st = setup k nonce st in
  st

let chacha20 (k: key_t) (counter: uint32_t) (nonce: nonce_t) : state_t =
  let st = chacha20_init k nonce in
  let st = chacha20_set_counter st counter in
  chacha20_core st

let chacha20_key_block (st: state_t) : block_t =
  let st = chacha20_core st in
  let block = bytes_from_uint32s_le st in
  block

let chacha20_key_block0 (k: key_t) (counter: uint32_t) (nonce: nonce_t) : block_t =
  let st = chacha20_init k nonce in
  let st = chacha20_set_counter st counter in
  let block = chacha20_key_block st in
  block

let xor_block (block: block_t) (keyblock: block_t) : block_t =
  let out = bytes_copy block in
  let out = repeati blocksize (fun i out -> out.[ i ] <- out.[ i ] ^. keyblock.[ i ]) out in
  out

let chacha_encrypt_block (st0: state_t) (c: uint32_t) (b: block_t) : block_t =
  let st = chacha20_set_counter st0 c in
  let kb = chacha20_key_block st in
  xor_block b kb

let chacha_encrypt_last (key: key_t) (ctr: uint32_t) (nonce: nonce_t) (last: subblock_t) : vlbytes_t =
  let keyblock = array_create blocksize (uint8 0) in
  let last_block = array_create blocksize (uint8 0) in
  let keyblock = chacha20_key_block0 key ctr nonce in
  let last_block = array_update_slice last_block 0 (array_length last) (last) in
  let last_block = xor_block last_block keyblock in
  let last = array_slice last_block 0 (array_length last) in
  last

let chacha20_counter_mode (key: key_t) (counter: uint32_t) (nonce: nonce_t) (msg: vlbytes_t)
  : vlbytes_t =
  let blocks, last = array_split_blocks msg blocksize in
  let keyblock = array_create blocksize (uint8 0) in
  let last_block = array_create blocksize (uint8 0) in
  let ctr = counter in
  let st = chacha20_init key nonce in
  let blocks, ctr =
    repeati (array_length blocks)
      (fun i (blocks, ctr) ->
          let blocks = blocks.[ i ] <- chacha_encrypt_block st ctr blocks.[ i ] in
          let ctr = ctr +. counter in
          (blocks, ctr))
      (blocks, ctr)
  in
  let keyblock = chacha20_key_block0 key ctr nonce in
  let last_block = array_update_slice last_block 0 (array_length last) (last) in
  let last_block = xor_block last_block keyblock in
  let last = array_slice last_block 0 (array_length last) in
  array_concat_blocks blocks last

let chacha20_encrypt_bytes (key: key_t) (counter: uint32_t) (nonce: nonce_t) (msg: vlbytes_t)
  : vlbytes_t = chacha20_counter_mode key counter nonce msg

let chacha20_decrypt (key: key_t) (counter: uint32_t) (nonce: nonce_t) (msg: vlbytes_t) : vlbytes_t =
  chacha20_counter_mode key counter nonce msg

