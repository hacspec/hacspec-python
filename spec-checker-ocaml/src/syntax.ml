(* -------------------------------------------------------------------- *)
open Core
open Location

(* -------------------------------------------------------------------- *)
exception ParseError of Location.t * string option

let pp_parse_error fmt loc msg =
  let msg =
       Option.bind msg (fun x -> Some (": " ^ x))
    |> Option.default ""
    |> (fun x -> "parse error" ^ x) in

  Format.fprintf fmt "%s: %s" (Location.tostring loc) msg

let () =
  let pp fmt exn =
    match exn with
    | ParseError (loc, msg) -> pp_parse_error fmt loc msg
    | _ -> raise exn
  in
    Pexception.register pp

(* -------------------------------------------------------------------- *)
type pident  = string located
type pqident = pident list * pident

(* -------------------------------------------------------------------- *)
type puniop = [ `Not | `Neg | `BNot ]

type pbinop = [
  | `Add | `Sub  | `Mul | `Div  | `IDiv | `Mod
  | `Pow | `BAnd | `BOr | `BXor
  | `And | `Or   | `Lt  | `Le   | `Gt   | `Ge
  | `LSL | `LSR
]

type passop =
  [ `Plain | `Add  | `Sub | `Mul  | `Div | `IDiv | `Mod
  | `Pow   | `BAnd | `BOr | `BXor ]

(* -------------------------------------------------------------------- *)
type pexpr_r =
  | PEVar    of pqident
  | PEBool   of bool
  | PEUInt   of Big_int.big_int
  | PEString of bytes
  | PETuple  of pexpr list * bool
  | PEArray  of pexpr list
  | PEEq     of bool * (pexpr * pexpr)
  | PEUniOp  of puniop * pexpr
  | PEBinOp  of pbinop * (pexpr * pexpr)
  | PECall   of pqident * pexpr list
  | PEGet    of pexpr * pslice
  | PEFun    of pident list * pexpr

and pexpr  = pexpr_r located
and ptype  = pexpr
and pslice = [ `One of pexpr | `Slice of (pexpr * pexpr) ]

and ptyident  = pident * ptype
and potyident = pident * ptype option

(* -------------------------------------------------------------------- *)
type pinstr_r =
  | PSFail   of pexpr
  | PSPass
  | PSReturn of pexpr option
  | PSDecl   of ptyident * pexpr
  | PSExpr   of pexpr
  | PSAssign of (plvalue * passop * pexpr)
  | PSIf     of (pexpr * pstmt) * (pexpr * pstmt) list * pstmt option
  | PSWhile  of (pexpr * pstmt) * pstmt option
  | PSFor    of (potyident * prange * pstmt) * pstmt option
  | PSDef    of pprocdef

and prange   = pexpr option * pexpr
and pstmt    = pinstr list
and pinstr   = pinstr_r located
and plvalue  = pexpr
and pprocdef = ptyident * ptyident list * pstmt

(* -------------------------------------------------------------------- *)
type ptopdecl =
  | PTImport of pimport
  | PTVar    of potyident * pexpr
  | PTDef    of pprocdef

and pimport = pqident * (pident option) list option

(* -------------------------------------------------------------------- *)
type pspec = ptopdecl list
