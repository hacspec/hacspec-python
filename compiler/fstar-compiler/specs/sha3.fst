(* Generated from hacspec module ../../../specs/sha3.py *)
module Sha3
open Speclib
#reset-options "--z3rlimit 60"
let state_t: Type0 = array_t uint64_t 25

let index_t: Type0 = range_t 0 5

let max_size_t: int = op_Subtraction (pow2 130) 1

let max_size_nat: int = op_Subtraction (pow2 32) 1

let size_nat_t: Type0 = range_t 0 4294967295

let size_nat_24_t: Type0 = range_t 0 23

let size_nat_25_t: Type0 = range_t 0 24

let size_nat_200_t: Type0 = range_t 0 200

let size_nat_0_200_t: Type0 = range_t 1 201

let rotval_u64_t: Type0 = range_t 1 64

let piln_t: Type0 = range_t 1 25

let lseq_rotc_t_24_t: Type0 = array_t rotval_u64_t 24

let lseq_pilns_t_24_t: Type0 = array_t piln_t 24

let lseq_rndc_t_24_t: Type0 = array_t uint64_t 24

let lseq_uint64_5_t: Type0 = array_t uint64_t 5

let lbytes_200_t: Type0 = array_t uint8_t 200

let keccak_rotc: lseq_rotc_t_24_t =
  array_createL [
      1; 3; 6; 10; 15; 21; 28; 36; 45; 55; 2; 14; 27; 41; 56; 8; 25; 43; 62; 18; 39; 61; 20; 44
    ]

let keccak_piln: lseq_pilns_t_24_t =
  array_createL [
      10; 7; 11; 17; 18; 3; 5; 16; 8; 21; 24; 4; 15; 23; 19; 13; 12; 2; 20; 14; 22; 9; 6; 1
    ]

let keccak_rndc: lseq_rndc_t_24_t =
  array_createL [
      uint64 1; uint64 32898; uint64 9223372036854808714; uint64 9223372039002292224; uint64 32907;
      uint64 2147483649; uint64 9223372039002292353; uint64 9223372036854808585; uint64 138;
      uint64 136; uint64 2147516425; uint64 2147483658; uint64 2147516555;
      uint64 9223372036854775947; uint64 9223372036854808713; uint64 9223372036854808579;
      uint64 9223372036854808578; uint64 9223372036854775936; uint64 32778;
      uint64 9223372039002259466; uint64 9223372039002292353; uint64 9223372036854808704;
      uint64 2147483649; uint64 9223372039002292232
    ]

let readLane (s: state_t) (x: index_t) (y: index_t) : uint64_t = s.[ x +. (5 *. y) ]

let writeLane (s: state_t) (x: index_t) (y: index_t) (v: uint64_t) : state_t =
  let s = s.[ x +. (5 *. y) ] <- v in
  s

let rotl (a: uint64_t) (b: rotval_u64_t) : uint64_t = uintn_rotate_left a b

let state_theta_inner_C (s: state_t) (i: nat_t) (_C: lseq_uint64_5_t) : lseq_uint64_5_t =
  let _C =
    _C.[ i ] <-
      ((((readLane s i 0) ^. (readLane s i 1)) ^. (readLane s i 2)) ^. (readLane s i 3)) ^.
      (readLane s i 4)
  in
  _C

let state_theta0 (s: state_t) (_C: lseq_uint64_5_t) : lseq_uint64_5_t =
  let _C = repeati 5 (fun x _C -> state_theta_inner_C s x _C) _C in
  _C

let state_theta_inner_s_inner (x: index_t) (_D: uint64_t) (y: index_t) (s: state_t) : state_t =
  writeLane s x y ((readLane s x y) ^. _D)

let state_theta_inner_s (_C: lseq_uint64_5_t) (x: index_t) (s: state_t) : state_t =
  let _D = _C.[ (x +. 4) % 5 ] ^. (rotl _C.[ (x +. 1) % 5 ] 1) in
  let s = repeati 5 (fun y s -> state_theta_inner_s_inner x _D y s) s in
  s

let state_theta1 (s: state_t) (_C: lseq_uint64_5_t) : state_t =
  let s = repeati 5 (fun x s -> state_theta_inner_s _C x s) s in
  s

let state_theta (s: state_t) : state_t =
  let _C = array_create 5 (uint64 0) in
  let _C = state_theta0 s _C in
  state_theta1 s _C

let state_pi_rho_inner (t: size_nat_24_t) (current: uint64_t) (s_pi_rho: state_t)
  : (uint64_t * state_t) =
  let r = keccak_rotc.[ t ] in
  let _Y = keccak_piln.[ t ] in
  let temp = s_pi_rho.[ _Y ] in
  let s_pi_rho = s_pi_rho.[ _Y ] <- rotl current r in
  let current = temp in
  (current, s_pi_rho)

let state_pi_rho (s_theta: state_t) : state_t =
  let current = readLane s_theta 1 0 in
  let s_pi_rho = array_copy s_theta in
  let current, s_pi_rho =
    repeati 24
      (fun t (current, s_pi_rho) -> state_pi_rho_inner t current s_pi_rho)
      (current, s_pi_rho)
  in
  s_pi_rho

let state_chi_inner (s_pi_rho: state_t) (y: index_t) (x: index_t) (s: state_t) : state_t =
  let s_chi =
    writeLane s
      x
      y
      ((readLane s_pi_rho x y) ^.
        (~(readLane s_pi_rho ((x +. 1) % 5) y) &. (readLane s_pi_rho ((x +. 2) % 5) y)))
  in
  s_chi

let state_chi_inner1 (s_pi_rho: state_t) (y: index_t) (s: state_t) : state_t =
  let s_chi = array_copy s_pi_rho in
  let s_chi = repeati 5 (fun x s_chi -> state_chi_inner s_pi_rho y x s) s_chi in
  s_chi

let state_chi (s_pi_rho: state_t) : state_t =
  let saved = array_copy s_pi_rho in
  let s_chi = array_copy s_pi_rho in
  let s_chi = repeati 5 (fun y s_chi -> state_chi_inner1 s_pi_rho y saved) s_chi in
  s_chi

let state_iota (s: state_t) (r: size_nat_24_t) : state_t =
  writeLane s 0 0 ((readLane s 0 0) ^. keccak_rndc.[ r ])

let state_permute1 (s: state_t) (round: size_nat_24_t) : state_t =
  let s_theta = state_theta s in
  let s_pi_rho = state_pi_rho s_theta in
  let s_chi = state_chi s_pi_rho in
  let s_iota = state_iota s_chi round in
  s_iota

let state_permute (s: state_t) : state_t =
  let s = repeati 24 (fun i s -> state_permute1 s i) s in
  s

let loadState_inner (block: lbytes_200_t) (j: size_nat_25_t) (s: state_t) : state_t =
  let nj = bytes_to_uint64_le (array_slice block (j *. 8) ((j *. 8) +. 8)) in
  let s = s.[ j ] <- s.[ j ] ^. nj in
  s

let loadState (rateInBytes: size_nat_200_t) (input_b: vlbytes_t) (s: state_t) : state_t =
  let block = array_create 200 (uint8 0) in
  let block = array_update_slice block 0 rateInBytes (input_b) in
  let s = repeati 25 (fun j s -> loadState_inner block j s) s in
  s

let storeState_inner (s: state_t) (j: size_nat_25_t) (block: lbytes_200_t) : lbytes_200_t =
  let block = array_update_slice block (j *. 8) ((j *. 8) +. 8) (bytes_from_uint64_le s.[ j ]) in
  block

let storeState (rateInBytes: size_nat_200_t) (s: state_t) : lbytes_200_t =
  let block = bytes (array_create 200 (uint8 0)) in
  let block = repeati 25 (fun j block -> storeState_inner s j block) block in
  array_slice block 0 rateInBytes

let absorb_next (s: state_t) (rateInBytes: size_nat_0_200_t) : state_t =
  let nextBlock = array_create rateInBytes (uint8 0) in
  let nextBlock = nextBlock.[ rateInBytes -. 1 ] <- uint8 128 in
  let s = loadState rateInBytes nextBlock s in
  let s = state_permute s in
  s

let absorb_last
  (delimitedSuffix: uint8_t) (rateInBytes: size_nat_0_200_t) (rem: nat_t) (input_b: lbytes_200_t)
  (inputByteLen: size_nat_t) (s: state_t)
  : state_t =
  let last = array_slice input_b (inputByteLen -. rem) inputByteLen in
  let lastBlock = array_create rateInBytes (uint8 0) in
  let lastBlock = array_update_slice lastBlock 0 rem (last) in
  let lastBlock = lastBlock.[ rem ] <- delimitedSuffix in
  let s = loadState rateInBytes lastBlock s in
  let s =
    if (not (delimitedSuffix &. (uint8 128)) = (uint8 0)) && rem = (rateInBytes -. 1)
    then state_permute s
    else s
  in
  let s = absorb_next s rateInBytes in
  s

let absorb_inner (rateInBytes: size_nat_0_200_t) (block: lbytes_200_t) (s: state_t) (i: nat_t)
  : state_t =
  let s =
    loadState rateInBytes
      (array_slice block (i *. rateInBytes) ((i *. rateInBytes) +. rateInBytes))
      s
  in
  let s = state_permute s in
  s

let absorb
  (s: state_t) (rateInBytes: size_nat_0_200_t) (inputByteLen: size_nat_t) (input_b: vlbytes_t)
  (delimitedSuffix: uint8_t)
  : state_t =
  let n = inputByteLen /. rateInBytes in
  let rem = inputByteLen % rateInBytes in
  let s = repeati n (fun i s -> absorb_inner rateInBytes input_b s i) s in
  let s = absorb_last delimitedSuffix rateInBytes rem input_b inputByteLen s in
  s

let squeeze_inner
  (rateInBytes: size_nat_0_200_t) (outputByteLen: size_nat_t) (i: nat_t) (s: state_t)
  : (lbytes_200_t * state_t) =
  let block = storeState rateInBytes s in
  let s = state_permute s in
  (block, s)

let squeeze (s: state_t) (rateInBytes: size_nat_0_200_t) (outputByteLen: size_nat_t) : vlbytes_t =
  let output = array_create outputByteLen (uint8 0) in
  let outBlocks = outputByteLen /. rateInBytes in
  let block = array_create 200 (uint8 0) in
  let block, output, s =
    repeati outBlocks
      (fun i (block, output, s) ->
          let block, s = squeeze_inner rateInBytes outputByteLen i s in
          let output =
            array_update_slice output (i *. rateInBytes) ((i *. rateInBytes) +. rateInBytes) (block)
          in
          (block, output, s))
      (block, output, s)
  in
  let remOut = outputByteLen % rateInBytes in
  let outBlock = storeState remOut s in
  let output = array_update_slice output (outputByteLen -. remOut) outputByteLen (outBlock) in
  output

let keccak
  (rate: size_nat_t) (capacity: size_nat_t) (inputByteLen: size_nat_t) (input_b: vlbytes_t)
  (delimitedSuffix: uint8_t) (outputByteLen: size_nat_t)
  : vlbytes_t =
  let rateInBytes = rate /. 8 in
  let s = array_create 25 (uint64 0) in
  let s = absorb s rateInBytes inputByteLen input_b delimitedSuffix in
  let output = squeeze s rateInBytes outputByteLen in
  output

let shake128 (inputByteLen: size_nat_t) (input_b: vlbytes_t) (outputByteLen: size_nat_t) : vlbytes_t =
  keccak 1344 256 inputByteLen input_b (uint8 31) outputByteLen

let shake256 (inputByteLen: size_nat_t) (input_b: vlbytes_t) (outputByteLen: size_nat_t) : vlbytes_t =
  keccak 1088 512 inputByteLen input_b (uint8 31) outputByteLen

let sha3_224 (inputByteLen: size_nat_t) (input_b: vlbytes_t) : vlbytes_t =
  keccak 1152 448 inputByteLen input_b (uint8 6) 28

let sha3_256 (inputByteLen: size_nat_t) (input_b: vlbytes_t) : vlbytes_t =
  keccak 1088 512 inputByteLen input_b (uint8 6) 32

let sha3_384 (inputByteLen: size_nat_t) (input_b: vlbytes_t) : vlbytes_t =
  keccak 832 768 inputByteLen input_b (uint8 6) 48

let sha3_512 (inputByteLen: size_nat_t) (input_b: vlbytes_t) : vlbytes_t =
  keccak 576 1024 inputByteLen input_b (uint8 6) 64

