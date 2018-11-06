(* -------------------------------------------------------------------- *)
module P = Hacs.Reader
module T = Hacs.Typing
module C = Hacs.Core

(* -------------------------------------------------------------------- *)
let main () =
  if Array.length Sys.argv - 1 <> 1 then begin
    Format.eprintf "Usage: %s [filename]" Sys.argv.(0);
    exit 2
  end;

  let filename = Sys.argv.(1) in
  let modulename = Filename.remove_extension (Filename.basename filename) in
  try
    let env =
        (* T.tt_interface T.Env.empty  *)
        let stream = P.from_file (C.Resource.getlib "speclib.pyi") in
        let speclib = P.parse_intf stream in
        T.tt_interface T.Env.empty speclib
    in

    let (p : T.Env.env * T.Env.env Hacs.Ast.program) =
      let stream = P.from_file filename in
      let past   = P.parse_spec stream in
      T.tt_program env past
    in

    Format.printf
         "(* Generated from hacspec module %s *)\n%s%!"
         filename (Fstar.fstar_of_program modulename p)
  with
  | e ->
      Format.eprintf "%s%!" (Hacs.Pexception.tostring e);
      exit 1

(* -------------------------------------------------------------------- *)
let () = main ()
