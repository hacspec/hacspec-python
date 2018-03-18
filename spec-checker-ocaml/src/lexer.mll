(* -------------------------------------------------------------------- *)
{
  (* ------------------------------------------------------------------ *)
  open Core
  open Parser

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

  (* ------------------------------------------------------------------ *)
  let _keywords = [
  ]

  (* ------------------------------------------------------------------ *)
  let keywords : (string, unit) Hashtbl.t =
    let table = Hashtbl.create 0 in
    List.iter (curry (Hashtbl.add table)) _keywords; table
}

let empty   = ""
let blank   = [' ' '\t' '\r']
let newline = '\n'
let upper   = ['A'-'Z']
let lower   = ['a'-'z']
let letter  = upper | lower
let digit   = ['0'-'9']
let uint    = digit+

(* -------------------------------------------------------------------- *)
rule main = parse
  | empty { assert false }
