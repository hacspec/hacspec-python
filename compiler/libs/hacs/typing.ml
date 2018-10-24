(* -------------------------------------------------------------------- *)
open Core
open Location
open Syntax
open Ast

(* -------------------------------------------------------------------- *)
let nmunloc (nm : pident list) : symbol list =
  List.map unloc nm

(* -------------------------------------------------------------------- *)
let qunloc ((nm, x) : pqident) : qsymbol =
  (List.map unloc nm, unloc x)

(* -------------------------------------------------------------------- *)
type ctype =
  | PUnit | PBool  | PInt   | PString
  | PWord | PTuple | PArray

type etype = [`Exact of type_ | `Approx of ctype]

(* -------------------------------------------------------------------- *)
let byte_t   = tword8
let bytes_t  = TArray (tword8, None)
let get_bit  = Ident.make "uintn_get_bit"
let get_bits = Ident.make "uintn_get_bits"
let int_t    = TInt `Int
let nat_t    = TInt `Nat
let pos_t    = TInt `Pos
          
let stdlib =
  let fs1 f = function [x      ] -> f x     | _ -> assert false
  and fs2 f = function [x; y   ] -> f x y   | _ -> assert false
  and fs3 f = function [x; y; z] -> f x y z | _ -> assert false in

 [
  (([],"array"), ([Some (`Approx PArray)], (fs1 (fun aty -> aty)), Ident.make "array"));
  ((["array"],"copy"), ([Some (`Approx PArray)], (fs1 (fun aty -> aty)), Ident.make "array_copy"));
  ((["array"],"create"), ([Some (`Approx PInt); None], (fs2 (fun _aty bty -> TArray(bty, None))), Ident.make "array_create"));
  ((["array"],"length"), ([Some (`Approx PArray)], (fs1 (fun _aty -> nat_t)), Ident.make "array_length"));
  ((["array"],"split_blocks"), ([Some (`Approx PArray);Some(`Exact int_t)], (fs2 (fun aty _bty -> TTuple [TArray(aty,None);aty])), Ident.make "array_split_blocks"));
  ((["array"],"concat_blocks"), ([Some (`Approx PArray);Some(`Approx PArray)],
      (fs2 (fun aty _bty -> match aty with TArray(aty,None) -> aty | _ -> assert false)),
      Ident.make "array_concat_blocks"));

  (([],"bytes"), ([Some (`Exact bytes_t)], (fs1 (fun aty -> aty)), Ident.make "bytes"));
  ((["bytes"],"copy"), ([Some (`Exact bytes_t)], (fs1 (fun aty -> aty)), Ident.make "bytes_copy"));
  ((["bytes"],"create"), ([Some (`Approx PInt); Some (`Exact byte_t)], (fs2 (fun _aty _bty -> bytes_t)), Ident.make "bytes_create"));
  ((["bytes"],"length"), ([Some (`Exact bytes_t)], (fs1 (fun _aty -> nat_t)), Ident.make "bytes_length"));
  ((["bytes"],"split_blocks"), ([Some (`Exact bytes_t);Some(`Approx PInt)], (fs2 (fun _aty _bty -> TTuple [TArray(bytes_t,None);bytes_t])), Ident.make "bytes_split_blocks"));
  ((["bytes"],"concat_blocks"), ([Some (`Exact (TArray(bytes_t,None)));Some(`Exact bytes_t)],
      (fs2 (fun aty _bty -> match aty with TArray(aty,None) -> aty | _ -> assert false)),
      Ident.make "bytes_concat_blocks"));
  ((["bytes"],"to_uint32_be"), ([Some (`Exact bytes_t)], (fs1 (fun _aty -> tword32)), Ident.make "bytes_to_uint32_be"));
  ((["bytes"],"from_uint32_be"), ([Some (`Exact (tword32))], (fs1 (fun _aty -> bytes_t)), Ident.make "bytes_from_uint32_be"));
  ((["bytes"],"to_uint32s_le"), ([Some (`Exact bytes_t)], (fs1 (fun _aty -> TArray (tword32,None))), Ident.make "bytes_to_uint32s_le"));
  ((["bytes"],"from_uint32s_le"), ([Some (`Exact (TArray (tword32,None)))], (fs1 (fun _aty -> bytes_t)), Ident.make "bytes_from_uint32s_le"));
  ((["bytes"],"to_uint32s_be"), ([Some (`Exact bytes_t)], (fs1 (fun _aty -> TArray (tword32,None))), Ident.make "bytes_to_uint32s_be"));
  ((["bytes"],"from_uint32s_be"), ([Some (`Exact (TArray (tword32,None)))], (fs1 (fun _aty -> bytes_t)), Ident.make "bytes_from_uint32s_be"));
  ((["bytes"],"to_nat_le"), ([Some (`Exact bytes_t)], (fs1 (fun _aty -> nat_t)), Ident.make "bytes_to_nat_le"));
  ((["bytes"],"from_nat_le"), ([Some (`Approx PInt); Some (`Approx PInt)], (fs2 (fun _aty _bty -> bytes_t)), Ident.make "bytes_from_nat_le"));
  ((["bytes"],"to_uint128_le"), ([Some (`Exact bytes_t)], (fs1 (fun _aty -> tword128)), Ident.make "bytes_to_uint128_le"));
  ((["bytes"],"from_uint128_le"), ([Some (`Exact (tword128))], (fs1 (fun _aty -> bytes_t)), Ident.make "bytes_from_uint128_le"));
  ((["bytes"],"to_uint128_be"), ([Some (`Exact bytes_t)], (fs1 (fun _aty -> tword128)), Ident.make "bytes_to_uint128_be"));
  ((["bytes"],"from_uint128_be"), ([Some (`Exact (tword128))], (fs1 (fun _aty -> bytes_t)), Ident.make "bytes_from_uint128_be"));

  (*  (([],"natmod"), ([Some (`Approx PInt); Some (`Approx PInt)], (fun [aty;bty] -> TInt (`Natm (EUInt Big_int.zero))), Ident.make "natmod"));*)
  ((["natmod"],"to_nat"), ([Some (`Approx PInt)], (fs1 (fun _aty -> nat_t)), Ident.make "natmod_to_nat"));
  ((["natmod"],"to_int"), ([Some (`Approx PInt)], (fs1 (fun _aty -> int_t)), Ident.make "natmod_to_int"));
  
  (*   (([],"uintn"), ([Some (`Approx PInt); Some (`Approx PInt)], (fun [aty;bty] -> TWord (`UN Big_int.zero)), Ident.make "uintn")); *)
  ((["uintn"],"to_int"), ([Some (`Approx PWord)], (fs1 (fun _aty -> nat_t)), Ident.make "uintn_to_int"));
  ((["uintn"],"to_nat"), ([Some (`Approx PWord)], (fs1 (fun _aty -> nat_t)), Ident.make "uintn_to_nat"));
  ((["uintn"],"get_bit"), ([Some (`Approx PWord);Some (`Approx PInt)], (fs2 (fun _aty _bty -> tword1)), Ident.make "uintn_get_bit"));
  ((["uintn"],"get_bits"), ([Some (`Approx PWord);Some (`Approx PInt);Some (`Approx PInt)], (fs3 (fun _aty _bty _cty -> TWord Big_int.zero)), Ident.make "uintn_get_bits"));
  ((["uintn"],"rotate_left"), ([Some (`Approx PWord); Some (`Approx PInt)], (fs2 (fun aty _bty -> aty)), Ident.make "uintn_rotate_left"));
  ((["uintn"],"rotate_right"), ([Some (`Approx PWord); Some (`Approx PInt)], (fs2 (fun aty _bty -> aty)), Ident.make "uintn_rotate_right"));

  ((["result"],"retval"), ([None], (fs1 (fun aty -> TResult aty)), Ident.make "result_retval"));
  ((["result"],"error"),  ([Some (`Exact TString)], (fs1 (fun _aty -> TResult TString)), Ident.make "result_error"));

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
  type pdecl = { pname : ident; psig  : hotype list; pret : type_; }

  val empty0 : env
  val empty  : env
  val cast_funs : ((string list * string) * (ctype list * type_ * Ast.Ident.ident)) list
    
  module Mod : sig
    val get    : env -> symbol -> env option
    val getnm  : env -> symbol list -> env option
    val bind   : env -> symbol -> env -> env
    val bindnm : env -> symbol list -> env -> env
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
    val get  : env -> symbol -> pdecl option
    val bind : env -> symbol -> hotype list * type_ -> env * ident
  end
end = struct
  type tdecl = { tname : ident; tdef  : type_; }
  type vdecl = { vname : ident; vtype : type_; vrawty : type_; }
  type pdecl = { pname : ident; psig  : hotype list; pret : type_; }

  type env = {
    e_types : tdecl Mstr.t;
    e_vars  : vdecl Mstr.t;
    e_procs : pdecl Mstr.t;
    e_mods  : env   Mstr.t;
  }

  let empty0 = {
    e_types = Mstr.empty;
    e_vars  = Mstr.empty;
    e_procs = Mstr.empty;
    e_mods  = Mstr.empty;
  }

  let dtypes = [
    ("bool"     , TBool     );
    ("int"      , TInt `Int );
    ("nat"      , TInt `Nat );
    ("string"   , TString   );
    ("nat_t"    , TInt `Nat );
    ("pos_t"    , TInt `Pos );
    ("bit_t"    , tword1    );
    ("uint8_t"  , tword8    );
    ("uint16_t" , tword16   );
    ("uint32_t" , tword32   );
    ("uint64_t" , tword64   );
    ("uint128_t", tword128  );
    ("vlbytes_t", TArray (tword8, None));
  ]

  let cast_funs = [
    (([],"nat")  , ([PInt],TInt `Pos, Ident.make "nat"));
    (([],"pos")  , ([PInt],TInt `Nat, Ident.make "pos"));
    (([],"bit")  , ([PWord;PInt],tword1, Ident.make "bit"   ));
    (([],"uint8"), ([PWord;PInt],tword8, Ident.make "uint8" ));
    (([],"uint16") , ([PWord;PInt],tword16, Ident.make "uint16"  ));
    (([],"uint32") , ([PWord;PInt],tword32, Ident.make "uint32"  ));
    (([],"uint64") , ([PWord;PInt], tword64, Ident.make "uint64"  ));
    (([],"uint128"), ([PWord;PInt], tword128, Ident.make "uint128" ));
    ]
          
  let dprocs = [
    ("nat"    , [TInt `Int], TInt `Pos);
    ("pos"    , [TInt `Int], TInt `Nat);
    ("bit"    , [TInt `Int], tword1   );
    ("uint8"  , [TInt `Int], tword8   );
    ("uint16" , [TInt `Int], tword16  );
    ("uint32" , [TInt `Int], tword32  );
    ("uint64" , [TInt `Int], tword64  );
    ("uint128", [TInt `Int], tword128 );
  ]

  module Mod = struct
    let get (env : env) (x : symbol) =
      Mstr.Exceptionless.find x env.e_mods

    let rec getnm (env : env) (nm : symbol list) =
      match nm with [] -> Some env | x :: nm ->
        Option.bind (get env x) (fun env -> getnm env nm)

    let bind (env : env) (x : symbol) (mod_ : env) =
      { env with e_mods = Mstr.add x mod_ env.e_mods }

    let rec bindnm (env : env) (nm : symbol list) (mod_ : env) =
      match nm with
      | []      -> assert false
      | [x]     -> bind env x mod_
      | x :: nm ->
          { env with e_mods =
              Mstr.modify_opt x (fun senv ->
                  Some (bindnm (Option.default empty0 senv) nm mod_))
                env.e_mods }
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

        | TWord n1, TWord n2  ->
            Big_int.eq_big_int n1 n2

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

    let bind (env : env) (f : symbol) ((sig_, ret) : hotype list * type_) =
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
          let sg = List.map hotype1  sg in
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
  | MisplacedProcDef
  | MustReturnAValue
  | UIntConstantExpected
  | ExpectVoidReturn
  | InvalidTypeExpr
  | InvalidArgCount
  | InvalidTypeCtor    of symbol
  | InvalidType        of type_ * etype list
  | InvalidLValueExpr
  | UnsupportedAnnotation
  | ProcNameExpected
  | InvalidHOApplication

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

  | MisplacedProcDef ->
      Format.fprintf fmt
        "inner procedures definitions can only occur at beginning of procs"

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

  | ProcNameExpected ->
      Format.fprintf fmt
        "only procedure names are allowed for second-order argument"

  | InvalidHOApplication ->
      Format.fprintf fmt "invalid second-order application"

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
      TWord sz

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
      TArray (tword8, Some sz)

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
and tt_hotype (env : env) ((sg, ty) : photype) =
  let sg = List.map (tt_type env) sg in
  let ty = tt_type env ty in
  (sg, ty)

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
       (ECall (Ident.make("uintn"), [`Expr xe; `Expr ye]), TWord n)

    | PECall (nmf, [x;y]) when (qunloc nmf) = ([],"natmod") ->
       let xe, _ = tt_expr ~cty:(`Approx PInt) env x in
       let ye, _ = tt_expr ~cty:(`Approx PInt) env y in
       (ECall (Ident.make("natmod"), [`Expr xe; `Expr ye]), TInt (`Natm ye))

    | PECall (nmf, [x]) when List.mem_assoc (qunloc nmf) Env.cast_funs ->
        let exp, rty, name = List.assoc (qunloc nmf) Env.cast_funs in

        let e1, ty1 = tt_expr env x in
        check_ty ~loc:(loc pe) exp ty1;
        (ECall (name, [`Expr e1]), rty)

    | PECall (nmf, args) when List.mem_assoc (qunloc nmf) stdlib ->
        let exp, rty, name = List.assoc (qunloc nmf) stdlib in

        if List.length args <> List.length exp then
          error ~loc:(loc pe) env InvalidArgCount;
        let args, tys =
             List.combine args exp
          |> List.map (fun (e, ty) -> tt_expr ?cty:ty env e)
          |> List.split in
        (ECall (name, List.map (fun x -> `Expr x) args), rty tys)
        
    | PECall ((nm, f) as nmf, args) ->
        let senv = tt_module env nm in

        let f =
          match Env.Procs.get senv (unloc f) with
          | None   -> error ~loc:(loc pe) env (UnknownProc (qunloc nmf))
          | Some f -> f in

        if List.length args <> List.length f.Env.psig then
          error ~loc:(loc pe) env InvalidArgCount;

        let args =
          let do1 e (sg, ty) =
            if List.is_empty sg then
              `Expr (fst (tt_expr ~cty:(`Exact ty) env e))
            else begin
              match unloc e with
              | PEVar ((nm, p) as nmp) -> begin
                  let senv = tt_module env nm in
                  match Env.Procs.get senv (unloc p) with
                  | None ->
                      error ~loc:(loc pe) env (UnknownProc (qunloc nmp))
                  | Some proc ->
                      if List.length proc.Env.psig <> List.length sg then
                        error ~loc:(loc pe) env InvalidHOApplication;
                      List.iter2 (fun (sg, ty) aty ->
                          if not (List.is_empty sg) then
                            error ~loc:(loc pe) env InvalidHOApplication;
                          check_ty_compat ~loc:(loc pe) ~src:aty ~dst:ty)
                        proc.Env.psig sg;
                      `Proc proc.Env.pname
                end
              | _ -> error ~loc:(loc pe) env ProcNameExpected
            end
          in List.map2 do1 args f.Env.psig in

        (ECall (f.Env.pname, args), Type.strip f.Env.pret)

    | PEGet (pe, ps) ->
        let e, ty = tt_expr env pe in   
        let s     = tt_slice env ps in
        let e, ty =
          match Env.Types.inline env ty, s with
          | TWord _, `One i ->
              ECall (get_bit, [`Expr e; `Expr i]), tword1

          | TWord _, `Slice (s,f) ->
              ECall (get_bits, [`Expr e; `Expr s; `Expr f]), TWord Big_int.zero

          | TArray (ty,_), `One _ ->
              EGet (e, s),ty

          | TArray (_,_), `Slice _ ->
              EGet (e, s), ty

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

  | PSDef _ ->
      (env, [])

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
    | [x] when List.mem (unloc x) ["bytes";"array";"uintn";"natmod"] ->
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
        let sg = ([hotype1 (TArray (aty, None))], ty) in
        fst (Env.Procs.bind env (unloc x) sg)

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
and tt_annotation (env : env) (att : pexpr) : ident * hoexpr list =
  match unloc att with (* TODO: typecheck annotations properly : (tt_expr env att) *)
  | PEVar ([],x) when unloc x = "typechecked" -> 
      (Ident.make "typechecked", [])
  | PECall (x, args) when qunloc x = ([],"contract3") || qunloc x = ([],"contract") ->
      let es, tys = List.split (List.map (tt_expr env) args) in
      (Ident.make "contract3", List.map (fun x -> `Expr x) es)
  | _ ->
      error ~loc:(loc att) env UnsupportedAnnotation

(* -------------------------------------------------------------------- *)
(* FIXME: check for duplicate argument name / local variables / inner procs *)
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
      | PSDef _ -> lv
      | _ -> AstUtils.pifold aux lv instr
    in AstUtils.psfold aux [] body in

  let fty  = tt_type env fty in
  let args = List.map (fun (x, xty) -> (unloc x, tt_type env xty)) args in
  let env1, args =
    List.fold_left_map (fun env (x, ty) ->
        let env, x = Env.Vars.bind env (x, ty) in
        (env, (x, hotype1 ty)))
      env args in

  let subs, body =
    let rec doit acc body =
      match body with
      | { pl_data = PSDef pf } :: body -> doit (pf :: acc) body
      | _ -> List.rev acc, body
    in doit [] body in

  let () =
    let rec aux instr =
      match unloc instr with
      | PSDef _ -> error ~loc:(loc instr) env MisplacedProcDef
      | _ -> AstUtils.piiter aux instr
    in AstUtils.psiter aux body in

  let env1, subs = List.fold_left_map tt_procdef env1 subs in

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
    prd_subs = subs;
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
let tt_intf1 (env : env) = function
  | IPTTypeAlias (x, ty) ->
      let env, _ = tt_tydecl env (x, ty) in env

  | IPTProcDecl ((nm, f), sg, rty) ->
      let sg =
        List.map (fun (_x, ty) ->
            match ty with
            | None     -> hotype1 (TNamed ([], "_")) (* FIXME *)
            | Some aty -> tt_hotype env aty) sg in

      let rty  = tt_type env rty in
      let senv = Env.Mod.getnm env (nmunloc nm) |> Option.default Env.empty in
      let senv = fst (Env.Procs.bind senv (unloc f) (sg, rty)) in

      if   List.is_empty nm
      then senv
      else Env.Mod.bindnm env (nmunloc nm) senv

(* -------------------------------------------------------------------- *)
let tt_interface (env : env) (i : pintf) : env =
  List.fold_left tt_intf1 env i

(* -------------------------------------------------------------------- *)
let tt_program (env : env) (p : pspec) : env * env program =
  let env, prgm = List.fold_left_map tt_topdecl1 env p in
  (env, List.flatten prgm)
