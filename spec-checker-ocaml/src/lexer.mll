(* -------------------------------------------------------------------- *)
{
  (* ------------------------------------------------------------------ *)
  open Core
  open Parser
  open Lexing

  (* ------------------------------------------------------------------ *)
  module L = Location

  (* ------------------------------------------------------------------ *)
  exception LexicalError of L.t option * string

  let pp_lex_error fmt msg =
    Format.fprintf fmt "parse error: %s" msg

  let () =
    let pp fmt exn =
      match exn with
      | LexicalError (_, msg) -> pp_lex_error fmt msg
      | _ -> raise exn
    in
      Pexception.register pp

  (* ------------------------------------------------------------------ *)
  let lex_error lexbuf msg =
    raise (LexicalError (Some (L.oflexbuf lexbuf), msg))

  module State : sig
    type state

    exception InvalidDeindent

    val create : unit -> state
    val offset : state -> int
    val set    : state -> int -> [`Up | `Down] option
  end = struct
    type rstate = {
      offset  : int;
      history : int list;
    }

    type state = rstate ref

    exception InvalidDeindent

    let empty : rstate =
      { offset = 0; history = []; }

    let roffset { offset } =
      offset

    let rpush (s : rstate) (i : int) =
      { offset = i; history = s.offset :: s.history; }

    let rpop (s : rstate) =
      match s.history with
      | []     -> s
      | i :: s -> { offset = i; history = s; }

    let rset (s : rstate) (i : int) =
      assert (0 <= i);

      if i >= s.offset then
        if i = s.offset then (s, None) else (rpush s i, Some `Up)
      else
        let s =
          let rec doit (s : rstate) =
            if i < s.offset then doit (rpop s) else s
          in doit s in
            
        if i <> s.offset then raise InvalidDeindent;
        (s, Some `Down)

    let create () : state =
      ref empty

    let offset (s : state) =
      roffset !s

    let set (s : state) (i : int) =
      let (news, aout) = rset !s i in s := news; aout
  end

  (* ------------------------------------------------------------------ *)
  let _keywords = [
    ("True"  , TRUE );
    ("False" , FALSE);

    ("and"   , AND  );
    ("def"   , DEF  );
    ("else"  , ELSE );
    ("elif"  , ELIF );
    ("fail"  , FAIL );
    ("for"   , FOR  );
    ("if"    , IF   );
    ("in"    , IN   );
    ("not"   , NOT  );
    ("or"    , OR   );
    ("pass"  , PASS );
    ("range" , RANGE);
    ("return", RETURN);
  ]

  (* ------------------------------------------------------------------ *)
  let keywords : (string, Parser.token) Hashtbl.t =
    let table = Hashtbl.create 0 in
    List.iter (curry (Hashtbl.add table)) _keywords; table
}

let empty   = ""
let blank   = [' ' '\t']
let newline = '\r'? '\n'
let upper   = ['A'-'Z']
let lower   = ['a'-'z']
let letter  = upper | lower
let digit   = ['0'-'9']
let xdigit  = ['0'-'9' 'a'-'f' 'A'-'F']
let ident   = (letter | '_') (letter | digit | '_')*
let uint    = digit+
let uhexint = xdigit+
let comment = '#' [^'\n']*

(* -------------------------------------------------------------------- *)
rule main stt = parse
  | eof
      { match State.set stt 0 with Some _ -> DEINDENT | _ -> EOF }

  | ((blank* comment? newline)* blank* comment? (newline | eof) as e) as s {
      for i = 1 to (String.count ((=) '\n') s) do
        Lexing.new_line lexbuf
      done; NEWLINE
    }

  | empty {
      let pos = lexbuf.lex_curr_p in
      let off = pos.pos_cnum - pos.pos_bol in
      if off = 0 then
        match offset stt lexbuf with
        | Some `Down -> DEINDENT
        | Some `Up   -> INDENT
        | None       -> token lexbuf
      else token lexbuf
    }

and offset stt = parse
  | blank* as s
      { State.set stt (String.length s) }

and token = parse
  | blank+
      { token lexbuf }

  | ident as id {
      Hashtbl.find_default keywords id (IDENT id)
    }

  | (uint | ("0x" uhexint)) as i {
      UINT (Big_int.big_int_of_string i)
    }

  | '(' { LPAREN   }
  | ')' { RPAREN   }
  | '[' { LBRACKET }
  | ']' { RBRACKET }
  | ':' { COLON    }
  | ',' { COMMA    }

  | "+"  { PLUS    }
  | "-"  { MINUS   }
  | "*"  { STAR    }
  | "/"  { SLASH   }
  | "="  { EQ      }
  | "+=" { PLUSEQ  }
  | "-=" { MINUSEQ }
  | "*=" { STAREQ  }
  | "/=" { SLASHEQ }
  | "==" { EQEQ    }
  | "!=" { BANGEQ  }
  | "<"  { LT      }
  | ">"  { GT      }
  | "<=" { LTEQ    }
  | ">=" { GTEQ    }

  |  _ as c { lex_error lexbuf (Printf.sprintf "illegal character: %c" c) }
