%{
  open Location
  open Syntax

  let parse_error loc msg = raise (ParseError (loc, msg))
%}

%token EOF

%type <Syntax.spec> spec

%start spec
%%

(* -------------------------------------------------------------------- *)
spec:
| EOF { assert false }
