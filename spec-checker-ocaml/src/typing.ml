(* -------------------------------------------------------------------- *)
open Core
open Location
open Syntax
open Ast

(* -------------------------------------------------------------------- *)
type ctype =
  | PUnit | PBool | PInt   | PString
  | PBit  | PWord | PTuple | PArray

type etype = [`Exact of type_ | `Approx of ctype]

(* -------------------------------------------------------------------- *)
let rec ctype_of_type (ty : type_) : ctype =
  match ty with
  | TUnit            -> PUnit
  | TBool            -> PBool
  | TInt             -> PInt
  | TString          -> PString
  | TBit             -> PBit
  | TWord    _       -> PWord
  | TTuple   _       -> PTuple
  | TArray   _       -> PArray
  | TRefined (ty, _) -> ctype_of_type ty
  | TRange   _       -> PInt

(* -------------------------------------------------------------------- *)
module Env : sig
  type env
  type tdecl = { tname : ident; tdef  : type_; }
  type vdecl = { vname : ident; vtype : type_; vrawty : type_; }
  type pdecl = { pname : ident; psig  : type_ list; pret : type_; }

  val empty : env

  module Types : sig
    val exists : env -> symbol -> bool
    val get : env -> symbol -> tdecl option
    val bind : env -> symbol * type_ -> env * ident
  end

  module Vars : sig
    val exists : env -> symbol -> bool
    val get : env -> symbol -> vdecl option
    val bind : env -> symbol * type_ -> env * ident
  end

  module Procs : sig
    val get : env -> symbol -> pdecl option
    val bind : env -> symbol -> type_ list * type_ -> env * ident
  end
end = struct
  type tdecl = { tname : ident; tdef  : type_; }
  type vdecl = { vname : ident; vtype : type_; vrawty : type_; }
  type pdecl = { pname : ident; psig  : type_ list; pret : type_; }

  type env = {
    e_types : tdecl Mstr.t;
    e_vars  : vdecl Mstr.t;
    e_procs : pdecl Mstr.t;
  }

  let dtypes = [
    ("bool"     , TBool      );
    ("int"      , TInt       );
    ("string"   , TString    );
    ("uint8_t"  , TWord `U8  );
    ("uint16_t" , TWord `U16 );
    ("uint32_t" , TWord `U32 );
    ("uint64_t" , TWord `U64 );
    ("uint128_t", TWord `U128);
    ("vlbytes"  , TArray (TWord `U8, None));
  ]

  module Types = struct
    let get (env : env) (x : symbol) =
      Mstr.Exceptionless.find x env.e_types

    let exists (env : env) (x : symbol) =
      Option.is_some (get env x)

    let bind (env : env) ((x, ty) : symbol * type_) =
      let decl = { tname = Ident.make x; tdef = ty } in
      let env  = { env with e_types = Mstr.add x decl env.e_types } in
      (env, decl.tname)
  end

  module Vars = struct
    let get (env : env) (x : symbol) =
      Mstr.Exceptionless.find x env.e_vars

    let exists (env : env) (x : symbol) =
      Option.is_some (get env x)

    let bind (env : env) ((x, ty) : symbol * type_) =
      let decl = { vname = Ident.make x; vtype = ty; vrawty = Type.strip ty } in
      let env  = { env with e_vars = Mstr.add x decl env.e_vars } in
      (env, decl.vname)
  end

  module Procs = struct
    let get (env : env) (x : symbol) =
      Mstr.Exceptionless.find x env.e_procs

    let bind (env : env) (f : symbol) ((sig_, ret) : type_ list * type_) =
      let decl = { pname = Ident.make f; psig = sig_; pret = ret } in
      let env  = { env with e_procs = Mstr.add f decl env.e_procs } in
      (env, decl.pname)

  end

  let empty =
    let empty = {
      e_types = Mstr.empty;
      e_vars  = Mstr.empty;
      e_procs = Mstr.empty;
    } in

    List.fold_left (fun env xty -> fst (Types.bind env xty)) empty dtypes
end

(* -------------------------------------------------------------------- *)
type env = Env.env

(* -------------------------------------------------------------------- *)
type tyerror =
  | CannotInferType
  | UnknownVar         of symbol
  | UnknownProc        of symbol
  | UnknownTypeName    of symbol
  | DuplicatedVarName  of symbol
  | DuplicatedTypeName of symbol
  | DuplicatedArgName  of symbol
  | MustReturnAValue
  | ExpectVoidReturn
  | InvalidTypeExpr
  | InvalidArgCount
  | InvalidTypeCtor    of symbol
  | InvalidType        of type_ * etype

(* -------------------------------------------------------------------- *)
let pp_tyerror fmt (error : tyerror) =
  match error with
  | CannotInferType ->
      Format.fprintf fmt "cannot infer type of this expression"

  | UnknownVar x ->
      Format.fprintf fmt "unknown variable: `%s'" x

  | UnknownProc x ->
      Format.fprintf fmt "unknown procedure: `%s'" x

  | UnknownTypeName x ->
      Format.fprintf fmt "unknown type name: `%s'" x

  | DuplicatedVarName x ->
      Format.fprintf fmt "duplicated var declaration for: `%s'" x

  |  DuplicatedTypeName x ->
      Format.fprintf fmt "duplicated type declaration for: `%s'" x

  | DuplicatedArgName x ->
      Format.fprintf fmt "duplicated argument name: `%s'" x

  | MustReturnAValue ->
      Format.fprintf fmt "void-return not allowed"

  | ExpectVoidReturn ->
      Format.fprintf fmt "non-void-return not allowed"

  | InvalidTypeExpr ->
      Format.fprintf fmt "invalid type expression"

  | InvalidArgCount ->
      Format.fprintf fmt "invalid arguments count"

  | InvalidTypeCtor x ->
      Format.fprintf fmt "invalid type constructor application: `%s'" x

  | InvalidType _ ->
      Format.fprintf fmt "this expression has an invalid type"

(* -------------------------------------------------------------------- *)
exception TyError of (Location.t * env * tyerror)

(* -------------------------------------------------------------------- *)
let pp_tyerror_exn fmt = function
  | TyError (loc, _, error) ->
      Format.fprintf fmt "%s: %a" (Location.tostring loc) pp_tyerror error

  | exn -> raise exn

let () = Pexception.register pp_tyerror_exn

(* -------------------------------------------------------------------- *)
let error ~(loc : Location.t) (env : env) (exn : tyerror) =
  raise (TyError (loc, env, exn))

(* -------------------------------------------------------------------- *)
let rec tt_type (env : env) (pty : ptype) =
  match unloc pty with
  | PEVar  ([], x)         ->  tt_type_app env (x, [])
  | PECall (([], x), args) ->  tt_type_app env (x, args)

  | _ -> error ~loc:(loc pty) env InvalidTypeExpr

(* -------------------------------------------------------------------- *)
and tt_type_app (env : env) ((x, args) : pident * pexpr list) =
  match unloc x, args with
  | "range_t", [i; j] ->
      let i = tt_cint env i in
      let j = tt_cint env j in
      TRange (i, j)

  | "array_t", [ty] ->
      TArray (tt_type env ty, None)

  | "array_t", [ty; sz] ->
      let sz = tt_cint env sz in
      let ty = tt_type env ty in
      TArray (ty, Some sz)

  | "bytes_t", [sz] ->
      let sz = tt_cint env sz in
      TArray (TWord `U8, Some sz)

    (* FIXME: why 3? *)
  | "refine3", [ty; e] ->
      let ty = tt_type env ty in
      TRefined (ty, EUnit)      (* FIXME: refinment *)

  | _, [] -> begin
      match Env.Types.get env (unloc x) with
      | None -> error ~loc:(loc x) env (UnknownTypeName (unloc x))
      | Some decl -> decl.Env.tdef
    end

  | _ -> error ~loc:(loc x) env (InvalidTypeCtor (unloc x))

(* -------------------------------------------------------------------- *)
and tt_cint (env : env) (e : pexpr) =
  match fst (tt_expr ~cty:(`Approx PInt) env e) with
  | EUInt i -> i | _ -> assert false

(*
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
 *)

(* -------------------------------------------------------------------- *)
and tt_expr ?(cty : etype option) (env : env) (pe : pexpr) =
  let e, ety =
    match unloc pe with
    | PEVar ([], x) -> begin
        match Env.Vars.get env (unloc x) with
        | None -> error ~loc:(loc pe) env (UnknownVar (unloc x))
        | Some x -> (EVar x.Env.vname, x.Env.vrawty)
      end

    | PEVar _ ->
        assert false
  
    | PEBool   b -> (EBool   b, TBool  )
    | PEUInt   i -> (EUInt   i, TInt   )
    | PEString s -> (EString s, TString)
  
    | PETuple ([], _) ->
        (EUnit, TUnit)
  
    | PETuple ([pe], false) ->
        tt_expr env pe
  
    | PETuple (pes, _) ->
        let es, tys =
          List.split (List.map (tt_expr env) pes)
        in (ETuple es, TTuple tys)
  
    | PEArray [] ->
        error ~loc:(loc pe) env CannotInferType

    | PEArray (e :: es) ->
        let e, ety = tt_expr env e in
        let es =
          List.map (fun e -> fst (tt_expr ~cty:(`Exact ety) env e)) es in
        (EArray (e :: es), TArray (ety, None))
  
    | PEEq (b, (pe1, pe2)) ->
        let e1, ty1 = tt_expr env pe1 in
        let e2, ty2 = tt_expr env pe2 in
  
        if not (Type.eq ty1 ty2) then
          error ~loc:(loc pe) env (InvalidType (ty1, `Exact ty2));
        (EEq (b, (e1, e2)), TBool)

    | PEFun _ ->
        assert false

    | PEUniOp (_op, _pe) ->
        assert false
  
    | PEBinOp (_op, (_pe1, _pe2)) ->
        assert false
  
    | PECall (([], f), args) ->
        let f =
          match Env.Procs.get env (unloc f) with
          | None   -> error ~loc:(loc pe) env (UnknownProc (unloc f))
          | Some f -> f in

        if List.length args <> List.length f.Env.psig then
          error ~loc:(loc pe) env InvalidArgCount;

        let args =
          List.map2 (fun e ty -> fst (tt_expr ~cty:(`Exact ty) env e))
          args f.Env.psig in

        (ECall (f.Env.pname, args), Type.strip f.Env.pret)

    | PECall _ ->
        assert false

    | PEGet (pe, ps) ->
        let e, ety = tt_expr ~cty:(`Approx PArray) env pe in
        let s = tt_slice env ps in
        let ty =
         match s with
         | `One   _ -> Type.as_array ety
         | `Slice _ -> ety

        in (EGet (e, s), ty)

  in

  Option.may (fun (cty : etype) ->
    let compat =
      match cty with
      | `Approx cty -> ctype_of_type ety = cty
      | `Exact  cty -> Type.eq ety cty
    in
      if not compat then
        error ~loc:(loc pe) env (InvalidType (ety, cty)))
    cty;

  (e, ety)

(* -------------------------------------------------------------------- *)
and tt_slice (env : env) (s : pslice) : slice =
  match s with
  | `One pe ->
      `One (fst (tt_expr ~cty:(`Approx PInt) env pe))

  | `Slice (pe1, pe2) ->
      let e1 = fst (tt_expr ~cty:(`Approx PInt) env pe1) in
      let e2 = fst (tt_expr ~cty:(`Approx PInt) env pe2) in
      `Slice (e1, e2)

(* -------------------------------------------------------------------- *)
let rec tt_instr ?(rty : type_ option) (env : env) (i : pinstr) =
  match unloc i with
  | PSFail e ->
      let _ = tt_expr ~cty:(`Exact TString) env e in ()

  | PSPass ->
      ()

  | PSDecl ((x, ty), e) ->
      let ty = tt_type env ty in
      let _  = tt_expr ~cty:(`Exact ty) env e in
      ()

  | PSAssign _ ->
      assert false

  | PSReturn None ->
      if Option.is_some rty then
        error ~loc:(loc i) env MustReturnAValue

  | PSReturn (Some e) -> begin
      let _ =
        match rty with
        | None    -> error ~loc:(loc i) env ExpectVoidReturn
        | Some ty -> tt_expr ~cty:(`Exact ty) env e
      in ()
    end

  | PSExpr e ->
      let _ = tt_expr env e in ()

  | PSIf ((c, bc), elifs, el) ->
      let ttif1 (c, bc) =
        let _ = tt_expr ~cty:(`Exact TBool) env c in
        let _ = tt_stmt ?rty env bc in
        () in

      let _ = ttif1 (c, bc) in
      let _ = List.iter ttif1 elifs in
      let _ = Option.may (tt_stmt ?rty env) el in

      ()

  | PSFor ((x, (i, j), bc), el) ->
      let _ = Option.map (tt_expr ~cty:(`Exact TInt) env) i in
      let _ = tt_expr ~cty:(`Exact TInt) env j in

      let env, x = Env.Vars.bind env (unloc x, TInt) in

      let _ = tt_stmt ?rty env bc in
      let _ = Option.may (tt_stmt ?rty env) el in

      ()

  | PSWhile ((c, bc), el) ->
      let _ = tt_expr ~cty:(`Exact TBool) env c in
      let _ = tt_stmt ?rty env bc in
      let _ = Option.may (tt_stmt ?rty env) el in

      ()

  | PSDef pf ->
      assert false

(* -------------------------------------------------------------------- *)
and tt_stmt ?(rty : type_ option) (env : env) (s : pstmt) =
  List.iter (tt_instr ?rty env) s

(* -------------------------------------------------------------------- *)
let tt_import (env : env) (_ : pimport) =
  env

(* -------------------------------------------------------------------- *)
let tt_tydecl (env : env) ((x, ty) : pident * pexpr) =
  let ty = tt_type env ty in

  if Env.Types.exists env (unloc x) then
    error ~loc:(loc x) env (DuplicatedTypeName (unloc x));

  fst (Env.Types.bind env (unloc x, ty))

(* -------------------------------------------------------------------- *)
let tt_vardecl (env : env) ((x, ty), e : (pident * pexpr) * pexpr) =
  let ty = tt_type env ty in
  let _e = fst (tt_expr ~cty:(`Exact ty) env e) in

  if Env.Vars.exists env (unloc x) then
    error ~loc:(loc x) env (DuplicatedVarName (unloc x));

  fst (Env.Vars.bind env (unloc x, ty))

(* -------------------------------------------------------------------- *)
(* FIXME: check for duplicate argument name *)
let tt_procdef (env : env) (((f, fty), args, body) : procdef) =
  let fty  = tt_type env fty in
  let args = List.map (fun (x, xty) -> (unloc x, tt_type env xty)) args in
  let env1 = List.fold_left (fun env xty -> fst (Env.Vars.bind env xty)) env args in
  let _    = tt_stmt ~rty:fty env1 body in

  fst (Env.Procs.bind env (unloc f) (List.map snd args, fty))

(* -------------------------------------------------------------------- *)
let tt_topdecl1 (env : env) = function
  | PTImport info -> tt_import  env info
  | PTDef    info -> tt_procdef env info

  | PTVar ((x, None), ty)   -> tt_tydecl  env (x, ty)
  | PTVar ((x, Some ty), e) -> tt_vardecl env ((x, ty), e)

(* -------------------------------------------------------------------- *)
let tt_program (p : pspec) =
  List.fold_left tt_topdecl1 Env.empty p
