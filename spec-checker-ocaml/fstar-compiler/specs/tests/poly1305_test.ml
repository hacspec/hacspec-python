open Yojson.Basic.Util
open Testutil
   
let main () =
  let json = Yojson.Basic.from_file "../../../tests/test_vectors/poly1305_test_vectors.json" in
  let jsonl = Yojson.Basic.Util.to_list json in
  List.iteri (fun i j ->
      let key = read_bytes j "key" in
      let input = read_bytes j "input" in
      let output = read_bytes j "tag" in
      let computed = Poly1305.poly1305_mac input key in
      if output = computed then Printf.printf "Poly1305 Test %d passed.\n" i
      else (Printf.printf "Poly1305 Test %d failed.\n" i;
            Printf.printf "expected ciphertext: %s\n" (hex_of_bytes output);
            Printf.printf "computed ciphertext: %s\n" (hex_of_bytes computed));
      ()) jsonl;
  ()

let _ = main()
