open Ocamlbuild_plugin

let _ = dispatch begin function
   | After_options ->
       Options.ocamlc   := S[!Options.ocamlc  ; A"-rectypes"];
       Options.ocamlopt := S[!Options.ocamlopt; A"-rectypes"];

   | After_rules ->
       (* menhir & --explain/--trace/--table *)
       flag ["ocaml"; "parser"; "menhir"; "menhir_explain"] & A"--explain";
       flag ["ocaml"; "parser"; "menhir"; "menhir_trace"  ] & A"--trace";
       flag ["ocaml"; "parser"; "menhir"; "menhir_table"  ] & A"--table";

       (* Threads switches *)
       flag ["ocaml"; "pkg_threads"; "compile"] (S[A "-thread"]);
       flag ["ocaml"; "pkg_threads"; "link"] (S[A "-thread"]);

       (* Bisect *)
       flag ["ocaml"; "compile" ;  "bisect"] & S[A"-package"; A"bisect"];
       flag ["ocaml"; "compile" ;  "bisect"] & S[A"-syntax" ; A"camlp4o"];
       flag ["ocaml"; "compile" ;  "bisect"] & S[A"-syntax" ; A"bisect_pp"];
       flag ["ocaml"; "ocamldep";  "bisect"] & S[A"-package"; A"bisect"];
       flag ["ocaml"; "ocamldep";  "bisect"] & S[A"-syntax" ; A"camlp4o"];
       flag ["ocaml"; "ocamldep";  "bisect"] & S[A"-syntax" ; A"bisect_pp"];
       flag ["ocaml"; "link"    ;  "bisect"] & S[A"-package"; A"bisect"];

   | _ -> ()
end
