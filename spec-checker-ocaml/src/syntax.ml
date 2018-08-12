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
  | PEString of string
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
and ptyidents = pident list * ptype
and potyident = pident * ptype option

(* -------------------------------------------------------------------- *)
type pinstr_r =
  | PSFail    of pexpr
  | PSPass
  | PSVarDecl of ptyident * pexpr option
  | PSReturn  of pexpr option
  | PSExpr    of pexpr
  | PSAssign  of (pexpr * passop * pexpr)
  | PSIf      of (pexpr * pstmt) * (pexpr * pstmt) list * pstmt option
  | PSWhile   of (pexpr * pstmt) * pstmt option
  | PSFor     of (potyident * prange * pstmt) * pstmt option
  | PSDef     of pprocdef


and pprocdef = {
  pf_name  : pident;
  pf_att   : pexpr list;
  pf_retty : ptype;
  pf_args  : ptyident list;
  pf_body  : pstmt;
}

and plvalue  = pexpr
and prange   = pexpr option * pexpr
and pstmt    = pinstr list
and pinstr   = pinstr_r located

(* -------------------------------------------------------------------- *)
type ptopdecl =
  | PTImport    of pimport
  | PTTypeAlias of pident * pexpr
  | PTVarDecl   of ptyident * pexpr
  | PTDef       of pprocdef

and pimport = pqident * (pident option) list option

(* -------------------------------------------------------------------- *)
type pspec = ptopdecl list
