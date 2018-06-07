(* -------------------------------------------------------------------- *)
open Core
open Location
open Syntax
open Ast

(* -------------------------------------------------------------------- *)
module Env : sig
  type env
end = struct
  type env = unit
end

(* -------------------------------------------------------------------- *)
type env = Env.env

(* -------------------------------------------------------------------- *)
type tyerror =
  | InvalidType   of type_ * ctype
  | InvalidTypeEq of type_ * type_

(* -------------------------------------------------------------------- *)
exception TyError of (Location.t * env * tyerror)

(* -------------------------------------------------------------------- *)
let error ~(loc : Location.t) (env : env) (exn : tyerror) =
  raise (TyError (loc, env, exn))

(* -------------------------------------------------------------------- *)
let rec tt_type (pty : ptype) =
  match unloc pty with
  | PTUnit      -> TUnit
  | PTBool      -> TBool
  | PTInt       -> TInt
  | PTString    -> TString
  | PTBit       -> TBit
  | PTWord w    -> TWord (w :> wsize)
  | PTTuple tys -> TTuple (List.map tt_type tys)
  | PTArray ty  -> TArray (tt_type ty)

(* -------------------------------------------------------------------- *)
let tt_uniop (op : puniop) =
  match op with
  | `Not -> PBool, TBool
  | `Neg -> PInt , TInt

(* -------------------------------------------------------------------- *)
let tt_binop (op : pbinop) =
  match op with
  | `Add -> (PInt , PInt ), TInt
  | `Sub -> (PInt , PInt ), TInt
  | `Mul -> (PInt , PInt ), TInt
  | `Div -> (PInt , PInt ), TInt
  | `And -> (PBool, PBool), TBool
  | `Or  -> (PBool, PBool), TBool
  | `Lt  -> (PInt , PInt ), TBool
  | `Le  -> (PInt , PInt ), TBool
  | `Gt  -> (PInt , PInt ), TBool
  | `Ge  -> (PInt , PInt ), TBool

(* -------------------------------------------------------------------- *)
let rec tt_expr ?(cty : ctype option) (env : env) (pe : pexpr) =
  let e, ety =
    match unloc pe with
    | PEVar x ->
        assert false
  
    | PEBool b -> (EBool b, TBool)
    | PEUInt i -> (EUInt i, TInt )
  
    | PETuple ([], _) ->
        (EUnit, TUnit)
  
    | PETuple ([pe], false) ->
        tt_expr env pe
  
    | PETuple (pes, _) ->
        let es, tys =
          List.split (List.map (tt_expr env) pes)
        in (ETuple es, TTuple tys)
  
    | PEArray pes ->
        assert false
  
    | PERange pe ->
        let e = fst (tt_expr ~cty:PInt env pe) in
        (ERange e, TArray TInt)
  
    | PEEq (b, (pe1, pe2)) ->
        let e1, ty1 = tt_expr env pe1 in
        let e2, ty2 = tt_expr env pe2 in
  
        if not (Type.eq ty1 ty2) then
          error ~loc:(loc pe) env (InvalidTypeEq (ty1, ty2));
        (EEq (b, (e1, e2)), TBool)
  
    | PEUniOp (op, pe) ->
        let cty, ty = tt_uniop op in
        let e = fst (tt_expr ~cty:cty env pe) in
        (EUniOp (op, e), ty)
  
    | PEBinOp (op, (pe1, pe2)) ->
        let (c1, c2), ty = tt_binop op in
        let e1 = fst (tt_expr ~cty:c1 env pe1) in
        let e2 = fst (tt_expr ~cty:c2 env pe2) in
        (EBinOp (op, (e1, e2)), ty)
  
    | PECall (f, pargs) ->
        assert false
  
    | PEGet (pe, ps) ->
        let e, ety = tt_expr ~cty:PArray env pe in
        let s = tt_slice env ps in
        let ty =
         match s with
         | `One   _ -> Type.as_array ety
         | `Slice _ -> ety

        in (EGet (e, s), ty)

  in

  Option.may (fun cty -> 
    if not (Type.compat ety cty) then
      error ~loc:(loc pe) env (InvalidType (ety, cty)))
    cty;

  (e, ety)

(* -------------------------------------------------------------------- *)
and tt_slice (env : env) (s : pslice) : slice =
  match s with
  | `One pe ->
      `One (fst (tt_expr ~cty:PInt env pe))

  | `Slice (pe1, pe2) ->
      let e1 = fst (tt_expr ~cty:PInt env pe1) in
      let e2 = fst (tt_expr ~cty:PInt env pe2) in
      `Slice (e1, e2)

