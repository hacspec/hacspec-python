(* -------------------------------------------------------------------- *)
open Core

module P = Reader
module T = Typing

(* -------------------------------------------------------------------- *)
let main () =
  if Array.length Sys.argv - 1 <> 1 then begin
    Format.eprintf "Usage: %s [filename]" Sys.argv.(0);
    exit 2
  end;

  let filename = Sys.argv.(1) in
  let modname  = Filename.remove_extension (Filename.basename filename) in

  try
    let (_i : Syntax.pintf) =
      with_dispose ~dispose:P.finalize
        (P.parse_intf)
        (P.from_file (Resource.getlib "speclib.pyi")) in

    let (_p : T.Env.env Ast.program) =
      with_dispose ~dispose:P.finalize
        (P.parse_spec %> T.tt_program)
        (P.from_file filename)
    in

    Format.eprintf
      "Parsed and type-checked hacspec module `%s'\n%!"
      modname
  with
  | e ->
      Format.eprintf "%s%!" (Pexception.tostring e);
      exit 1

(* -------------------------------------------------------------------- *)
let () = main ()
