module Curve25519
#set-options "--z3rlimit 20 --max_fuel 0"
open Spec.Lib.IntTypes
open Spec.Lib.RawIntTypes
open Spec.Lib.IntSeq
open Speclib
let p25519 = ((0x2 **. 0xff) -. 0x13) 
type felem_t = x:nat{(x < p25519)}

let felem (x:nat) : felem_t =
  (x %. p25519) 
let fadd (x:felem_t) (y:felem_t) : felem_t =
  felem (x +. y) 
let fsub (x:felem_t) (y:felem_t) : felem_t =
  felem (x -. y) 
let fmul (x:felem_t) (y:felem_t) : felem_t =
  felem (x *. y) 
let fsqr (x:felem_t) : felem_t =
  felem (x *. x) 
let fexp (x:felem_t) (n:nat) : felem_t =
  felem (pow x nat p25519) 
let finv (x:felem_t) : felem_t =
  felem (pow x (p25519 -. 0x2) p25519) 
let point_t = tuple2 felem_t felem_t 
let scalar_t = bitvector_t 0x100 
let g25519 : point_t = Tuple(elts=0x9
                       0x1,
                       ctx=Load()) 
let serialized_point_t = bytes_t 0x20 
let serialized_scalar_t = bytes_t 0x20 
let decodeScalar (s:serialized_scalar_t) : scalar_t =
  let k = vlcopy s in 
  let k = k.[0x0] <- k.[0x0] &. u8 0xf8 in 
  let k = k.[0x1f] <- k.[0x1f] &. u8 0x7f in 
  let k = k.[0x1f] <- k.[0x1f] |. u8 0x40 in 
  bitvector (bytes.to_nat_le k) 0x100 
let decodePoint (u:serialized_point_t) : point_t =
  let b = bytes.to_nat_le u in 
  Tuple(elts=((b &. ((0x1 <<. 0xff) -. 0x1)) %. p25519)
  0x1,
  ctx=Load()) 
let encodePoint (p:point_t) : serialized_point_t =
  let b = fmul p.[0x0] (finv p.[0x1]) in 
  bytes.from_nat_le b 
let point_add_and_double (q:point_t) (nq:point_t) (nqp1:point_t) : tuple2 point_t point_t =
  let (x_1,_) = q in 
  let (x_2,z_2) = nq in 
  let (x_3,z_3) = nqp1 in 
  let a = fadd x_2 z_2 in 
  let aa = fsqr a in 
  let b = fsub x_2 z_2 in 
  let bb = fsqr b in 
  let e = fsub aa bb in 
  let c = fadd x_3 z_3 in 
  let d = fsub x_3 z_3 in 
  let da = fmul d a in 
  let cb = fmul c b in 
  let x_3 = fsqr (fadd da cb) in 
  let z_3 = fmul x_1 (fsqr (fsub da cb)) in 
  let x_2 = fmul aa bb in 
  let z_2 = fmul e (fadd aa (fmul (felem 0x1db41) e)) in 
  Tuple(elts=Tuple(elts=x_2
  z_2,
  ctx=Load())
  Tuple(elts=x_3
  z_3,
  ctx=Load()),
  ctx=Load()) 
let montgomery_ladder (k:scalar_t) (init:point_t) : point_t =
  let p0 : point_t = Tuple(elts=0x1
                     0x0,
                     ctx=Load()) in 
  let p1 : point_t = init in 
  let () = repeati (range 0x100)
    (fun i () ->
      let () = if ((k.[(0xff -. i)] = bit 0x1)) then (let (p1,p0) = point_add_and_double init p1 p0 in () )else (let (p0,p1) = point_add_and_double init p0 p1 in ()) in 
      ())
    () in 
  p0 
let scalarmult (s:serialized_scalar_t) (p:serialized_point_t) : serialized_point_t =
  let s_ = decodeScalar s in 
  let p_ = decodePoint p in 
  let r = montgomery_ladder s_ p_ in 
  encodePoint r 
let is_on_curve (s:serialized_point_t) : bool =
  true 
let private_to_public (s:serialized_scalar_t) : serialized_point_t =
  scalarmult s g25519 
let ecdh_shared_secret (private:serialized_scalar_t) (public:serialized_point_t) : serialized_point_t =
  let () = if (is_on_curve public) then (scalarmult private public() )else (fail "public key is not on curve";()) in  
