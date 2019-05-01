(* Generated from hacspec module ../../../specs/sha256.py *)

module Sha256
open Speclib
#reset-options "--z3rlimit 60"
let i_range_t:Type0 = range_t 0 4
let op_range_t:Type0 = range_t 0 1
let blockSize:int = 64
let block_t:Type0 = array_t uint8_t 64
let lenSize:int = 8
let len_t:Type0 = uint64_t
let word_t:Type0 = uint32_t
let kSize:int = 64
let k_t:Type0 = array_t word_t 64
let opTableType_t:Type0 = array_t int 12
let opTable:opTableType_t = array (array_createL [2; 13; 22; 6; 11; 25; 7; 18; 3; 17; 19; 10])
let kTable:k_t =
  array (array_createL [
          uint32 1116352408; uint32 1899447441; uint32 3049323471; uint32 3921009573;
          uint32 961987163; uint32 1508970993; uint32 2453635748; uint32 2870763221;
          uint32 3624381080; uint32 310598401; uint32 607225278; uint32 1426881987;
          uint32 1925078388; uint32 2162078206; uint32 2614888103; uint32 3248222580;
          uint32 3835390401; uint32 4022224774; uint32 264347078; uint32 604807628; uint32 770255983;
          uint32 1249150122; uint32 1555081692; uint32 1996064986; uint32 2554220882;
          uint32 2821834349; uint32 2952996808; uint32 3210313671; uint32 3336571891;
          uint32 3584528711; uint32 113926993; uint32 338241895; uint32 666307205; uint32 773529912;
          uint32 1294757372; uint32 1396182291; uint32 1695183700; uint32 1986661051;
          uint32 2177026350; uint32 2456956037; uint32 2730485921; uint32 2820302411;
          uint32 3259730800; uint32 3345764771; uint32 3516065817; uint32 3600352804;
          uint32 4094571909; uint32 275423344; uint32 430227734; uint32 506948616; uint32 659060556;
          uint32 883997877; uint32 958139571; uint32 1322822218; uint32 1537002063;
          uint32 1747873779; uint32 1955562222; uint32 2024104815; uint32 2227730452;
          uint32 2361852424; uint32 2428436474; uint32 2756734187; uint32 3204031479;
          uint32 3329325298
        ])
let hashSize:int = 32
let hash_t:Type0 = array_t word_t 8
let digest_t:Type0 = array_t uint8_t 32
let h0:hash_t =
  array (array_createL [
          uint32 1779033703;
          uint32 3144134277;
          uint32 1013904242;
          uint32 2773480762;
          uint32 1359893119;
          uint32 2600822924;
          uint32 528734635;
          uint32 1541459225
        ])
let ch (x y z: word_t) : word_t = (x &. y) ^. ((~x) &. z)
let maj (x y z: word_t) : word_t = (x &. y) ^. ((x &. z) ^. (y &. z))
let sigma (x: word_t) (i: i_range_t) (op: op_range_t) : word_t =
  let tmp =
    if op = 0
    then x >>. opTable.[ (3 *. i) +. 2 ]
    else uintn_rotate_right x opTable.[ (3 *. i) +. 2 ]
  in
  ((uintn_rotate_right x opTable.[ 3 *. i ]) ^. (uintn_rotate_right x opTable.[ (3 *. i) +. 1 ])) ^.
  tmp
let schedule (block: block_t) : k_t =
  let b = bytes_to_uint32s_be block in
  let s = array_create 64 (uint32 0) in
  let t16 = uint32 0 in
  let t15 = uint32 0 in
  let t7 = uint32 0 in
  let t2 = uint32 0 in
  let t1 = uint32 0 in
  let s1 = uint32 0 in
  let s0 = uint32 0 in
  let s, s0, s1, t15, t16, t2, t7 =
    repeati kSize
      (fun i (s, s0, s1, t15, t16, t2, t7) ->
          if i <. 16
          then
            let s = s.[ i ] <- b.[ i ] in
            (s, s0, s1, t15, t16, t2, t7)
          else
            let t16 = s.[ i -. 16 ] in
            let t15 = s.[ i -. 15 ] in
            let t7 = s.[ i -. 7 ] in
            let t2 = s.[ i -. 2 ] in
            let s1 = sigma t2 3 0 in
            let s0 = sigma t15 2 0 in
            let s = s.[ i ] <- ((s1 +. t7) +. s0) +. t16 in
            (s, s0, s1, t15, t16, t2, t7))
      (s, s0, s1, t15, t16, t2, t7)
  in
  s
let shuffle (ws: k_t) (hashi: hash_t) : hash_t =
  let h = array_copy hashi in
  let a0 = h.[ 0 ] in
  let b0 = h.[ 1 ] in
  let c0 = h.[ 2 ] in
  let d0 = h.[ 3 ] in
  let e0 = h.[ 4 ] in
  let f0 = h.[ 5 ] in
  let g0 = h.[ 6 ] in
  let h0 = h.[ 7 ] in
  let t1 = uint32 0 in
  let t2 = uint32 0 in
  let a0, b0, c0, d0, e0, f0, g0, h, h0, t1, t2 =
    repeati kSize
      (fun i (a0, b0, c0, d0, e0, f0, g0, h, h0, t1, t2) ->
          let a0 = h.[ 0 ] in
          let b0 = h.[ 1 ] in
          let c0 = h.[ 2 ] in
          let d0 = h.[ 3 ] in
          let e0 = h.[ 4 ] in
          let f0 = h.[ 5 ] in
          let g0 = h.[ 6 ] in
          let h0 = h.[ 7 ] in
          let t1 = (((h0 +. (sigma e0 1 1)) +. (ch e0 f0 g0)) +. kTable.[ i ]) +. ws.[ i ] in
          let t2 = (sigma a0 0 1) +. (maj a0 b0 c0) in
          let h = h.[ 0 ] <- t1 +. t2 in
          let h = h.[ 1 ] <- a0 in
          let h = h.[ 2 ] <- b0 in
          let h = h.[ 3 ] <- c0 in
          let h = h.[ 4 ] <- d0 +. t1 in
          let h = h.[ 5 ] <- e0 in
          let h = h.[ 6 ] <- f0 in
          let h = h.[ 7 ] <- g0 in
          (a0, b0, c0, d0, e0, f0, g0, h, h0, t1, t2))
      (a0, b0, c0, d0, e0, f0, g0, h, h0, t1, t2)
  in
  h
let compress (block: block_t) (hIn: hash_t) : hash_t =
  let s = schedule block in
  let h = shuffle s hIn in
  let h = repeati 8 (fun i h -> h.[ i ] <- h.[ i ] +. hIn.[ i ]) h in
  h
let truncate (b: array_t uint8_t 256) : digest_t =
  let result = array_create hashSize (uint8 0) in
  let result = repeati hashSize (fun i result -> result.[ i ] <- b.[ i ]) result in
  digest_t result
let sha256 (msg: vlbytes_t) : digest_t =
  let blocks, last = array_split_blocks msg blockSize in
  let nblocks = array_length blocks in
  let h = h0 in
  let h = repeati nblocks (fun i h -> compress blocks.[ i ] h) h in
  let last_len = array_length last in
  let len_bits = (array_length msg) *. 8 in
  let pad = array_create (2 *. blockSize) (uint8 0) in
  let pad = array_update_slice pad 0 last_len (last) in
  let pad = pad.[ last_len ] <- uint8 128 in
  let h, pad =
    if last_len <. (blockSize -. lenSize)
    then
      let pad =
        array_update_slice pad
          (blockSize -. lenSize)
          blockSize
          (bytes_from_uint64s_be (uint64 len_bits))
      in
      let h = compress (array_slice pad 0 blockSize) h in
      (h, pad)
    else
      let pad =
        array_update_slice pad
          ((2 *. blockSize) -. lenSize)
          (2 *. blockSize)
          (bytes_from_uint64s_be (uint64 len_bits))
      in
      let h = compress (array_slice pad 0 blockSize) h in
      let h = compress (array_slice pad blockSize (2 *. blockSize)) h in
      (h, pad)
  in
  let result = bytes_from_uint32s_be h in
  truncate result

