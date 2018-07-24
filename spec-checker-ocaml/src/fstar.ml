open Location
open Syntax
open Ast
module T = Typing

let fstar_of_uniop u = 
  match u with
  | `Not -> "not"
  | `Neg -> "-"
  | `BNot -> "~"

let fstar_of_binop b = 
  match b with
  | `Add -> "+."
  | `Sub -> "-."
  | `Mul -> "*."
  | `Div -> "/."
  | `IDiv -> "/."
  | `Mod -> "%"
  | `Pow -> "**."
  | `BAnd -> "&."
  | `BOr -> "|."
  | `BXor -> "^."
  | `And -> "&&"
  | `Or -> "||"
  | `Lt -> "<."
  | `Gt -> ">."
  | `Le -> "<=."
  | `Ge -> ">=."
  | `LSL -> "<<."
  | `LSR -> ">>."
  

let rec fstar_of_expr b e =
  match e with
  | EVar v -> Ident.to_string v 
  | EUnit -> "()"
  | EBool b -> string_of_bool b 
  | EUInt u -> Big_int.string_of_big_int u
  | EString s -> "\""^s^"\""
  | ETuple el -> "("^String.concat "," (List.map (fstar_of_expr false) el)^")"
  | EArray el -> if b then "(createL ["^String.concat "; " (List.map (fstar_of_expr false) el)^"])"
                 else "createL ["^String.concat "; " (List.map (fstar_of_expr false) el)^"]"
  | ECall (i,[e]) when Ident.to_string i = "uint32" -> 
		if b then "(u32 "^fstar_of_expr true e^")"
		else "u32 "^fstar_of_expr true e
  | ECall (i,el) -> 
                if b then "("^Ident.to_string i^" "^(String.concat " " (List.map (fstar_of_expr true) el))^")" 
		else Ident.to_string i^" "^(String.concat " " (List.map (fstar_of_expr true) el))
  | EUniOp (u,e) -> fstar_of_uniop u ^ " " ^ (fstar_of_expr false e)
  | EBinOp (b,(e1,e2)) -> fstar_of_expr true e1 ^ " " ^ fstar_of_binop b ^ " " ^ fstar_of_expr true e2
  | EEq (false,(e1,e2)) -> fstar_of_expr true e1 ^ " = " ^ fstar_of_expr true e2
  | EEq (true,(e1,e2)) -> fstar_of_expr true e1 ^ " <> " ^ fstar_of_expr true e2
  | EGet(e1,`One e2) -> (fstar_of_expr true e1)^".["^(fstar_of_expr false e2)^"]"
  | EGet(e1,`Slice (e2,e3)) -> "slice "^(fstar_of_expr true e1)^" "^(fstar_of_expr true e2)^" "^(fstar_of_expr true e3)
  | _ -> ("not an f* expr:")

let rec fstar_of_type b ty =
  match ty with
  | TUnit    -> "unit"
  | TBool    -> "bool"
  | TInt     -> "int"
  | TString  -> "string"
  | TBit     -> "bit"
  | TWord `U8  -> "uint8_t"
  | TWord `U16 -> "uint16_t"
  | TWord `U32  -> "uint32_t"
  | TWord `U64  -> "uint64_t"
  | TWord `U128  -> "uint128_t"

  | TTuple tys ->
        "("^(String.concat ", " (List.map (fstar_of_type false) tys))^")"

  | TArray (ty, None) ->
       if b then Format.sprintf "(seq %s)" (fstar_of_type true ty)
       else Format.sprintf "seq %s" (fstar_of_type true ty) 
 
      
  | TArray (ty, Some i) ->
       if b then
        Format.sprintf "(lseq %s %s)"
        (fstar_of_type true ty) (Big_int.string_of_big_int i)
       else 
        Format.sprintf "lseq %s %s"
        (fstar_of_type true ty) (Big_int.string_of_big_int i)

  | TRange (i, j) ->
      Format.sprintf "range_t %s %s"
        (Big_int.string_of_big_int i)
        (Big_int.string_of_big_int j)

  | TRefined (ty, e) ->
      Format.sprintf "refine_t (%s)" (fstar_of_type true ty)

  | TNamed name ->
      Format.sprintf "%s" (QSymbol.to_string name)

let fstar_of_topdecl d =
    match d with
    | TD_TyDecl td -> "let "^Ident.to_string td.tyd_name^" : Type0 = "^fstar_of_type false td.tyd_body
    | TD_VarDecl vd -> "let "^Ident.to_string vd.vrd_name^" : "^fstar_of_type false vd.vrd_type^" = "^fstar_of_expr false vd.vrd_init
    | TD_ProcDef pd -> "let "^Ident.to_string pd.prd_name^" "^(String.concat " " (List.map (fun (v,t) -> "(" ^ Ident.to_string v ^ " : " ^ fstar_of_type false t ^ ")") pd.prd_args)) ^" : " ^(fstar_of_type false pd.prd_ret)
let fstar_of_program (n:string) (p: T.Env.env program) : string =
    let e,dl = p in
    "module " ^(String.capitalize_ascii n)^"\n"^ 
    String.concat "\n" (List.map fstar_of_topdecl dl) ^"\n"


