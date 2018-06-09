(* -------------------------------------------------------------------- *)
module P = Reader
module T = Typing

(* -------------------------------------------------------------------- *)
let main () =
  try
    let (_ : Typing.Env.env) =
      let stream = P.from_channel ~name:"stdin" stdin in
      let past   = P.parse_spec stream in
      T.tt_program past
    in ()
  with
  | e ->
      Format.eprintf "%s%!" (Pexception.tostring e);
      exit 1

(* -------------------------------------------------------------------- *)
let () = main ()
