(* Generated from hacspec module ../../../specs/curve448.py *)
module Curve448
open Speclib
let p448: int = ((2 **. 448) -. (2 **. 224)) -. 1
let felem_t: Type0 = natmod_t p448
let to_felem (x: nat_t) : felem_t = natmod x p448
let finv (x: felem_t) : felem_t = x **. (p448 -. 2)
let point_t: Type0 = (felem_t * felem_t)
let point (a: int) (b: int) : point_t = (to_felem (nat a), to_felem (nat b))
let scalar_t: Type0 = uintn_t 448
let to_scalar (n: nat_t) : scalar_t = uintn n 448
let serialized_point_t: Type0 = array_t uint8_t 56
let serialized_scalar_t: Type0 = array_t uint8_t 56
let decodeScalar (s: serialized_scalar_t) : scalar_t =
  let k = bytes_copy s in
  let k = k.[ 0 ] <- k.[ 0 ] &. uint8 252 in
  let k = k.[ 55 ] <- k.[ 55 ] |. uint8 128 in
  to_scalar (bytes_to_nat_le k)
let decodePoint (u: serialized_point_t) : point_t =
  let b = bytes_to_nat_le u in
  point ((b % (2 **. 448)) % p448) 1
let encodePoint (p: point_t) : serialized_point_t =
  let x, y = p in
  let b = natmod_to_int (x *. (finv y)) in
  bytes_from_nat_le b 56
let point_add_and_double (q: point_t) (nq: point_t) (nqp1: point_t) : (point_t * point_t) =
  let x_1, z_1 = q in
  let x_2, z_2 = nq in
  let x_3, z_3 = nqp1 in
  let a = x_2 +. z_2 in
  let aa = a **. 2 in
  let b = x_2 -. z_2 in
  let bb = b **. 2 in
  let e = aa -. bb in
  let c = x_3 +. z_3 in
  let d = x_3 -. z_3 in
  let da = d *. a in
  let cb = c *. b in
  let x_3 = (da +. cb) **. 2 in
  let z_3 = x_1 *. ((da -. cb) **. 2) in
  let x_2 = aa *. bb in
  let z_2 = e *. (aa +. ((to_felem 39081) *. e)) in
  ((x_2, z_2), (x_3, z_3))
let montgomery_ladder (k: scalar_t) (init: point_t) : point_t =
  let p0 = point 1 0 in
  let p1 = init in
  let p0, p1 =
    repeati 448
      (fun i (p0, p1) ->
          if (uintn_get_bit k (447 -. i)) = (bit 1)
          then
            let p1, p0 = point_add_and_double init p1 p0 in
            (p0, p1)
          else point_add_and_double init p0 p1)
      (p0, p1)
  in
  p0
let scalarmult (s: serialized_scalar_t) (p: serialized_point_t) : serialized_point_t =
  let s_ = decodeScalar s in
  let p_ = decodePoint p in
  let r = montgomery_ladder s_ p_ in
  encodePoint r

