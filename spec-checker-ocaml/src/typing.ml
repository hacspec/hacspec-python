(* -------------------------------------------------------------------- *)
open Core
open Location
open Syntax
open Ast

(* -------------------------------------------------------------------- *)
let qunloc ((nm, x) : pqident) : qsymbol =
  (List.map unloc nm, unloc x)

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

  module Mod : sig
    val get : env -> symbol -> env option
    val bind : env -> symbol -> env -> env
  end
end = struct
  type tdecl = { tname : ident; tdef  : type_; }
  type vdecl = { vname : ident; vtype : type_; vrawty : type_; }
  type pdecl = { pname : ident; psig  : type_ list; pret : type_; }

  type env = {
    e_types : tdecl Mstr.t;
    e_vars  : vdecl Mstr.t;
    e_procs : pdecl Mstr.t;
    e_mods  : env   Mstr.t;
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

  module Mod = struct
    let get (env : env) (x : symbol) =
      Mstr.Exceptionless.find x env.e_mods

    let bind (env : env) (x : symbol) (mod_ : env) =
      { env with e_mods = Mstr.add x mod_ env.e_mods }
  end

  let empty =
    let empty = {
      e_types = Mstr.empty;
      e_vars  = Mstr.empty;
      e_procs = Mstr.empty;
      e_mods  = Mstr.empty;
    } in

    List.fold_left (fun env xty -> fst (Types.bind env xty)) empty dtypes
end

(* -------------------------------------------------------------------- *)
type env = Env.env

(* -------------------------------------------------------------------- *)
type tyerror =
  | CannotInferType
  | UnknownVar         of qsymbol
  | UnknownProc        of qsymbol
  | UnknownTypeName    of qsymbol
  | UnknownModule      of qsymbol
  | DuplicatedVarName  of symbol
  | DuplicatedTypeName of symbol
  | DuplicatedArgName  of symbol
  | MustReturnAValue
  | ExpectVoidReturn
  | InvalidTypeExpr
  | InvalidArgCount
  | InvalidTypeCtor    of symbol
  | InvalidType        of type_ * etype list

(* -------------------------------------------------------------------- *)
let pp_tyerror fmt (error : tyerror) =
  let pp_qsymbol fmt (nm, x) =
    Format.fprintf fmt "%s" (String.concat "." (nm @ [x])) in

  match error with
  | CannotInferType ->
      Format.fprintf fmt "cannot infer type of this expression"

  | UnknownVar x ->
      Format.fprintf fmt "unknown variable: `%a'" pp_qsymbol x

  | UnknownProc x ->
      Format.fprintf fmt "unknown procedure: `%a'" pp_qsymbol x

  | UnknownTypeName x ->
      Format.fprintf fmt "unknown type name: `%a'" pp_qsymbol x

  | UnknownModule x ->
      Format.fprintf fmt "unknown module name: `%a'" pp_qsymbol x

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
      | None -> error ~loc:(loc x) env (UnknownTypeName ([], unloc x))
      | Some decl -> decl.Env.tdef
    end

  | _ -> error ~loc:(loc x) env (InvalidTypeCtor (unloc x))

(* -------------------------------------------------------------------- *)
and tt_cint (env : env) (e : pexpr) =
  match fst (tt_expr ~cty:(`Approx PInt) env e) with
  | EUInt i -> i | _ -> assert false

(* -------------------------------------------------------------------- *)
and tt_expr ?(cty : etype option) (env : env) (pe : pexpr) =
  let check_ty ~loc (etys : ctype list) (ty : type_) =
    if not (List.exists ((=) (ctype_of_type ty)) etys) then
      error ~loc env (InvalidType (ty, List.map (fun ty -> `Approx ty) etys))

  and check_ty_eq ~loc ~src ~dst =
    if not (Type.eq src dst) then
      error ~loc env (InvalidType (src, [`Exact dst]))

  in

  let e, ety =
    match unloc pe with
    | PEVar ((nm, x) as nmx) -> begin
        let senv = tt_module env nm in

        match Env.Vars.get senv (unloc x) with
        | None -> error ~loc:(loc pe) env (UnknownVar (qunloc nmx))
        | Some x -> (EVar x.Env.vname, x.Env.vrawty)
      end

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
          error ~loc:(loc pe) env (InvalidType (ty1, [`Exact ty2]));
        (EEq (b, (e1, e2)), TBool)

    | PEFun _ ->
        error ~loc:(loc pe) env CannotInferType

    | PEUniOp (op, pe) -> begin
        let e, ty = tt_expr env pe in

        match op with
        | `Not as op ->
            check_ty ~loc:(loc pe) [PBool] ty;
            EUniOp (op, e), TBool

        | `Neg as op ->
            check_ty ~loc:(loc pe) [PInt] ty;
            EUniOp (op, e), TInt

        | `BNot as op ->
            check_ty ~loc:(loc pe) [PWord] ty;
            EUniOp (op, e), ty
      end
  
    | PEBinOp (op, (pe1, pe2)) -> begin
        let e1, ty1 = tt_expr env pe1 in
        let e2, ty2 = tt_expr env pe2 in

        match op with
        | (`Add | `Sub | `Mul | `Div | `IDiv | `Mod) as op ->
            check_ty ~loc:(loc pe1) [PWord; PInt] ty1;
            check_ty ~loc:(loc pe2) [PWord; PInt] ty2;
            check_ty_eq ~loc:(loc pe2) ~dst:ty1 ~src:ty2;
            EBinOp (op, (e1, e2)), ty1

        | `Pow as op ->
            check_ty ~loc:(loc pe1) [PWord] ty1;
            check_ty ~loc:(loc pe2) [PInt ] ty2;
            EBinOp (op, (e1, e2)), ty1

        | (`BAnd | `BOr | `BXor) as op ->
            check_ty ~loc:(loc pe1) [PWord] ty1;
            check_ty ~loc:(loc pe2) [PWord] ty2;
            check_ty_eq ~loc:(loc pe2) ~dst:ty1 ~src:ty2;
            EBinOp (op, (e1, e2)), ty1

        | (`LSL | `LSR) as op ->
            check_ty ~loc:(loc pe1) [PWord] ty1;
            check_ty ~loc:(loc pe2) [PInt ] ty2;
            EBinOp (op, (e1, e2)), ty1

        | (`And | `Or) as op ->
            check_ty ~loc:(loc pe1) [PBool] ty1;
            check_ty ~loc:(loc pe2) [PBool] ty2;
            EBinOp (op, (e1, e2)), TBool

        | (`Lt | `Le | `Gt | `Ge) as op ->
            check_ty ~loc:(loc pe1) [PInt; PString] ty1;
            check_ty ~loc:(loc pe2) [PInt; PString] ty2;
            check_ty_eq ~loc:(loc pe2) ~dst:ty1 ~src:ty2;
            EBinOp (op, (e1, e2)), TBool
      end

  
    | PECall ((nm, f) as nmf, args) ->
        let senv = tt_module env nm in

        let f =
          match Env.Procs.get senv (unloc f) with
          | None   -> error ~loc:(loc pe) env (UnknownProc (qunloc nmf))
          | Some f -> f in

        if List.length args <> List.length f.Env.psig then
          error ~loc:(loc pe) env InvalidArgCount;

        let args =
          List.map2 (fun e ty -> fst (tt_expr ~cty:(`Exact ty) env e))
          args f.Env.psig in

        (ECall (f.Env.pname, args), Type.strip f.Env.pret)

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
        error ~loc:(loc pe) env (InvalidType (ety, [cty])))
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
and tt_instr ?(rty : type_ option) (env : env) (i : pinstr) : block =
  match unloc i with
  | PSFail e ->
      let ety = tt_expr ~cty:(`Exact TString) env e in [IFail ety]

  | PSPass ->
      []

  | PSDecl ((x, ty), e) ->
      let ty = tt_type env ty in
      let _  = tt_expr ~cty:(`Exact ty) env e in
      []                        (* FIXME *)

  | PSAssign (_, _, e) ->
      let e = tt_expr env e in [IAssign (None, e)] (* FIXME *)

  | PSReturn None ->
      if Option.is_some rty then
        error ~loc:(loc i) env MustReturnAValue;
      [IReturn None]

  | PSReturn (Some e) -> begin
      let ety =
        match rty with
        | None    -> error ~loc:(loc i) env ExpectVoidReturn
        | Some ty -> tt_expr ~cty:(`Exact ty) env e
      in [IReturn (Some ety)]
    end

  | PSExpr e ->
      let ety = tt_expr env e in [IAssign (None, ety)]

  | PSIf ((c, bc), elifs, el) ->
      let ttif1 (c, bc) =
        let c  = fst (tt_expr ~cty:(`Exact TBool) env c) in
        let bc = tt_stmt ?rty env bc in
        (c, bc) in

      let cbc   = ttif1 (c, bc) in
      let elifs = List.map ttif1 elifs in
      let el    = Option.map (tt_stmt ?rty env) el in

      [IIf (cbc, elifs, el)]

  | PSFor ((x, (i, j), bc), el) ->
      let i = Option.map (tt_expr ~cty:(`Exact TInt) env %> fst) i in
      let j = fst (tt_expr ~cty:(`Exact TInt) env j) in

      let env, x = Env.Vars.bind env (unloc x, TInt) in

      let bc = tt_stmt ?rty env bc in
      let el = Option.map (tt_stmt ?rty env) el in

      [IFor ((x, (i, j), bc), el)]

  | PSWhile ((c, bc), el) ->
      let c  = fst (tt_expr ~cty:(`Exact TBool) env c) in
      let bc = tt_stmt ?rty env bc in
      let el = Option.map (tt_stmt ?rty env) el in

      [IWhile ((c, bc), el)]

  | PSDef _pf ->
      assert false              (* FIXME *)

(* -------------------------------------------------------------------- *)
and tt_stmt ?(rty : type_ option) (env : env) (s : pstmt) : block =
  List.flatten (List.map (tt_instr ?rty env) s)

(* -------------------------------------------------------------------- *)
and tt_module (env : env) (nm : pident list) =
  let rec resolve (env, pre) nm =
    match nm with
    | [] ->
        env

    | x :: nm -> begin
        match Env.Mod.get env (unloc x) with
        | None ->
            error ~loc:(loc x) env (UnknownModule (List.rev pre, unloc x))

        | Some env ->
            resolve (env, unloc x :: pre) nm

      end

  in resolve (env, []) nm

(* -------------------------------------------------------------------- *)
let tt_import (env : env) (_ : pimport) =
  env

(* -------------------------------------------------------------------- *)
let tt_tydecl (env : env) ((x, ty) : pident * pexpr) : env * tydecl =
  let ty = tt_type env ty in

  if Env.Types.exists env (unloc x) then
    error ~loc:(loc x) env (DuplicatedTypeName (unloc x));

  let env, name = Env.Types.bind env (unloc x, ty) in
  let aout = { tyd_name = name; tyd_body = ty } in

  (env, aout)

(* -------------------------------------------------------------------- *)
let tt_vardecl
  (env : env) ((x, ty), e : (pident * pexpr) * pexpr) : env * vardecl
 =
  let ty = tt_type env ty in
  let it = fst (tt_expr ~cty:(`Exact ty) env e) in

  if Env.Vars.exists env (unloc x) then
    error ~loc:(loc x) env (DuplicatedVarName (unloc x));

  let env, name = Env.Vars.bind env (unloc x, ty) in
  let aout = { vrd_name = name; vrd_type = ty; vrd_init = it; } in

  (env, aout)

(* -------------------------------------------------------------------- *)
(* FIXME: check for duplicate argument name *)
let tt_procdef
(env : env) (((f, fty), args, body) : pprocdef) : env * env procdef
=
  let fty  = tt_type env fty in
  let args = List.map (fun (x, xty) -> (unloc x, tt_type env xty)) args in
  let env1, args =
    List.fold_left_map (fun env (x, ty) ->
        let env, x = Env.Vars.bind env (x, ty) in (env, (x, ty)))
      env args in
  let body = tt_stmt ~rty:fty env1 body in

  let env, name = Env.Procs.bind env (unloc f) (List.map snd args, fty) in

  let aout = {
    prd_name = name;
    prd_args = args;
    prd_ret  = fty;
    prd_body = (env1, body);
  }

  in (env, aout)

(* -------------------------------------------------------------------- *)
let tt_topdecl1 (env : env) = function
  | PTImport info ->
      (tt_import  env info, [])

  | PTDef info ->
      let env, x = tt_procdef env info in (env, [TD_ProcDef x])

  | PTVar ((x, None), ty) ->
      let env, x = tt_tydecl  env (x, ty) in (env, [TD_TyDecl x])

  | PTVar ((x, Some ty), e) ->
      let env, x = tt_vardecl env ((x, ty), e) in (env, [TD_VarDecl x])

(* -------------------------------------------------------------------- *)
let tt_program (p : pspec) : env program =
  let env, prgm = List.fold_left_map tt_topdecl1 Env.empty p in
  (env, List.flatten prgm)
