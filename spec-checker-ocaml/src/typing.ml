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
  | PUnit | PBool  | PInt   | PString
  | PWord | PTuple | PArray

type etype = [`Exact of type_ | `Approx of ctype]

(* -------------------------------------------------------------------- *)
let byte_t = TWord `U8
let bytes_t = TArray (TWord `U8, None)
let get_bit = Ident.make "uintn_get_bit"
let get_bits = Ident.make "uintn_get_bits"
let int_t = TInt `Int
let nat_t = TInt `Nat
let pos_t = TInt `Pos
          
let stdlib = [
  (([],"array"), ([Some (`Approx PArray)], (fun [aty] -> aty), Ident.make "array"));
  ((["array"],"copy"), ([Some (`Approx PArray)], (fun [aty] -> aty), Ident.make "array_copy"));
  ((["array"],"create"), ([Some (`Approx PInt); None], (fun [aty;bty] -> TArray(bty, None)), Ident.make "array_create"));
  ((["array"],"length"), ([Some (`Approx PArray)], (fun [aty] -> nat_t), Ident.make "array_length"));
  ((["array"],"split_blocks"), ([Some (`Approx PArray);Some(`Exact int_t)], (fun [aty;bty] -> TTuple [TArray(aty,None);aty]), Ident.make "array_split_blocks"));
  ((["array"],"concat_blocks"), ([Some (`Approx PArray);Some(`Approx PArray)], (fun [TArray(aty,None);bty] -> aty), Ident.make "array_concat_blocks"));

  (([],"bytes"), ([Some (`Exact bytes_t)], (fun [aty] -> aty), Ident.make "bytes"));
  ((["bytes"],"copy"), ([Some (`Exact bytes_t)], (fun [aty] -> aty), Ident.make "bytes_copy"));
  ((["bytes"],"create"), ([Some (`Approx PInt); Some (`Exact byte_t)], (fun [aty;bty] -> bytes_t), Ident.make "bytes_create"));
  ((["bytes"],"length"), ([Some (`Exact bytes_t)], (fun [aty] -> nat_t), Ident.make "bytes_length"));
  ((["bytes"],"split_blocks"), ([Some (`Exact bytes_t);Some(`Approx PInt)], (fun [aty;bty] -> TTuple [TArray(bytes_t,None);bytes_t]), Ident.make "bytes_split_blocks"));
  ((["bytes"],"concat_blocks"), ([Some (`Exact (TArray(bytes_t,None)));Some(`Exact bytes_t)], (fun [TArray(aty,None);bty] -> aty), Ident.make "bytes_concat_blocks"));
  ((["bytes"],"to_uint32_be"), ([Some (`Exact bytes_t)], (fun [aty] -> TWord `U32), Ident.make "bytes_to_uint32_be"));
  ((["bytes"],"from_uint32_be"), ([Some (`Exact (TWord `U32))], (fun [aty] -> bytes_t), Ident.make "bytes_from_uint32_be"));
  ((["bytes"],"to_uint32s_le"), ([Some (`Exact bytes_t)], (fun [aty] -> TArray (TWord `U32,None)), Ident.make "bytes_to_uint32s_le"));
  ((["bytes"],"from_uint32s_le"), ([Some (`Exact (TArray (TWord `U32,None)))], (fun [aty] -> bytes_t), Ident.make "bytes_from_uint32s_le"));
  ((["bytes"],"to_uint32s_be"), ([Some (`Exact bytes_t)], (fun [aty] -> TArray (TWord `U32,None)), Ident.make "bytes_to_uint32s_be"));
  ((["bytes"],"from_uint32s_be"), ([Some (`Exact (TArray (TWord `U32,None)))], (fun [aty] -> bytes_t), Ident.make "bytes_from_uint32s_be"));
  ((["bytes"],"to_nat_le"), ([Some (`Exact bytes_t)], (fun [aty] -> nat_t), Ident.make "bytes_to_nat_le"));
  ((["bytes"],"from_nat_le"), ([Some (`Approx PInt); Some (`Approx PInt)], (fun [aty;bty] -> bytes_t), Ident.make "bytes_from_nat_le"));
  ((["bytes"],"to_uint128_le"), ([Some (`Exact bytes_t)], (fun [aty] -> TWord `U128), Ident.make "bytes_to_uint128_le"));
  ((["bytes"],"from_uint128_le"), ([Some (`Exact (TWord `U128))], (fun [aty] -> bytes_t), Ident.make "bytes_from_uint128_le"));

  (*  (([],"natmod"), ([Some (`Approx PInt); Some (`Approx PInt)], (fun [aty;bty] -> TInt (`Natm (EUInt Big_int.zero))), Ident.make "natmod"));*)
  ((["natmod"],"to_nat"), ([Some (`Approx PInt)], (fun [aty] -> nat_t), Ident.make "natmod_to_nat"));
  ((["natmod"],"to_int"), ([Some (`Approx PInt)], (fun [aty] -> int_t), Ident.make "natmod_to_int"));
  
  (*   (([],"uintn"), ([Some (`Approx PInt); Some (`Approx PInt)], (fun [aty;bty] -> TWord (`UN Big_int.zero)), Ident.make "uintn")); *)
  ((["uintn"],"to_int"), ([Some (`Approx PWord)], (fun [aty] -> nat_t), Ident.make "uintn_to_int"));
  ((["uintn"],"to_nat"), ([Some (`Approx PWord)], (fun [aty] -> nat_t), Ident.make "uintn_to_nat"));
  ((["uintn"],"get_bit"), ([Some (`Approx PWord);Some (`Approx PInt)], (fun [aty;bty] -> TWord `U1), Ident.make "uintn_get_bit"));
  ((["uintn"],"get_bits"), ([Some (`Approx PWord);Some (`Approx PInt);Some (`Approx PInt)], (fun [aty;bty;cty] -> TWord (`UN Big_int.zero)), Ident.make "uintn_get_bits"));
  ((["uintn"],"rotate_left"), ([Some (`Approx PWord); Some (`Approx PInt)], (fun [aty;bty] -> aty), Ident.make "uintn_rotate_left"));
  ((["uintn"],"rotate_right"), ([Some (`Approx PWord); Some (`Approx PInt)], (fun [aty;bty] -> aty), Ident.make "uintn_rotate_right"));

  ((["result"],"retval"), ([None], (fun [aty] -> TResult aty), Ident.make "result_retval"));
  ((["result"],"error"),  ([Some (`Exact TString)], (fun [aty] -> TResult TString), Ident.make "result_error"));

  ]

(* -------------------------------------------------------------------- *)
module StdLib : sig
  module Array : sig
    val copy          : ident
    val create        : ident
    val length        : ident
    val split_blocks  : ident
    val concat_blocks : ident
  end

  module UIntn : sig
    val rotate_left  : ident
    val rotate_right : ident
  end

  module Bytes : sig
    val copy            : ident
    val to_uint32s_le   : ident
    val from_uint32s_le : ident
    val to_nat_le   : ident
    val from_nat_le : ident
  end
end = struct
  module Array = struct
    let create        = Ident.make "array.create"
    let copy          = Ident.make "array.copy"
    let length        = Ident.make "array.length"
    let split_blocks  = Ident.make "array.split_blocks"
    let concat_blocks = Ident.make "array.concat_blocks"
  end

  module UIntn = struct
    let rotate_left  = Ident.make "uintn.rotate_left"
    let rotate_right = Ident.make "uintn.rotate_right"
  end

  module Bytes = struct
    let copy            = Ident.make "bytes.copy"
    let to_uint32s_le   = Ident.make "bytes.to_uint32s_le"
    let from_uint32s_le = Ident.make "bytes.from_uint32s_le"
    let to_nat_le   = Ident.make "bytes.to_nat_le"
    let from_nat_le = Ident.make "bytes.from_nat_le"
  end
end

(* -------------------------------------------------------------------- *)
module Env : sig
  type env
  type tdecl = { tname : ident; tdef  : type_; }
  type vdecl = { vname : ident; vtype : type_; vrawty : type_; }
  type pdecl = { pname : ident; psig  : type_ list; pret : type_; }

  val empty : env

  module Mod : sig
    val get   : env -> symbol -> env option
    val getnm : env -> symbol list -> env option
    val bind  : env -> symbol -> env -> env
  end

  module Types : sig
    val compat : env -> type_ -> type_ -> bool
    val approx : env -> type_ -> ctype -> bool

    val exists : env -> symbol -> bool
    val get    : env -> symbol -> tdecl option
    val bind   : env -> symbol * type_ -> env * ident
    val unfold : env -> qsymbol -> type_ option
    val hred   : env -> type_ -> type_
    val inline : env -> type_ -> type_
  end

  module Vars : sig
    val exists : env -> symbol -> bool
    val get    : env -> symbol -> vdecl option
    val bind   : env -> symbol * type_ -> env * ident
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
    e_mods  : env   Mstr.t;
  }

  let dtypes = [
    ("bool"     , TBool      );
    ("int"      , TInt  `Int );
    ("nat"      , TInt  `Nat );
    ("string"   , TString    );
    ("nat_t"    , TInt  `Nat );
    ("pos_t"    , TInt  `Pos );
    ("bit_t"    , TWord `U1  );
    ("uint8_t"  , TWord `U8  );
    ("uint16_t" , TWord `U16 );
    ("uint32_t" , TWord `U32 );
    ("uint64_t" , TWord `U64 );
    ("uint128_t", TWord `U128);
    ("vlbytes_t", TArray (TWord `U8, None));
  ]

  let dprocs = [
    ("nat"    , [TInt `Int], TInt  `Pos );
    ("pos"    , [TInt `Int], TInt  `Nat );
    ("bit"    , [TInt `Int], TWord `U1  );
    ("uint8"  , [TInt `Int], TWord `U8  );
    ("uint16" , [TInt `Int], TWord `U16 );
    ("uint32" , [TInt `Int], TWord `U32 );
    ("uint64" , [TInt `Int], TWord `U64 );
    ("uint128", [TInt `Int], TWord `U128);
  ]

  module Mod = struct
    let get (env : env) (x : symbol) =
      Mstr.Exceptionless.find x env.e_mods

    let rec getnm (env : env) (nm : symbol list) =
      match nm with [] -> Some env | x :: nm ->
        Option.bind (get env x) (fun env -> getnm env nm)

    let bind (env : env) (x : symbol) (mod_ : env) =
      { env with e_mods = Mstr.add x mod_ env.e_mods }
  end

  module Types = struct
    let get (env : env) (x : symbol) =
      Mstr.Exceptionless.find x env.e_types

    let exists (env : env) (x : symbol) =
      Option.is_some (get env x)

    let bind (env : env) ((x, ty) : symbol * type_) =
      let decl = { tname = Ident.make x; tdef = ty } in
      let env  = { env with e_types = Mstr.add x decl env.e_types } in
      (env, decl.tname)

    let unfold (env : env) ((nm, x) : qsymbol) =
      Option.map
        (fun tdecl -> tdecl.tdef)
        (Option.bind (Mod.getnm env nm) (fun env -> get env x))

    let hred (env : env) =
      let rec hred (ty : type_) =
        match ty with
        | TNamed qs -> hred (Option.get (unfold env qs))
        | _ -> ty

      in fun ty -> hred ty

    let inline (env : env) =
      let rec inline (ty : type_) =
        match ty with
        | TNamed qs       -> inline (Option.get (unfold env qs))
        | TTuple tl       -> TTuple (List.map inline tl)
        | TArray (t, s)   -> TArray (inline t,s)
        | TRefined (t, s) -> TRefined (inline t,s)
        | TResult t       -> TResult (inline t)
        | _               -> ty

      in fun ty -> inline ty

    let compat (env : env) =
      let rec compat (ty1 : type_) (ty2 : type_) : bool =
        match ty1, ty2 with
        | TUnit  , TUnit
        | TBool  , TBool
        | TInt _ , TInt _
        | TString, TString -> true

        | TWord (`UN n1), TWord (`UN n2)  ->
            Big_int.compare_big_int n1 n1 = 0

        | TWord sz1, TWord sz2  ->
            sz1 = sz2

        | TTuple tys1, TTuple tys2
              when List.length tys1 = List.length tys2
          -> List.for_all2 compat tys1 tys2

        | TArray (aty1, _), TArray (aty2, _) -> (* FIXME *)
            compat aty1 aty2

        | TRange _, _ -> compat (TInt `Nat) ty2
        | _, TRange _ -> compat (TInt `Nat) ty1

        | TRefined (ty1, _), _ ->
            compat ty1 ty2

        | _, TRefined (ty2, _) ->
            compat ty1 ty2

        | TNamed q1, TNamed q2 when QSymbol.equal q1 q2 ->
            true

        | TNamed q, _ ->
            compat (Option.get (unfold env q)) ty2

        | _, TNamed q ->
            compat ty1 (Option.get (unfold env q))

        | TResult _, TResult _ ->
            true
        | _, _ ->
            false

    in fun ty1 ty2 -> compat ty1 ty2

    let approx (env : env) =
      let rec approx (ty : type_) (cty : ctype) =
        match ty, cty with
        | TUnit     , PUnit    -> true
        | TBool     , PBool    -> true
        | TInt _    , PInt     -> true
        | TString   , PString  -> true
        | TWord    _, PWord    -> true
        | TArray   _, PArray   -> true
        | TTuple   _, PTuple   -> true
        | TRange   _, PInt     -> true
  
        | TRefined (ty, _), _ ->
            approx ty cty

        | TNamed q, _ ->
            approx (Option.get (unfold env q)) cty
  
        | _, _ -> false

      in fun ty cty -> approx ty cty

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
    let env = {
      e_types = Mstr.empty;
      e_vars  = Mstr.empty;
      e_procs = Mstr.empty;
      e_mods  = Mstr.empty;
    } in

    let env =
      List.fold_left
        (fun env xty -> fst (Types.bind env xty)) env dtypes in

    let env =
      List.fold_left
        (fun env (f, sg, re) ->
          fst (Procs.bind env f (sg, re))) env dprocs in

    env
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
  | CannotUnpack
  | DoNotSupportSlicing of [`LValue | `RValue]
  | MisplacedVarDecl
  | MustReturnAValue
  | UIntConstantExpected
  | ExpectVoidReturn
  | InvalidTypeExpr
  | InvalidArgCount
  | InvalidTypeCtor    of symbol
  | InvalidType        of type_ * etype list
  | InvalidLValueExpr
  | UnsupportedAnnotation

(* -------------------------------------------------------------------- *)
let pp_tyerror fmt (error : tyerror) =
  let pp_qsymbol fmt (nm, x) =
    Format.fprintf fmt "%s" (String.concat "." (nm @ [x])) in

  match error with
  | CannotInferType ->
      Format.fprintf fmt "cannot infer type of this expression"

  | CannotUnpack ->
      Format.fprintf fmt "cannot unpack"

  | DoNotSupportSlicing `RValue ->
      Format.fprintf fmt "this expression cannot be indexed/sliced"

  | DoNotSupportSlicing `LValue ->
      Format.fprintf fmt "this expression cannot be indexed/sliced (in lvalues)"

  | MisplacedVarDecl ->
      Format.fprintf fmt
        "variable declarations can only occur at beginning of procs"

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

  | UIntConstantExpected ->
      Format.fprintf fmt "unsigned integer constant expected"

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

  | InvalidLValueExpr ->
      Format.fprintf fmt "invalid lvalue expression"

  | UnsupportedAnnotation ->
      Format.fprintf fmt "unsupported annotation"

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
let check_ty ~loc env (etys : ctype list) (ty : type_) =
  if not (List.exists (Env.Types.approx env ty) etys) then
    error ~loc env (InvalidType (ty, List.map (fun ty -> `Approx ty) etys))

let check_ty_compat ~loc env ~src ~dst =
  if not (Env.Types.compat env src dst) then
    error ~loc env (InvalidType (src, [`Exact dst]))

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

  | "natmod_t", [sz] ->
      let sz,_ = tt_expr ~cty:(`Approx PInt) env sz in
      TInt (`Natm sz)

  | "uintn_t", [sz] ->
      let sz = tt_cint env sz in
      TWord (`UN sz)

  | "array_t", [ty; sz] ->
      let sz = tt_cint env sz in
      let ty = tt_type env ty in
      TArray (ty, Some sz)

  | "vlarray_t", [ty] ->
      let ty = tt_type env ty in
      TArray (ty, None)

  | "result_t", [ty] ->
      let ty = tt_type env ty in
      TResult (ty)
      
  | "bytes_t", [sz] ->
      let sz = tt_cint env sz in
      TArray (TWord `U8, Some sz)

  | ("refine" | "refine_t"), [pty; pe] ->
     (match unloc pe with
      | PEFun ([{ pl_data = x }], pr) ->
        let ty = tt_type env pty in
        let env1, name = Env.Vars.bind env (x, ty) in
        let r = fst (tt_expr ~cty:(`Exact TBool) env1 pr) in
        TRefined (ty, EFun ([name], r))

     | _ -> error ~loc:(loc pe) env InvalidTypeExpr)

  | "tuple2_t", [ty1; ty2] ->
      let ty1 = tt_type env ty1 in
      let ty2 = tt_type env ty2 in
      TTuple [ty1; ty2]

  | "tuple3_t", [ty1; ty2; ty3] ->
      let ty1 = tt_type env ty1 in
      let ty2 = tt_type env ty2 in
      let ty3 = tt_type env ty3 in
      TTuple [ty1; ty2; ty3]

  | "tuple_t", tyl ->
      let tyl = List.map (fun t -> tt_type env t) tyl in
      TTuple tyl

  | tn, [] -> TNamed ([],tn)
(*
     begin
      match Env.Types.get env (unloc x) with
      | None -> error ~loc:(loc x) env (UnknownTypeName ([], unloc x))
      | Some decl -> decl.Env.tdef
    end
 *)

  | _ -> error ~loc:(loc x) env (InvalidTypeCtor (unloc x))

(* -------------------------------------------------------------------- *)
and tt_cint (env : env) (e : pexpr) =
  match fst (tt_expr ~cty:(`Approx PInt) env e) with
  | EUInt i -> i
  | _       -> error ~loc:(loc e) env UIntConstantExpected

(* -------------------------------------------------------------------- *)
and tt_lvalue ?(cty : etype option) (env : env) (pe : plvalue) =
  let e, ety =
    match unloc pe with
    | PEVar ((nm, x) as nmx) -> begin
        let senv = tt_module env nm in

        match Env.Vars.get senv (unloc x) with
        | None -> error ~loc:(loc pe) env (UnknownVar (qunloc nmx))
        | Some x -> (LVar x.Env.vname, x.Env.vrawty)
      end

    | PETuple ([], _) ->
        (LTuple [], TUnit)

    | PETuple ([pe], _) ->
        tt_lvalue env pe

    | PETuple (pes, _) ->
        let es, tys = List.split (List.map (tt_lvalue env) pes) in
        (LTuple es, TTuple tys) 

    | PEGet (pl, ps) ->
        let l, lty = tt_lvalue ~cty:(`Approx PArray) env pl in   
        let s      = tt_slice env ps in
        let ty     =
          match Env.Types.inline env lty, s with
          | TArray (ty, _), `One _   -> ty
          | TArray _      , `Slice _ -> lty

          | _, _ ->
              error ~loc:(loc pe) env (DoNotSupportSlicing `LValue)

        in (LGet (l, s), ty)

    | _ ->
        error ~loc:pe.pl_loc env InvalidLValueExpr
  in

  Option.may (fun (cty : etype) ->
    let compat =
      match cty with
      | `Approx cty ->
          Env.Types.approx env ety cty
      | `Exact  cty ->
          Env.Types.compat env ety cty
    in
      if not compat then
        error ~loc:(loc pe) env (InvalidType (ety, [cty])))
    cty;

  (e, ety)

(* -------------------------------------------------------------------- *)
and tt_expr ?(cty : etype option) (env : env) (pe : pexpr) =
  let check_ty = check_ty env in
  let check_ty_compat = check_ty_compat env in

  let e, ety =
    match unloc pe with
    | PEVar ((nm, x) as nmx) -> begin
        let senv = tt_module env nm in

        match Env.Vars.get senv (unloc x) with
        | None -> error ~loc:(loc pe) env (UnknownVar (qunloc nmx))
        | Some x -> (EVar x.Env.vname, x.Env.vrawty)
      end

    | PEBool   b -> (EBool   b, TBool  )
    | PEUInt   i -> (EUInt   i, TInt `Int )
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
        check_ty_compat ~loc:(loc pe) ~dst:ty1 ~src:ty2;
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
            EUniOp (op, e), TInt `Int

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
            check_ty_compat ~loc:(loc pe2) ~dst:ty1 ~src:ty2;
            EBinOp (op, (e1, e2)), ty1

        | `Pow as op ->
            check_ty ~loc:(loc pe1) [PWord; PInt] ty1;
            check_ty ~loc:(loc pe2) [PInt ] ty2;
            EBinOp (op, (e1, e2)), ty1

        | (`BAnd | `BOr | `BXor) as op ->
            check_ty ~loc:(loc pe1) [PWord] ty1;
            check_ty ~loc:(loc pe2) [PWord] ty2;
            check_ty_compat ~loc:(loc pe2) ~dst:ty1 ~src:ty2;
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
            check_ty_compat ~loc:(loc pe2) ~dst:ty1 ~src:ty2;
            EBinOp (op, (e1, e2)), TBool
      end

    | PECall (nmf, [x;y]) when (qunloc nmf) = ([],"uintn") ->
       let xe, _ = tt_expr ~cty:(`Approx PInt) env x in
       let ye, _ = tt_expr ~cty:(`Approx PInt) env y in
       let n = tt_cint env y in
       (ECall (Ident.make("uintn"), [xe;ye]), TWord (`UN n))

    | PECall (nmf, [x;y]) when (qunloc nmf) = ([],"natmod") ->
       let xe, _ = tt_expr ~cty:(`Approx PInt) env x in
       let ye, _ = tt_expr ~cty:(`Approx PInt) env y in
       (ECall (Ident.make("natmod"), [xe;ye]), TInt (`Natm ye))

    | PECall (nmf, args) when List.mem_assoc (qunloc nmf) stdlib ->
        let exp, rty, name = List.assoc (qunloc nmf) stdlib in

        if List.length args <> List.length exp then
          error ~loc:(loc pe) env InvalidArgCount;
        let args, tys =
             List.combine args exp
          |> List.map (fun (e, ty) -> tt_expr ?cty:ty env e)
          |> List.split in
        (ECall (name, args), rty tys)
        
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
        let e, ty = tt_expr env pe in   
        let s     = tt_slice env ps in
        let e, ty =
          match Env.Types.inline env ty, s with
          | TWord _, `One i ->
              ECall(get_bit, [e; i]), TWord `U1

          | TWord _, `Slice (s,f) ->
              ECall(get_bits, [e; s; f]),TWord (`UN Big_int.zero)

          | TArray (ty,_), `One _ ->
              EGet(e, s),ty

          | TArray (_,_), `Slice _ ->
              EGet(e, s), ty

          | _ -> error ~loc:(loc pe) env (DoNotSupportSlicing `RValue)

        in (e, ty)
  in

  Option.may (fun (cty : etype) ->
    let compat =
      match cty with
      | `Approx cty ->
          Env.Types.approx env ety cty
      | `Exact  cty ->
          Env.Types.compat env ety cty
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
and tt_instr ?(rty : type_ option) (env : env) (i : pinstr) : env * block =
  match unloc i with
  | PSFail e ->
      let ety = tt_expr ~cty:(`Exact TString) env e in 
      (env, [IFail ety])

  | PSPass ->
      (env, [])

  | PSVarDecl (_, None) ->
      (env, []) 

  | PSVarDecl ((pi, pity), Some e) ->
     let ity = tt_type env pity in
     let e, te = tt_expr env ~cty:(`Exact ity) e in 
     let l, _  =                (* FIXME *)
       (match Env.Vars.get env (unloc pi) with
        | None -> error ~loc:(loc pi) env (UnknownVar ([], unloc pi))
        | Some x -> (LVar x.Env.vname, x.Env.vrawty))

     in (env, [IAssign (Some (l, `Plain), (e, te))])

  | PSAssign (pv, pop, pe) ->
     let e, te = tt_expr env pe in 
     let l, tl = tt_lvalue env pv in
     check_ty_compat env ~loc:(loc pe) ~src:te ~dst:tl;
     (env, [IAssign (Some (l, pop), (e, te))])

  | PSReturn None ->
      if Option.is_some rty then
        error ~loc:(loc i) env MustReturnAValue;
      (env, [IReturn None])

  | PSReturn (Some e) -> begin
      let ety =
        match rty with
        | None    -> error ~loc:(loc i) env ExpectVoidReturn
        | Some ty ->   tt_expr ~cty:(`Exact ty) env e
      in (env, [IReturn (Some ety)])
    end

  | PSExpr e ->
      let ety = tt_expr env e in (env, [IAssign (None, ety)])

  | PSIf ((c, bc), elifs, el) ->
      let ttif1 env (c, bc) =
        let c  = fst (tt_expr ~cty:(`Exact TBool) env c) in
        let env, bc = tt_stmt ?rty env bc in
        env, (c, bc) in

      let env, cbc   = ttif1 env (c, bc) in
      let env, elifs = List.fold_left_map ttif1 env elifs in
      let env, el    =
        fst_map
          (Option.default env)
          (Option.split (Option.map (tt_stmt ?rty env) el)) in

      (env, [IIf (cbc, elifs, el)])

  | PSFor (((x, xty), (i, j), bc), el) ->
      let i = Option.map (tt_expr ~cty:(`Approx PInt) env %> fst) i in
      let j = fst (tt_expr ~cty:(`Approx PInt) env j) in

      Option.may (fun xty ->
        let ty = tt_type env xty in
        check_ty ~loc:(loc x) env [PInt] ty)
      xty;

      let env, x = Env.Vars.bind env (unloc x, TInt `Int) in

      let env, bc = tt_stmt ?rty env bc in
      let env, el =
        fst_map
          (Option.default env)
          (Option.split (Option.map (tt_stmt ?rty env) el)) in

      (env, [IFor ((x, (i, j), bc), el)])

  | PSWhile ((c, bc), el) ->
      let c       = fst (tt_expr ~cty:(`Exact TBool) env c) in
      let env, bc = tt_stmt ?rty env bc in
      let env, el =
        fst_map
          (Option.default env)
          (Option.split (Option.map (tt_stmt ?rty env) el)) in

      (env, [IWhile ((c, bc), el)])

  | PSDef pf ->
      (* FIXME *)
      let env, _ = tt_procdef env pf in (env, [])

(* -------------------------------------------------------------------- *)
and tt_stmt ?(rty : type_ option) (env : env) (s : pstmt) : env * block =
  let env, blocks = List.fold_left_map (tt_instr ?rty) env s in
  env, List.flatten blocks

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
and tt_import (env : env) (_ : pimport) =
  env

(* -------------------------------------------------------------------- *)
and tt_tydecl (env : env) ((x, ty) : pident * pexpr) : env * tydecl =
  let ty = tt_type env ty in

  if Env.Types.exists env (unloc x) then
    error ~loc:(loc x) env (DuplicatedTypeName (unloc x));

  let env, name = Env.Types.bind env (unloc x, ty) in
  let aout = { tyd_name = name; tyd_body = ty } in

  let env = begin
    match Type.strip ty with
    | TArray (aty, _) ->
        fst (Env.Procs.bind env (unloc x) ([TArray (aty, None)], ty))

    | _ -> env
  end

  in (env, aout)

(* -------------------------------------------------------------------- *)
and tt_vardecl
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
and tt_annotation (env : env) (att : pexpr) : ident * expr list =
  match fst (tt_expr env att) with
  | EVar x ->
      (x, [])

  | ECall (x, args) ->
      (x, args)

  | _ ->
      error ~loc:(loc att) env UnsupportedAnnotation

(* -------------------------------------------------------------------- *)
(* FIXME: check for duplicate argument name *)
and tt_procdef (env : env) (pf : pprocdef) : env * env procdef =
  let {
    pf_name  = f   ;
    pf_att   = fatt;
    pf_retty = fty ;
    pf_args  = args;
    pf_body  = body;
  } = pf in

  let fatt = List.map (tt_annotation env) fatt in

  let lv =
    let rec aux lv instr =
      match unloc instr with
      | PSVarDecl (xty, _) -> xty :: lv
      | PSDef _ -> lv           (* FIXME *)
      | _ -> AstUtils.pifold aux lv instr
    in AstUtils.psfold aux [] body in

  let fty  = tt_type env fty in
  let args = List.map (fun (x, xty) -> (unloc x, tt_type env xty)) args in
  let env1, args =
    List.fold_left_map (fun env (x, ty) ->
        let env, x = Env.Vars.bind env (x, ty) in (env, (x, ty)))
      env args in

  let env1 = List.fold_left (fun env (x, ty) ->
    let ty = tt_type env ty in
    fst (Env.Vars.bind env (unloc x, ty))) env1 lv in

  let body = snd (tt_stmt ~rty:fty env1 body) in

  let env, name = Env.Procs.bind env (unloc f) (List.map snd args, fty) in

  let aout = {
    prd_name = name;
    prd_att  = fatt;
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

  | PTTypeAlias (x, ty) ->
      let env, x = tt_tydecl  env (x, ty) in (env, [TD_TyDecl x])

  | PTVarDecl ((x, ty), e) ->
      let env, x = tt_vardecl env ((x, ty), e) in (env, [TD_VarDecl x])

(* -------------------------------------------------------------------- *)
let tt_program (p : pspec) : env program =
  let env, prgm = List.fold_left_map tt_topdecl1 Env.empty p in
  (env, List.flatten prgm)
