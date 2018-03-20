%{
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
%token IF
%token IN
%token NOT
%token OR
%token PASS
%token RANGE
%token RETURN

%token <string> IDENT
%token <Big_int.big_int> UINT

%token BANGEQ
%token COLON
%token COMMA
%token EQ
%token EQEQ
%token GT
%token GTEQ
%token LT
%token LTEQ
%token MINUS
%token MINUSEQ
%token PLUS
%token PLUSEQ
%token SLASH
%token SLASHEQ
%token STAR
%token STAREQ

%token LPAREN
%token RPAREN
%token LBRACKET
%token RBRACKET

%token EOF

%left     OR
%left     AND
%nonassoc NOT
%nonassoc EQEQ BANGEQ
%left     LT GT LTEQ GTEQ
%left     PLUS MINUS
%left     STAR SLASH
%right    LBRACKET

%type <Syntax.pspec> spec

%start spec
%%

(* -------------------------------------------------------------------- *)
spec:
| x=topdecl EOF { x }

(* -------------------------------------------------------------------- *)
ident:
| x=loc(IDENT) { x }

(* -------------------------------------------------------------------- *)
%inline uniop:
| NOT   { (`Not :> puniop) }
| MINUS { (`Neg :> puniop) }

(* -------------------------------------------------------------------- *)
%inline binop:
| EQEQ   { (`Eq  :> pbinop) }
| BANGEQ { (`NEq :> pbinop) }
| PLUS   { (`Add :> pbinop) }
| MINUS  { (`Sub :> pbinop) }
| STAR   { (`Mul :> pbinop) }
| SLASH  { (`Div :> pbinop) }
| OR     { (`Or  :> pbinop) }
| AND    { (`And :> pbinop) }
| LT     { (`Lt  :> pbinop) }
| GT     { (`Gt  :> pbinop) }
| LTEQ   { (`Le  :> pbinop) }
| GTEQ   { (`Ge  :> pbinop) }

(* -------------------------------------------------------------------- *)
%inline assop:
| EQ      { (`Plain :> passop) }
| PLUSEQ  { (`Add   :> passop) }
| MINUSEQ { (`Sub   :> passop) }
| STAREQ  { (`Mul   :> passop) }
| SLASHEQ { (`Div   :> passop) }

(* -------------------------------------------------------------------- *)
slice:
| e=expr
    { (`One e :> pslice) }

| e1=expr COLON e2=expr
    { (`Slice (e1, e2) :> pslice) }

(* -------------------------------------------------------------------- *)
expr_r:
| x=ident
    { EVar x }

| TRUE
    { EBool true }

| FALSE
    { EBool false }

| i=UINT
    { EUInt i }

| RANGE e=parens(expr)
    { ERange e }

| o=uniop e=expr %prec NOT
    { EUniOp (o, e) }

| e1=expr o=binop e2=expr
    { EBinOp (o, (e1, e2)) }

| f=ident args=parens(plist0(expr, COMMA))
    { ECall (f, args) }

| es=parens(empty)
    { ETuple ([], false) }

| esb=parens(es=rlist1(expr, COMMA) b=iboption(COMMA) { (es, b) })
    { let (es, b) = esb in ETuple (es, b) }

| es=brackets(es=rlist1(expr, COMMA) COMMA? { es })
    { EArray es }

| e=expr i=brackets(slice)
    { EGet (e, i) }

(* -------------------------------------------------------------------- *)
expr:
| e=loc(expr_r) { e }

(* -------------------------------------------------------------------- *)
instr_r:
| FAIL
    { SFail }

| PASS
    { SPass }

| RETURN e=expr?
    { SReturn e }

| lv=expr o=assop e=expr
    { SAssign (lv, o, e) }

| FOR x=ident IN e=expr COLON b=block
    be=option(ELSE COLON b=block { b })

    { SFor ((x, e, b), be) }

| IF e=expr COLON b=block
    bie=list  (ELIF e=expr COLON b=block { (e, b) })
    bse=option(ELSE COLON b=block { b })

    { SIf ((e, b), bie, bse) }

(* -------------------------------------------------------------------- *)
instr:
| i=loc(instr_r) eol { i }

(* -------------------------------------------------------------------- *)
block:
| NEWLINE INDENT b=instr+ DEINDENT
    { b }

(* -------------------------------------------------------------------- *)
topdecl_r:
| x=ident EQ e=expr eol
    { TVar (x, e) }

| DEF f=ident args=parens(plist0(ident, COMMA)) COLON b=block
    { TDef (f, args, b) }

(* -------------------------------------------------------------------- *)
topdecl:
| NEWLINE? xs=list(topdecl_r) { xs }

(* -------------------------------------------------------------------- *)
%inline eol: NEWLINE | EOF { }

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
%inline parens(X):
| LPAREN x=X RPAREN { x }

%inline brackets(X):
| LBRACKET x=X RBRACKET { x }
