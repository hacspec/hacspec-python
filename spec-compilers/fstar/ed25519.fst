module Ed25519
#set-options "--z3rlimit 20 --max_fuel 0"
open Spec.Lib.IntTypes
open Spec.Lib.RawIntTypes
open Spec.Lib.IntSeq
open Speclib
open Curve25519
open Sha2
let d25519 : felem_t = felem 0x52036cee2b6ffe738cc740797779e89800700a4d4141d8ab75eb4dca135978a3 
let q25519 : felem_t = felem ((0x1 <<. 0xfc) +. 0x14def9dea2f79cd65812631a5cf5d3ed) 
let sha512_modq (s:vlbytes) : felem_t =
  let h = sha512 s in 
  felem ((bytes.to_nat_le h) %. q25519) 
let affine_point_t = tuple2 felem_t felem_t 
let extended_point_t = tuple4 felem_t felem_t felem_t felem_t 
let point_add (p:extended_point_t) (q:extended_point_t) : extended_point_t =
  let () = if ((p = Tuple(elts=0x0
    0x1
    0x1
    0x0,
    ctx=Load()))) then (q() )else (()) in 
  let () = if ((q = Tuple(elts=0x0
    0x1
    0x1
    0x0,
    ctx=Load()))) then (p() )else (()) in 
  let (x1,y1,z1,t1) = p in 
  let (x2,y2,z2,t2) = q in 
  let a = fmul (fsub y1 x1) (fsub y2 x2) in 
  let b = fmul (fadd y1 x1) (fadd y2 x2) in 
  let c = fmul (felem 0x2) (fmul (fmul d25519 t1) t2) in 
  let d = fmul 0x2 (fmul z1 z2) in 
  let e = fsub b a in 
  let f = fsub d c in 
  let g = fadd d c in 
  let h = fadd b a in 
  let x3 = fmul e f in 
  let y3 = fmul g h in 
  let t3 = fmul e h in 
  let z3 = fmul f g in 
  let p = Tuple(elts=x3
          y3
          z3
          t3,
          ctx=Load()) in 
  p 
let point_double (p:extended_point_t) : extended_point_t =
  let () = if ((p = Tuple(elts=0x0
    0x1
    0x1
    0x0,
    ctx=Load()))) then (p() )else (()) in 
  let (x1,y1,z1,t1) = p in 
  let a = fmul x1 x1 in 
  let b = fmul y1 y1 in 
  let c = fmul (felem 0x2) (fmul z1 z1) in 
  let h = fadd a b in 
  let e = fsub h (fmul (fadd x1 y1) (fadd x1 y1)) in 
  let g = fsub a b in 
  let f = fadd c g in 
  let x3 = fmul e f in 
  let y3 = fmul g h in 
  let t3 = fmul e h in 
  let z3 = fmul f g in 
  Tuple(elts=x3
  y3
  z3
  t3,
  ctx=Load()) 
let montgomery_ladder (k:scalar_t) (init:extended_point_t) : extended_point_t =
  let p0 : extended_point_t = Tuple(elts=0x0
                              0x1
                              0x1
                              0x0,
                              ctx=Load()) in 
  let p1 : extended_point_t = init in 
  let () = repeati (range 0x100)
    (fun i () ->
      let () = if ((k.[(0xff -. i)] = bit 0x1)) then (let (p0,p1) = Tuple(elts=p1
                      p0,
                      ctx=Load()) in () )else (()) in 
      let xx = point_double p0 in 
      let xp1 = point_add p0 p1 in 
      let () = if ((k.[(0xff -. i)] = bit 0x1)) then (let (p0,p1) = Tuple(elts=xp1
                      xx,
                      ctx=Load()) in () )else (let (p0,p1) = Tuple(elts=xx
                      xp1,
                      ctx=Load()) in ()) in 
      ())
    () in 
  p0 
let point_mul (s:serialized_scalar_t) (p:extended_point_t) : extended_point_t =
  let s_ = bitvector (bytes.to_nat_le s) 0x100 in 
  let Q : extended_point_t = Tuple(elts=0x0
                             0x1
                             0x1
                             0x0,
                             ctx=Load()) in 
  let Q1 = montgomery_ladder s_ p in 
  Q1 
let point_compress (p:extended_point_t) : serialized_point_t =
  let (px,py,pz,pt) = p in 
  let zinv = finv pz in 
  let x = fmul px zinv in 
  let y = fmul py zinv in 
  let r = nat_t (((0x2 **. 0xff) *. (x %. 0x2)) +. y) in 
  bytes.from_nat_le r 
let fsqrt_m1 : felem_t = felem (pow 0x2 ((p25519 -. 0x1) /. 0x4) p25519) 
let recover_x_coordinate (y:nat) (sign:bool) : felem_t =
  let () = if ((y >= p25519)) then (None() )else (let y = felem y in 
    let p1 = fmul d25519 (fsqr y) in 
    let p1_1 = fadd p1 0x1 in 
    let x2 = fmul (fsub (fsqr y) 0x1) (finv p1_1) in 
    let () = if ((x2 = 0x0) && sign) then (None() )else (let () = if ((x2 = 0x0) && (unknown op: <_ast3.Not object at 0x000001C4E96880F0> sign)) then (felem 0x0() )else (let x = pow x2 ((p25519 +. 0x3) /. 0x8) p25519 in 
        let () = if ((fsub (fsqr x) x2 != 0x0)) then (let x = fmul x fsqrt_m1 in () )else (()) in 
        let () = if ((fsub (fsqr x) x2 != 0x0)) then (None() )else (let () = if ((((x %. 0x2) = 0x1) != sign)) then (felem (p25519 -. x)() )else (x()) in ()) in ()) in ()) in ()) in  
let point_decompress (s:serialized_point_t) : extended_point_t =
  let y = bytes.to_nat_le s in 
  let sign = (((y /. (0x1 <<. 0xff)) %. 0x2) = 0x1) in 
  let y = (y %. (0x1 <<. 0xff)) in 
  let x = recover_x_coordinate y sign in 
  let () = if ((x = None)) then (None() )else (Tuple(elts=x
    (y %. p25519)
    0x1
    fmul x (y %. p25519),
    ctx=Load())()) in  
let expand_secret (s:serialized_scalar_t) : tuple2 serialized_scalar_t serialized_scalar_t =
  let h = sha512 s in 
  let h_low = slice h 0x0 0x20 in 
  let h_high = slice h 0x20 0x40 in 
  let h_low = h_low.[0x0] <- h_low.[0x0] &. u8 0xf8 in 
  let h_low = h_low.[0x1f] <- h_low.[0x1f] &. u8 0x7f in 
  let h_low = h_low.[0x1f] <- h_low.[0x1f] |. u8 0x40 in 
  Tuple(elts=h_low
  h_high,
  ctx=Load()) 
let _g_x : felem_t = felem 0x216936d3cd6e53fec0a4e231fdd6dc5c692cc7609525a7b2c9562d608f25d51a 
let _g_y : felem_t = felem 0x6666666666666666666666666666666666666666666666666666666666666658 
let g_ed25519 : extended_point_t = Tuple(elts=_g_x
                                   _g_y
                                   0x1
                                   fmul _g_x _g_y,
                                   ctx=Load()) 
let sigval_t = bytes_t 0x40 
let private_to_public (s:serialized_scalar_t) : serialized_point_t =
  let (a,_) = expand_secret s in 
  point_compress (point_mul s g_ed25519) 
let sign (priv:serialized_scalar_t) (msg:vlbytes_t) : sigval_t =
  let (a,prefix) = expand_secret priv in 
  let ap = point_compress (point_mul a g_ed25519) in 
  let tmp = create ((length msg) +. 0x40) (u8 0x0) in 
  let tmp = update_slice tmp 0x20 0x40 prefix in 
  let tmp = update_slice tmp 0x40 None msg in 
  let pmsg = slice tmp 0x20 None in 
  let r = sha512_modq pmsg in 
  let rp = point_compress (point_mul (bytes.from_nat_le r) g_ed25519) in 
  let tmp = update_slice tmp 0x0 0x20 rp in 
  let tmp = update_slice tmp 0x20 0x40 ap in 
  let h = sha512_modq tmp in 
  let s = ((r +. ((h *. bytes.to_nat_le a) %. q25519)) %. q25519) in 
  let tmp = update_slice tmp 0x20 0x40 (bytes.from_nat_le (nat s)) in 
  slice tmp 0x0 0x40 
let point_equal (p:extended_point_t) (q:extended_point_t) : bool =
  let (px,py,pz,pt) = p in 
  let (qx,qy,qz,qt) = q in 
  (fmul px qz = fmul qx pz) && (fmul py qz = fmul qy pz) 
let verify (pub:serialized_point_t) (msg:vlbytes) (sigval:sigval_t) : bool =
  let ap = point_decompress pub in 
  let () = if ((ap = None)) then (False() )else (()) in 
  let rs = slice sigval 0x0 0x20 in 
  let rp = point_decompress rs in 
  let () = if ((rp = None)) then (False() )else (()) in 
  let s = bytes.to_nat_le slice sigval 0x20 0x40 in 
  let tmp = if ((s >= q25519)) then (Falsetmp )else (let tmp = create ((length msg) +. 0x40) (u8 0x0) in 
    let tmp = update_slice tmp 0x0 0x20 rs in 
    let tmp = update_slice tmp 0x20 0x40 pub in 
    let tmp = update_slice tmp 0x40 None msg in 
    let h = sha512_modq tmp in 
    let sB = point_mul (bytes.from_nat_le s) g_ed25519 in 
    let hA = point_mul (bytes.from_nat_le h) ap in 
    point_equal sB (point_add rp hA)tmp) in  
