(* -------------------------------------------------------------------- *)
module P = Reader
module T = Typing

(* -------------------------------------------------------------------- *)
let main () =
  let (_ : Syntax.pspec) =
    let stream = Reader.from_channel ~name:"stdin" stdin in
    Reader.parse_spec stream
  in ()

(* -------------------------------------------------------------------- *)
let () = main ()
