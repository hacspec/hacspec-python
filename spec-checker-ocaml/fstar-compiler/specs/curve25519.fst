(* Generated from hacspec module ../../../specs/curve25519.py *)
module Curve25519
open Speclib
let p25519: nat_t = (2 **. 255) -. 19
let felem_t: Type0 = natmod_t p25519
let to_felem (x: nat_t) : felem_t = natmod x p25519
let zero: felem_t = to_felem 0
let one: felem_t = to_felem 1
let finv (x: felem_t) : felem_t = x **. (p25519 -. 2)
let point_t: Type0 = (felem_t * felem_t)
let scalar_t: Type0 = uintn_t 256
let to_scalar (i: nat_t) : uintn_t 256 = uintn i 256
let serialized_point_t: Type0 = array_t uint8_t 32
let serialized_scalar_t: Type0 = array_t uint8_t 32
let g25519: point_t = (to_felem 1, to_felem 9)
let point (a: nat_t) (b: nat_t) : point_t = (to_felem a, to_felem b)
let decodeScalar (s: serialized_scalar_t) : scalar_t =
  let k = bytes_copy s in
  let k = k.[ 0 ] <- k.[ 0 ] &. uint8 248 in
  let k = k.[ 31 ] <- k.[ 31 ] &. uint8 127 in
  let k = k.[ 31 ] <- k.[ 31 ] |. uint8 64 in
  to_scalar (bytes_to_nat_le k)
let decodePoint (u: serialized_point_t) : point_t =
  let b = bytes_to_nat_le u in
  point ((b % (2 **. 255)) % p25519) 1
let encodePoint (p: point_t) : serialized_point_t =
  let y, x = p in
  let b = natmod_to_int (x *. (finv y)) in
  bytes_from_nat_le b 32
let point_add_and_double (q: point_t) (nq: point_t) (nqp1: point_t) : (point_t * point_t) =
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
let montgomery_ladder (k: scalar_t) (init: point_t) : point_t =
  let p0 = point 1 0 in
  let p1 = init in
  let p0, p1 =
    repeati 256
      (fun i (p0, p1) ->
          if (uintn_get_bit k (255 -. i)) = (bit 1)
          then point_add_and_double init p1 p0
          else
            let p1, p0 = point_add_and_double init p0 p1 in
            (p0, p1))
      (p0, p1)
  in
  p0
let scalarmult (s: serialized_scalar_t) (p: serialized_point_t) : serialized_point_t =
  let s_ = decodeScalar s in
  let p_ = decodePoint p in
  let r = montgomery_ladder s_ p_ in
  encodePoint r
let is_on_curve (s: serialized_point_t) : bool =
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
  let res = true in
  let res =
    repeati (array_length disallowed) (fun i res -> if n = disallowed.[ i ] then false else res) res
  in
  res
let private_to_public (s: serialized_scalar_t) : serialized_point_t =
  scalarmult s (encodePoint g25519)
let ecdh_shared_secret (priv: serialized_scalar_t) (pub: serialized_point_t)
  : result_t serialized_point_t =
  let res =
    if is_on_curve pub
    then result_retval (scalarmult priv pub)
    else result_error "public key is not on curve"
  in
  res

