(* -------------------------------------------------------------------- *)
open Core

module P = Parser
module L = Lexing

(* -------------------------------------------------------------------- *)
let lexbuf_from_channel = fun name channel ->
  let lexbuf = Lexing.from_channel channel in
    lexbuf.Lexing.lex_curr_p <- {
        Lexing.pos_fname = name;
        Lexing.pos_lnum  = 1;
        Lexing.pos_bol   = 0;
        Lexing.pos_cnum  = 0
      };
    lexbuf

(* -------------------------------------------------------------------- *)
let parserfun_spec =
    MenhirLib.Convert.Simplified.traditional2revised P.spec

(* -------------------------------------------------------------------- *)
type reader = Lexing.lexbuf Disposable.t

let lexbuf (reader : reader) =
  Disposable.get reader

(* -------------------------------------------------------------------- *)
let from_channel ~name channel =
  let lexbuf = lexbuf_from_channel name channel in
  Disposable.create lexbuf

(* -------------------------------------------------------------------- *)
let from_file filename =
  let channel = open_in filename in

  try
    let lexbuf = lexbuf_from_channel filename channel in
    Disposable.create ~cb:(fun _ -> close_in channel) lexbuf

  with
    | e ->
        (try close_in channel with _ -> ());
        raise e

(* -------------------------------------------------------------------- *)
let from_string data =
  Disposable.create (Lexing.from_string data)

(* -------------------------------------------------------------------- *)
let finalize (reader : reader) =
  Disposable.dispose reader

(* -------------------------------------------------------------------- *)
let lexer (lexbuf : L.lexbuf) =
  let token = Lexer.main lexbuf in
  (token, L.lexeme_start_p lexbuf, L.lexeme_end_p lexbuf)

(* -------------------------------------------------------------------- *)
let parse_spec (reader : reader) =
  parserfun_spec (fun () -> lexer (lexbuf reader))
