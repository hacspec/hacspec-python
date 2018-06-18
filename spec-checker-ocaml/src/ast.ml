(* -------------------------------------------------------------------- *)
module Ident : sig
  type ident = private string

  val make : string -> ident
end = struct
  type ident = string

  module H = Weak.Make(struct
    type t = string

    let equal   = ((=) : t -> t -> bool)
    let compare = (compare : t -> t -> int)
    let hash    = (Hashtbl.hash : t -> int)
  end)

  let table = H.create 0

  let make (s : string) : ident =
    H.merge table s
end

(* -------------------------------------------------------------------- *)
type symbol  = string
type qsymbol = (string list * string)
type ident   = Ident.ident
type wsize   = [`U8 | `U16 | `U32 | `U64 | `U128]

(* -------------------------------------------------------------------- *)
type uniop = Syntax.puniop
type binop = Syntax.pbinop
type assop = Syntax.passop

(* -------------------------------------------------------------------- *)
type refined = private unit
type raw     = private unit

type type_ =
  | TUnit
  | TBool
  | TInt
  | TString
  | TBit
  | TWord    of wsize
  | TTuple   of type_ list
  | TArray   of type_ * Big_int.big_int option
  | TRange   of Big_int.big_int * Big_int.big_int
  | TRefined of type_ * expr

(* -------------------------------------------------------------------- *)
and expr =
  | EVar    of ident
  | EUnit
  | EBool   of bool
  | EUInt   of Big_int.big_int
  | EString of string
  | ETuple  of expr list
  | EArray  of expr list
  | ERange  of expr
  | EEq     of bool * (expr * expr)
  | EUniOp  of uniop * expr
  | EBinOp  of binop * (expr * expr)
  | ECall   of ident * expr list
  | EGet    of expr * slice

and slice = [ `One of expr | `Slice of expr * expr ]

(* -------------------------------------------------------------------- *)
type tyexpr = expr * type_

(* -------------------------------------------------------------------- *)
module Type : sig
  val eq : type_ -> type_ -> bool
  val compat : type_ -> type_ -> bool

  val is_unit    : type_ -> bool
  val is_bool    : type_ -> bool
  val is_int     : type_ -> bool
  val is_string  : type_ -> bool
  val is_bit     : type_ -> bool
  val is_word    : type_ -> bool
  val is_tuple   : type_ -> bool
  val is_array   : type_ -> bool
  val is_refined : type_ -> bool
  val is_range   : type_ -> bool

  val as_word  : type_ -> wsize
  val as_tuple : type_ -> type_ list
  val as_array : type_ -> type_

  val strip : type_ -> type_
end = struct
  let eq = ((=) : type_ -> type_ -> bool)

  let is_unit    = function TUnit      -> true | _ -> false
  let is_bool    = function TBool      -> true | _ -> false
  let is_int     = function TInt       -> true | _ -> false
  let is_string  = function TString    -> true | _ -> false
  let is_bit     = function TBit       -> true | _ -> false
  let is_word    = function TWord    _ -> true | _ -> false
  let is_tuple   = function TTuple   _ -> true | _ -> false
  let is_array   = function TArray   _ -> true | _ -> false
  let is_refined = function TRefined _ -> true | _ -> false
  let is_range   = function TRange   _ -> true | _ -> false

  let as_word  = function TWord  ws      -> ws  | _ -> assert false
  let as_tuple = function TTuple tys     -> tys | _ -> assert false
  let as_array = function TArray (ty, _) -> ty  | _ -> assert false

  let rec strip (ty : type_) : type_ =
    match ty with
    | TUnit           -> TUnit
    | TBool           -> TBool
    | TInt            -> TInt
    | TString         -> TString
    | TBit            -> TBit
    | TWord    ws     -> TWord ws
    | TTuple   t      -> TTuple (List.map strip t)
    | TArray   (t, _) -> TArray (strip t, None)
    | TRefined (t, _) -> strip t  
    | TRange   _      -> TInt

  let compat (ty1 : type_) (ty2 : type_) =
    eq (strip ty1) (strip ty2)
end

(* -------------------------------------------------------------------- *)
type instr =
  | IFail   of tyexpr
  | IReturn of tyexpr option
  | IAssign of (lvalue * assop option) option * tyexpr
  | IIf     of (expr * block) * (expr * block) list * block option
  | IWhile  of (expr * block) * block option
  | IFor    of (ident * range * block) * block option

and block  = instr list
and lvalue = unit
and range  = expr option * expr

(* -------------------------------------------------------------------- *)
type tydecl  = { tyd_name : ident; tyd_body : type_; }
type vardecl = { vrd_name : ident; vrd_type : type_; vrd_init : expr; }

type 'env procdef = {
  prd_name : ident;
  prd_args : (ident * type_) list;
  prd_ret  : type_;
  prd_body : 'env * block;
}

(* -------------------------------------------------------------------- *)
type 'env topdecl1 =
  | TD_TyDecl  of tydecl
  | TD_VarDecl of vardecl
  | TD_ProcDef of 'env procdef

(* -------------------------------------------------------------------- *)
type 'env program = 'env * (('env topdecl1) list)
