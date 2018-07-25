(* -------------------------------------------------------------------- *)
module P = Reader
module T = Typing

(* -------------------------------------------------------------------- *)
let main () =
  if Array.length Sys.argv - 1 <> 1 then begin
    Format.eprintf "Usage: %s [filename]" Sys.argv.(0);
    exit 2
  end;

  let filename = Sys.argv.(1) in
  let modulename = Filename.remove_extension (Filename.basename filename) in
  try
    let (p : T.Env.env Ast.program) =
      let stream = P.from_file filename in
      let past   = P.parse_spec stream in
      T.tt_program past
    in Format.printf "Parsed and Type-checked hacspec module %s \n" modulename
  with
  | e ->
      Format.eprintf "%s%!" (Pexception.tostring e);
      exit 1

(* -------------------------------------------------------------------- *)
let () = main ()
