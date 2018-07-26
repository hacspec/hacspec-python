(* Generated from hacspec module ../specs/curve25519.py *)
module Curve25519
open Speclib
let p25519: nat = (2 **. 255) -. 19
let felem_t: Type0 = natmod_t p25519
let to_felem (x: nat) : natmod_t p25519 = natmod x p25519
let zero: natmod_t p25519 = to_felem 0
let one: natmod_t p25519 = to_felem 1
let finv (x: natmod_t p25519) : natmod_t p25519 = x **. (p25519 -. 2)
let point_t: Type0 = (natmod_t p25519 * natmod_t p25519)
let scalar_t: Type0 = uintn_t 256
let to_scalar (i: nat) : uintn_t 256 = uintn i 256
let serialized_point_t: Type0 = array_t uint8_t 32
let serialized_scalar_t: Type0 = array_t uint8_t 32
let g25519: (natmod_t p25519 * natmod_t p25519) = (natmod 1 p25519, natmod 9 p25519)
let point (a: nat) (b: nat) : (natmod_t p25519 * natmod_t p25519) = (to_felem a, to_felem b)
let decodeScalar (s: array_t uint8_t 32) : uintn_t 256 =
  let k = bytes_copy s in
  let k = k.[ 0 ] <- (k.[ 0 ] &. (uint8 248)) in
  let k = k.[ 31 ] <- (k.[ 31 ] &. (uint8 127)) in
  let k = k.[ 31 ] <- (k.[ 31 ] |. (uint8 64)) in
  to_scalar (bytes_to_nat_le k)
let decodePoint (u: array_t uint8_t 32) : (natmod_t p25519 * natmod_t p25519) =
  let b = bytes_to_nat_le u in
  point ((b % (2 **. 255)) % p25519) 1
let encodePoint (p: (natmod_t p25519 * natmod_t p25519)) : array_t uint8_t 32 =
  let y, x = p in
  let b = natmod_to_int (x *. (finv y)) in
  bytes_from_nat_le b 32
let point_add_and_double
  (q: (natmod_t p25519 * natmod_t p25519)) (nq: (natmod_t p25519 * natmod_t p25519))
  (nqp1: (natmod_t p25519 * natmod_t p25519))
  : ((natmod_t p25519 * natmod_t p25519) * (natmod_t p25519 * natmod_t p25519)) =
  let z_1, x_1 = q in
  let z_2, x_2 = nq in
  let z_3, x_3 = nqp1 in
  let a = x_2 +. z_2 in
  let aa = a **. 2 in
  let b = x_2 -. z_2 in
  let bb = b *. b in
  let e = aa -. bb in
  let c = x_3 +. z_3 in
  let d = x_3 -. z_3 in
  let da = d *. a in
  let cb = c *. b in
  let x_3 = (da +. cb) **. 2 in
  let z_3 = x_1 *. ((da -. cb) **. 2) in
  let x_2 = aa *. bb in
  let z_2 = e *. (aa +. ((to_felem 121665) *. e)) in
  ((z_3, x_3), (z_2, x_2))
let montgomery_ladder (k: uintn_t 256) (init: (natmod_t p25519 * natmod_t p25519))
  : (natmod_t p25519 * natmod_t p25519) =
  let p0 = point 1 0 in
  let p1 = init in
  let p0, p1 =
    repeati 256
      (fun i (p0, p1) ->
          let p0, p1 =
            if (uintn_get_bit k (255 -. i)) =. (bit 1)
            then
              (let p0, p1 = point_add_and_double init p1 p0 in
                (p0, p1))
            else
              let p1, p0 = point_add_and_double init p0 p1 in
              (p0, p1)
          in
          (p0, p1))
      (p0, p1)
  in
  p0
let scalarmult (s: array_t uint8_t 32) (p: array_t uint8_t 32) : array_t uint8_t 32 =
  let s_ = decodeScalar s in
  let p_ = decodePoint p in
  let r = montgomery_ladder s_ p_ in
  encodePoint r
let is_on_curve (s: array_t uint8_t 32) : bool =
  let n = bytes_to_nat_le s in
  let disallowed =
    array (array_createL [
            0; 1; 325606250916557431795983626356110631294008115727848805560023387167927233504;
            39382357235489614581723060781553021112529911719440698176882885853963445705823;
            ((2 **. 255) -. 19) -. 1; (2 **. 255) -. 19; ((2 **. 255) -. 19) +. 1;
            ((2 **. 255) -. 19) +.
            325606250916557431795983626356110631294008115727848805560023387167927233504;
            ((2 **. 255) -. 19) +.
            39382357235489614581723060781553021112529911719440698176882885853963445705823;
            (2 *. ((2 **. 255) -. 19)) -. 1; 2 *. ((2 **. 255) -. 19);
            (2 *. ((2 **. 255) -. 19)) +. 1
          ])
  in
  assert (array_length disallowed == 12);
  let res = true in
  let res =
    repeati (array_length disallowed)
      (fun i res ->
          let res =
            if n = disallowed.[ i ]
            then
              (let res = false in
                res)
            else res
          in
          res)
      res
  in
  res
let private_to_public (s: array_t uint8_t 32) : array_t uint8_t 32 =
  scalarmult s (encodePoint g25519)
let ecdh_shared_secret (priv: array_t uint8_t 32) (pub: array_t uint8_t 32)
  : result_t (array_t uint8_t 32) =
  let res =
    if is_on_curve pub
    then
      (let res = result_retval (scalarmult priv pub) in
        res)
    else
      let res = result_error "public key is not on curve" in
      res
  in
  res

