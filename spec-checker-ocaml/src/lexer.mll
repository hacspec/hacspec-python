(* -------------------------------------------------------------------- *)
{
  (* ------------------------------------------------------------------ *)
  open Core
  open Parser
  open Lexing

  (* ------------------------------------------------------------------ *)
  module L = Location

  (* ------------------------------------------------------------------ *)
  let lex_error lexbuf msg =
    raise (Syntax.ParseError (L.oflexbuf lexbuf, Some msg))

  module State : sig
    type state

    exception InvalidDeindent
    exception InvalidState

    val create      : unit  -> state
    val offset      : state -> int
    val incontn     : state -> bool
    val contn       : state -> int
    val enter_contn : state -> unit
    val leave_contn : state -> unit
    val set         : state -> int -> [`Up | `Down of int] option
  end = struct
    type stindent = {
      offset  : int;
      history : int list;
    }

    type rstate =
      Contn of int * stindent | Indent of stindent

    type state = rstate ref

    exception InvalidDeindent
    exception InvalidState

    let empty : rstate =
      Indent { offset = 0; history = []; }

    let roffset = function 
      | Indent { offset } -> offset
      | _ -> raise InvalidState

    let on_stindent f = function
      | Indent s -> Indent (f s)
      | Contn  _ -> raise InvalidState

    let rcontn = function Indent _ -> 0 | Contn (c, _) -> c

    let renter_contn = function
      | Indent st -> Contn (1, st)
      | Contn (n, st) -> Contn (n + 1, st)

    let rleave_contn = function
      | Indent st -> raise InvalidState
      | Contn (n, st) ->
          if n <= 1 then Indent st else Contn (n-1, st)

    let rincont = function Indent _ -> false | Contn _ -> true

    let stpush (s : stindent) (i : int) =
      { offset = i; history = s.offset :: s.history; }

    let stpop (s : stindent) =
      match s.history with
      | []     -> s
      | i :: s -> { offset = i; history = s; }

    let stset (s : stindent) (i : int) =
      assert (0 <= i);

      if i >= s.offset then
        if i = s.offset then (s, None) else (stpush s i, Some `Up)
      else
        let lvl, s =
          let rec doit acc (s : stindent) =
            if i < s.offset then doit (1+acc) (stpop s) else (acc, s)
          in doit 0 s in
            
        if i <> s.offset then raise InvalidDeindent;
        (s, Some (`Down lvl))

    let rpush (s : rstate) (i : int) =
      on_stindent (fun s -> stpush s i) s

    let rpop (s : rstate) =
      on_stindent stpop s

    let rset (s : rstate) (i : int) =
      match s with
      | Indent s ->
          let (s, aout) = stset s i in (Indent s, aout)

      | Contn _ ->
          raise InvalidState

    let create () : state =
      ref empty

    let offset (s : state) =
      roffset !s

    let contn (s : state) =
      rcontn !s

    let incontn (s : state) =
      rincont !s

    let enter_contn (s : state) =
      s := renter_contn !s

    let leave_contn (s : state) =
      s := rleave_contn !s

    let set (s : state) (i : int) =
      let (news, aout) = rset !s i in s := news; aout
  end

  (* ------------------------------------------------------------------ *)
  let _keywords = [
    ("True"  , TRUE );
    ("False" , FALSE);

    ("lambda", LAMBDA);
    ("and"   , AND   );
    ("def"   , DEF   );
    ("else"  , ELSE  );
    ("elif"  , ELIF  );
    ("fail"  , FAIL  );
    ("for"   , FOR   );
    ("from"  , FROM  );
    ("if"    , IF    );
    ("import", IMPORT);
    ("in"    , IN    );
    ("not"   , NOT   );
    ("or"    , OR    );
    ("pass"  , PASS  );
    ("range" , RANGE );
    ("return", RETURN);
  ]

  (* ------------------------------------------------------------------ *)
  let keywords : (string, Parser.token) Hashtbl.t =
    let table = Hashtbl.create 0 in
    List.iter (curry (Hashtbl.add table)) _keywords; table
}

let empty    = ""
let blank    = [' ' '\t']
let newline  = '\r'? '\n'
let upper    = ['A'-'Z']
let lower    = ['a'-'z']
let letter   = upper | lower
let digit    = ['0'-'9']
let xdigit   = ['0'-'9' 'a'-'f' 'A'-'F']
let ident    = (letter | '_') (letter | digit | '_')*
let uint     = digit+
let uhexint  = xdigit+
let comment  = '#' [^'\n']*

(* -------------------------------------------------------------------- *)
rule main stt = parse
  | eof {
      let pos = lexbuf.lex_start_p in
      let off = pos.pos_cnum - pos.pos_bol in
      let all = ref [] in

      if off <> 0 then all := NEWLINE :: !all;
      begin match State.set stt 0 with
      | Some (`Down i) -> all := List.make i DEINDENT @ !all
      | _ -> () end;
      List.rev (EOF :: !all)
    }

  | blank* comment? (newline as s | eof) {
      Lexing.new_line lexbuf;

      if State.incontn stt then main stt lexbuf else

      let pos = lexbuf.lex_start_p in
      let off = pos.pos_cnum - pos.pos_bol in

      if off = 0 then main stt lexbuf else [NEWLINE]
    }

  | empty {
      let pos = lexbuf.lex_curr_p in
      let off = pos.pos_cnum - pos.pos_bol in
      if off = 0 then
        match offset stt lexbuf with
        | Some (`Down i) -> List.make i DEINDENT
        | Some `Up       -> [INDENT]
        | None           -> token stt lexbuf
      else token stt lexbuf
    }

and offset stt = parse
  | blank* as s
      { if not (State.incontn stt) then
          State.set stt (String.length s)
        else None }

and token stt = parse
  | blank+
      { token stt lexbuf }

  | ident as id {
      [Hashtbl.find_default keywords id (IDENT id)]
    }

  | (uint | ("0x" uhexint)) as i {
      [UINT (Big_int.big_int_of_string i)]
    }

  | '(' { State.enter_contn stt; [LPAREN   ] }
  | '[' { State.enter_contn stt; [LBRACKET ] }

  | ')' { if State.incontn stt then State.leave_contn stt; [RPAREN   ] }
  | ']' { if State.incontn stt then State.leave_contn stt; [RBRACKET ] }

  | ':' { [COLON    ] }
  | ';' { [SEMICOLON] }
  | ',' { [COMMA    ] }
  | '.' { [DOT      ] }
  | '@' { [AT       ] }
  | '|' { [PIPE     ] }
  | '&' { [AMP      ] }
  | '%' { [PCENT    ] }
  | '^' { [HAT      ] }

  | "+"   { [PLUS        ] }
  | "-"   { [MINUS       ] }
  | "*"   { [STAR        ] }
  | "**"  { [STARSTAR    ] }
  | "/"   { [SLASH       ] }
  | "//"  { [SLASHSLASH  ] }
  | "="   { [EQ          ] }
  | "+="  { [PLUSEQ      ] }
  | "-="  { [MINUSEQ     ] }
  | "**=" { [STARSTAREQ  ] }
  | "*="  { [STAREQ      ] }
  | "/="  { [SLASHEQ     ] }
  | "//=" { [SLASHSLASHEQ] }
  | "|="  { [PIPEEQ       ] }
  | "&="  { [AMPEQ       ] }
  | "^="  { [HATEQ       ] }
  | "=="  { [EQEQ        ] }
  | "!="  { [BANGEQ      ] }
  | "<"   { [LT          ] }
  | ">"   { [GT          ] }
  | "<="  { [LTEQ        ] }
  | ">="  { [GTEQ        ] }
  | "->"  { [DASHGT      ] }
  | "<<"   { [LTLT          ] }
  | ">>"   { [GTGT          ] }

  |  _ as c { lex_error lexbuf (Printf.sprintf "illegal character: %c" c) }
