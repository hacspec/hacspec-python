module Chacha20
open Speclib
let blocksize = 0x40 
let index = int 
let shiftval = int 
let state = array uint32 
let key_t = array uint8 
let nonce_t = array uint8 
let bytes_t = array uint8 
let line a b d s m =
  let m = copy m in 
  let m = m.[a] <- (m.[a] + m.[b]) in 
  let m = m.[d] <- uint32.rotate_left (m.[d] ^ m.[a]) s in 
  m 
let quarter_round a b c d m =
  let m = line a b d 0x10 m in 
  let m = line c d b 0xc m in 
  let m = line a b d 0x8 m in 
  let m = line c d b 0x7 m in 
  m 
let double_round m =
  let m = quarter_round 0x0 0x4 0x8 0xc m in 
  let m = quarter_round 0x1 0x5 0x9 0xd m in 
  let m = quarter_round 0x2 0x6 0xa 0xe m in 
  let m = quarter_round 0x3 0x7 0xb 0xf m in 
  let m = quarter_round 0x0 0x5 0xa 0xf m in 
  let m = quarter_round 0x1 0x6 0xb 0xc m in 
  let m = quarter_round 0x2 0x7 0x8 0xd m in 
  let m = quarter_round 0x3 0x4 0x9 0xe m in 
  m 
let constants = array [ uint32 0x61707865, uint32 0x3320646e, uint32 0x79622d32, uint32 0x6b206574 ] 
let chacha20_init k counter nonce =
  let st = create uint32 0x0 0x10 in 
  let st = update_slice st 0x0 0x4 constants in 
  let st = update_slice st 0x4 0xc bytes.to_uint32s_le k in 
  let st = st.[0xc] <- counter in 
  let st = update_slice st 0xd 0x10 bytes.to_uint32s_le nonce in 
  st 
let chacha20_core st =
  let working_state = copy st in 
  let working_state = repeati (range 0xa) (fun x working_state -> let working_state = double_round working_state in  working_state) working_state in 
  let working_state = repeati (range 0x10) (fun i working_state -> let working_state = working_state.[i] <- working_state.[i] + st.[i] in  working_state) working_state in 
  working_state 
let chacha20 k counter nonce =
  chacha20_core chacha20_init k counter nonce 
let chacha20_block k counter nonce =
  let st = chacha20 k uint32 counter nonce in 
  let block = bytes.from_uint32s_le st in 
  block 
let xor_block block keyblock =
  let out = array list block in 
  let out = repeati (range len out) (fun i out -> let out = out.[i] <- out.[i] ^ keyblock.[i] in  out) out in 
  out 
let chacha20_counter_mode key counter nonce msg =
  let blocks = split_blocks msg blocksize in 
  let keyblock = create uint8 0x0 blocksize in 
  let (keyblock,'blocks') = repeati (range 0x0 len blocks) (fun i (keyblock,'blocks') -> let keyblock = chacha20_block key (counter + i) nonce in 
let blocks = blocks.[i] <- xor_block blocks.[i] keyblock in  (keyblock,'blocks')) (keyblock,'blocks') in 
  concat_blocks blocks 
let chacha20_encrypt key counter nonce msg =
  chacha20_counter_mode key counter nonce msg 
let chacha20_decrypt key counter nonce msg =
  chacha20_counter_mode key counter nonce msg 
