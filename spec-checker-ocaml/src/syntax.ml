(* -------------------------------------------------------------------- *)
open Core
open Location

(* -------------------------------------------------------------------- *)
exception ParseError of Location.t * string option

(* -------------------------------------------------------------------- *)
type pident = string located

(* -------------------------------------------------------------------- *)
type pwsize = [ `U8 | `U16 | `U32 | `U64 | `U128 ]

type ptype_r =
  | PTUnit
  | PTBool
  | PTInt
  | PTString
  | PTBit
  | PTWord  of pwsize
  | PTTuple of ptype list
  | PTArray of ptype

and ptype = ptype_r located

(* -------------------------------------------------------------------- *)
type ptyident = pident * ptype

(* -------------------------------------------------------------------- *)
type puniop = [ `Not | `Neg ]

type pbinop = [
  | `Add | `Sub | `Mul | `Div
  | `And | `Or  | `Lt  | `Le  | `Gt  | `Ge
]

type passop = [ `Plain | `Add | `Sub | `Mul | `Div ]

(* -------------------------------------------------------------------- *)
type pexpr_r =
  | PEVar   of pident
  | PEBool  of bool
  | PEUInt  of Big_int.big_int
  | PETuple of pexpr list * bool
  | PEArray of pexpr list
  | PERange of pexpr
  | PEEq    of bool * (pexpr * pexpr)
  | PEUniOp of puniop * pexpr
  | PEBinOp of pbinop * (pexpr * pexpr)
  | PECall  of pident * pexpr list
  | PEGet   of pexpr * pslice

and pexpr  = pexpr_r located
and pslice = [ `One of pexpr | `Slice of (pexpr * pexpr) ]

(* -------------------------------------------------------------------- *)
type pinstr_r =
  | PSFail
  | PSPass
  | PSReturn of pexpr option
  | PSDecl   of ptyident * pexpr
  | PSExpr   of pexpr
  | PSAssign of (plvalue * passop * pexpr)
  | PSIf     of (pexpr * pstmt) * (pexpr * pstmt) list * pstmt option
  | PSWhile  of (pexpr * pstmt) * pstmt option
  | PSFor    of (pident * pexpr * pstmt) * pstmt option

and pstmt   = pinstr list
and pinstr  = pinstr_r located
and plvalue = pexpr

(* -------------------------------------------------------------------- *)
type ptopdecl =
  | PTVar of ptyident * pexpr
  | PTDef of ptyident * ptyident list * pstmt

(* -------------------------------------------------------------------- *)
type pspec = ptopdecl list
