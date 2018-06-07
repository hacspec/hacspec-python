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
type reader_r = {
  (* - *) r_lexbuf : Lexing.lexbuf;
  (* - *) r_lexstt : Lexer.State.state;
  mutable r_tokens : Parser.token list;
}

type reader = reader_r Disposable.t

(* -------------------------------------------------------------------- *)
let create lexbuf =
  let state = Lexer.State.create () in
  { r_lexbuf = lexbuf; r_lexstt = state; r_tokens = []; }

(* -------------------------------------------------------------------- *)
let from_channel ~name channel =
  let lexbuf = lexbuf_from_channel name channel in
  Disposable.create (create lexbuf)

(* -------------------------------------------------------------------- *)
let from_file filename =
  let channel = open_in filename in

  try
    let lexbuf = lexbuf_from_channel filename channel in
    Disposable.create ~cb:(fun _ -> close_in channel) (create lexbuf)

  with
    | e ->
        (try close_in channel with _ -> ());
        raise e

(* -------------------------------------------------------------------- *)
let from_string data =
  Disposable.create (create (Lexing.from_string data))

(* -------------------------------------------------------------------- *)
let finalize (reader : reader) =
  Disposable.dispose reader

(* -------------------------------------------------------------------- *)
let lexer = fun reader ->
  let state  = reader.r_lexstt in
  let lexbuf = reader.r_lexbuf in

  if reader.r_tokens = [] then
    reader.r_tokens <- Lexer.main state lexbuf;

  match reader.r_tokens with
  | [] ->
      failwith "short-read-from-lexer"

  | token :: queue -> begin
      reader.r_tokens  <- queue;
      (token, Lexing.lexeme_start_p lexbuf, Lexing.lexeme_end_p lexbuf)
  end

(* -------------------------------------------------------------------- *)
let parse_spec (reader : reader) =
  parserfun_spec (fun () -> lexer (Disposable.get reader))
