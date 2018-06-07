(* -------------------------------------------------------------------- *)
module P = Reader

(* -------------------------------------------------------------------- *)
let main () =
  try
    let (_ : Syntax.pspec) =
      let stream = Reader.from_channel ~name:"stdin" stdin in
      Reader.parse_spec stream
    in ()
  with
  | e ->
      Format.eprintf "%s%!" (Pexception.tostring e);
      exit 1

(* -------------------------------------------------------------------- *)
let () = main ()
