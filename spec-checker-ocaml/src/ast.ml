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
type ident = Ident.ident
type wsize = Syntax.pwsize

(* -------------------------------------------------------------------- *)
type type_ =
  | TUnit
  | TBool
  | TInt
  | TString
  | TBit
  | TWord  of wsize
  | TTuple of type_ list
  | TArray of type_

(* -------------------------------------------------------------------- *)
type ctype =
  | PUnit | PBool | PInt   | PString
  | PBit  | PWord | PTuple | PArray

(* -------------------------------------------------------------------- *)
type uniop = Syntax.puniop
type binop = Syntax.pbinop
type assop = Syntax.passop

(* -------------------------------------------------------------------- *)
type expr =
  | EVar   of ident
  | EUnit
  | EBool  of bool
  | EUInt  of Big_int.big_int
  | ETuple of expr list
  | EArray of expr list
  | ERange of expr
  | EEq    of bool * (expr * expr)
  | EUniOp of uniop * expr
  | EBinOp of binop * (expr * expr)
  | ECall  of ident * expr list
  | EGet   of expr * slice

and slice = [ `One of expr | `Slice of expr * expr ]

(* -------------------------------------------------------------------- *)
module Type : sig
  val eq : type_ -> type_ -> bool
  val compat : type_ -> ctype -> bool

  val is_unit   : type_ -> bool
  val is_bool   : type_ -> bool
  val is_int    : type_ -> bool
  val is_string : type_ -> bool
  val is_bit    : type_ -> bool
  val is_word   : type_ -> bool
  val is_tuple  : type_ -> bool
  val is_array  : type_ -> bool

  val as_array : type_ -> type_

  val to_ctype : type_ -> ctype
end = struct
  let eq = ((=) : type_ -> type_ -> bool)

  let is_unit   = function TUnit     -> true | _ -> false
  let is_bool   = function TBool     -> true | _ -> false
  let is_int    = function TInt      -> true | _ -> false
  let is_string = function TString   -> true | _ -> false
  let is_bit    = function TBit      -> true | _ -> false
  let is_word   = function TWord   _ -> true | _ -> false
  let is_tuple  = function TTuple  _ -> true | _ -> false
  let is_array  = function TArray  _ -> true | _ -> false

  let to_ctype = function
    | TUnit      -> PUnit  
    | TBool      -> PBool  
    | TInt       -> PInt   
    | TString    -> PString
    | TBit       -> PBit   
    | TWord   _  -> PWord  
    | TTuple  _  -> PTuple 
    | TArray  _  -> PArray 

  let as_array = function TArray ty -> ty | _ -> assert false

  let compat (ty : type_) (cty : ctype) =
    to_ctype ty = cty
end
