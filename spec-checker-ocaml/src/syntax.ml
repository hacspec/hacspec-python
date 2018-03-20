(* -------------------------------------------------------------------- *)
open Core
open Location

(* -------------------------------------------------------------------- *)
exception ParseError of Location.t * string option

(* -------------------------------------------------------------------- *)
type pident = string located

(* -------------------------------------------------------------------- *)
type puniop = [ `Not | `Neg ]

type pbinop = [
  | `Eq  | `NEq | `Add | `Sub | `Mul | `Div
  | `And | `Or  | `Lt  | `Le  | `Gt  | `Ge
]

type passop = [ `Plain | `Add | `Sub | `Mul | `Div ]

(* -------------------------------------------------------------------- *)
type pexpr_r =
  | EVar   of pident
  | EBool  of bool
  | EUInt  of Big_int.big_int
  | ETuple of pexpr list * bool
  | EArray of pexpr list
  | ERange of pexpr
  | EUniOp of puniop * pexpr
  | EBinOp of pbinop * (pexpr * pexpr)
  | ECall  of pident * pexpr list
  | EGet   of pexpr * pslice

and pexpr  = pexpr_r located
and pslice = [ `One of pexpr | `Slice of (pexpr * pexpr) ]

(* -------------------------------------------------------------------- *)
type pinstr_r =
  | SFail
  | SPass
  | SReturn of pexpr option
  | SAssign of (plvalue * passop * pexpr)
  | SIf     of (pexpr * pstmt) * (pexpr * pstmt) list * pstmt option
  | SWhile  of (pexpr * pstmt) * pstmt option
  | SFor    of (pident * pexpr * pstmt) * pstmt option

and pstmt   = pinstr list
and pinstr  = pinstr_r located
and plvalue = pexpr

(* -------------------------------------------------------------------- *)
type ptopdecl =
  | TVar of pident * pexpr
  | TDef of pident * pident list * pstmt

(* -------------------------------------------------------------------- *)
type pspec = ptopdecl list
