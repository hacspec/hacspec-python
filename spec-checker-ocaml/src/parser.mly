%{
  open Core
  open Location
  open Syntax

  let parse_error loc msg = raise (ParseError (loc, msg))
%}

%token INDENT
%token DEINDENT
%token NEWLINE

%token TRUE
%token FALSE

%token AND
%token DEF
%token ELIF
%token ELSE
%token FAIL
%token FOR
%token FROM
%token IF
%token IMPORT
%token IN
%token LAMBDA
%token NOT
%token OR
%token PASS
%token RANGE
%token RETURN

%token <string> IDENT
%token <Big_int.big_int> UINT
%token <string> STRING

%token AT
%token BANGEQ
%token COLON
%token COMMA
%token DASHGT
%token EQ
%token EQEQ
%token GT
%token GTEQ
%token DOT
%token LT
%token LTEQ
%token LTLT
%token GTGT
%token MINUS
%token MINUSEQ
%token PLUS
%token PLUSEQ
%token SEMICOLON
%token SLASH
%token SLASHEQ
%token SLASHSLASH
%token SLASHSLASHEQ
%token STAR
%token STAREQ
%token STARSTAR
%token STARSTAREQ
%token HAT
%token TILDE
%token HATEQ
%token AMP
%token AMPEQ
%token PIPE
%token PIPEEQ
%token PCENT
%token PCENTEQ

%token LPAREN
%token RPAREN
%token LBRACKET
%token RBRACKET

%token EOF

%nonassoc LAMBDA_prec
%left     OR
%left     AND
%nonassoc NOT 
%nonassoc EQEQ BANGEQ
%left     LT GT LTEQ GTEQ
%nonassoc LTLT
%nonassoc GTGT
%left     PLUS MINUS HAT AMP PIPE
%left     STAR SLASH SLASHSLASH PCENT
%right    STARSTAR
%right    LBRACKET

%type <Syntax.pspec> spec

%start spec
%%

(* -------------------------------------------------------------------- *)
spec:
| x=topdecl EOF
    { x }

| x=loc(error)
    { parse_error (loc x) None }

(* -------------------------------------------------------------------- *)
ident:
| x=loc(IDENT) { x }

(* -------------------------------------------------------------------- *)
%inline qident:
| q=ioption(postfix(rlist0(ident, DOT), DOT)) x=ident
    { (List.rev (Option.default [] q), x) }

(* -------------------------------------------------------------------- *)
tyident:
| x=ident COLON ty=type_ { (x, ty) }

(* -------------------------------------------------------------------- *)
otyident:
| x=ident ty=prefix(COLON, type_)? { (x, ty) }

(* -------------------------------------------------------------------- *)
%inline uniop:
| NOT   { (`Not :> puniop) }
| TILDE  { (`BNot :> puniop) }
| MINUS { (`Neg :> puniop) }

(* -------------------------------------------------------------------- *)
%inline binop:
| PLUS       { (`Add  :> pbinop) }
| MINUS      { (`Sub  :> pbinop) }
| STAR       { (`Mul  :> pbinop) }
| STARSTAR   { (`Pow  :> pbinop) }
| SLASH      { (`Div  :> pbinop) }
| SLASHSLASH { (`IDiv :> pbinop) }
| PCENT      { (`Mod  :> pbinop) }
| PIPE       { (`BOr  :> pbinop) }
| AMP        { (`BAnd :> pbinop) }
| HAT        { (`BXor :> pbinop) }
| OR         { (`Or   :> pbinop) }
| AND        { (`And  :> pbinop) }
| LT         { (`Lt   :> pbinop) }
| GT         { (`Gt   :> pbinop) }
| LTLT       { (`LSL  :> pbinop) }
| GTGT       { (`LSR  :> pbinop) }
| LTEQ       { (`Le   :> pbinop) }
| GTEQ       { (`Ge   :> pbinop) }

(* -------------------------------------------------------------------- *)
%inline assop:
| EQ           { (`Plain :> passop) }
| PLUSEQ       { (`Add   :> passop) }
| MINUSEQ      { (`Sub   :> passop) }
| STAREQ       { (`Mul   :> passop) }
| STARSTAREQ   { (`Pow   :> passop) }
| SLASHEQ      { (`Div   :> passop) }
| SLASHSLASHEQ { (`IDiv  :> passop) }
| PCENTEQ      { (`Mod   :> passop) }
| AMPEQ        { (`BAnd  :> passop) }
| PIPEEQ       { (`BOr   :> passop) }
| HATEQ        { (`BXor  :> passop) }

(* -------------------------------------------------------------------- *)
slice:
| e=expr
    { (`One e :> pslice) }

| e1=expr COLON e2=expr
    { (`Slice (e1, e2) :> pslice) }

(* -------------------------------------------------------------------- *)
sexpr_r:
| x=qident
    { PEVar x }

| TRUE
    { PEBool true }

| FALSE
    { PEBool false }

| i=UINT
    { PEUInt i }

| s=STRING
    { PEString s }

| o=uniop e=sexpr %prec NOT
    { PEUniOp (o, e) }

| e1=sexpr o=binop e2=sexpr
    { PEBinOp (o, (e1, e2)) }

| e1=sexpr EQEQ e2=sexpr
    { PEEq (false, (e1, e2)) }

| e1=sexpr BANGEQ e2=sexpr
    { PEEq (true, (e1, e2)) }

| f=qident args=parens(plist0(sexpr, COMMA))
    { PECall (f, args) }

| es=parens(empty)
    { PETuple ([], false) }

| esb=parens(es=rlist1(sexpr, COMMA) b=iboption(COMMA) { (es, b) })
    { let (es, b) = esb in PETuple (List.rev es, b) }

| es=brackets(rlist0(sexpr, COMMA))
    { PEArray es }

| e=sexpr i=brackets(slice)
    { PEGet (e, i) }

| LAMBDA xs=plist1(ident, COMMA) COLON e=sexpr %prec LAMBDA_prec
    { PEFun (xs, e) }

(* -------------------------------------------------------------------- *)
%inline expr_r:
| e=sexpr_r
    { e }

| es=plist2(sexpr, COMMA)
    { PETuple (es, false) }

(* -------------------------------------------------------------------- *)
%inline sexpr:
| e=loc(sexpr_r) { e }

(* -------------------------------------------------------------------- *)
%inline expr:
| e=loc(expr_r) { e }

(* -------------------------------------------------------------------- *)
%inline type_:
| ty=sexpr { ty }

(* -------------------------------------------------------------------- *)
sinstr_r:
| FAIL s=expr
    { PSFail (s) }

| PASS
    { PSPass }

| x=tyident EQ e=expr
    { PSDecl (x, e) }

| RETURN e=expr?
    { PSReturn e }

| lv=expr o=assop e=expr
    { PSAssign (lv, o, e) }

| e=expr
    { PSExpr e }

(* -------------------------------------------------------------------- *)
prange:
| RANGE e=parens(sexpr)
    { (None, e) }

| RANGE e=parens(e1=sexpr COMMA e2=sexpr { (e1, e2) })
    { (Some (fst e), snd e) }

(* -------------------------------------------------------------------- *)
%inline sinstr:
| i=loc(sinstr_r) { i }

(* -------------------------------------------------------------------- *)
instr_r:
| i=sinstr_r NEWLINE
    { i }

| FOR x=ident ty=prefix(COLON, type_)? IN e=prange COLON b=block
    be=option(ELSE COLON b=block { b })

    { PSFor (((x, ty), e, b), be) }

| IF e=expr COLON b=block
    bie=list  (ELIF e=expr COLON b=block { (e, b) })
    bse=option(ELSE COLON b=block { b })

    { PSIf ((e, b), bie, bse) }

| x=procdef
    { PSDef x }

(* -------------------------------------------------------------------- *)
%inline instr:
| i=loc(instr_r) { i }

(* -------------------------------------------------------------------- *)
procdef:
| iboption(postfix(annotation, NEWLINE)) DEF f=ident
    args=parens(plist0(tyident, COMMA)) DASHGT ty=type_
  COLON b=block

    { ((f, ty), args, b) }

(* -------------------------------------------------------------------- *)
block:
| NEWLINE INDENT b=instr+ DEINDENT
    { b }

| b=plist1(sinstr, SEMICOLON) NEWLINE
    { b }

(* -------------------------------------------------------------------- *)
annotation:
| AT sexpr { () }

(* -------------------------------------------------------------------- *)
ipident:
| STAR    { None }
| x=ident { Some x}

import:
| IMPORT xs=plist1(qident, COMMA)
    { List.map (fun x -> PTImport (x, None)) xs }

| FROM x=qident IMPORT ips=plist1(ipident, COMMA)
    { [PTImport (x, Some ips)] }

(* -------------------------------------------------------------------- *)
topdecl_r:
| mods=import NEWLINE
    { mods }

| xs=plist1(otyident, COMMA) EQ e=expr NEWLINE
    { List.map (fun x -> PTVar (x, e)) xs }

| x=procdef
    { [PTDef x] }

(* -------------------------------------------------------------------- *)
topdecl:
| xs=list(topdecl_r) { List.flatten xs }

(* -------------------------------------------------------------------- *)
%inline loc(X):
| x=X {
    let loc = Location.make $startpos $endpos in
    { pl_data = x; pl_loc = loc }
  }

(* -------------------------------------------------------------------- *)
%inline plist0(X, S):
| aout=separated_list(S, X) { aout }

iplist1_r(X, S):
| x=X { [x] }
| xs=iplist1_r(X, S) S x=X { x :: xs }

%inline iplist1(X, S):
| xs=iplist1_r(X, S) { List.rev xs }

%inline plist1(X, S):
| aout=separated_nonempty_list(S, X) { aout }

%inline plist2(X, S):
| x=X S xs=plist1(X, S) { x :: xs }

(* -------------------------------------------------------------------- *)
%inline empty:
| /**/ { () }

(* -------------------------------------------------------------------- *)
__rlist1(X, S):                         (* left-recursive *)
| x=X { [x] }
| xs=__rlist1(X, S) S x=X { x :: xs }

%inline rlist0(X, S):
| /* empty */     { [] }
| xs=rlist1(X, S) { xs }

%inline rlist1(X, S):
| xs=__rlist1(X, S) { List.rev xs }

(* -------------------------------------------------------------------- *)
%inline iboption(X):
| X { true  }
|   { false }

(* -------------------------------------------------------------------- *)
%inline prefix(P, X):
| P x=X { x }

(* -------------------------------------------------------------------- *)
%inline postfix(X, P):
| x=X P { x }

(* -------------------------------------------------------------------- *)
%inline parens(X):
| LPAREN x=X RPAREN { x }

%inline brackets(X):
| LBRACKET x=X RBRACKET { x }
