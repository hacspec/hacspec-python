open Yojson.Basic.Util
open Testutil
   
let main () =
  let json = Yojson.Basic.from_file "../../../tests/test_vectors/curve448_test_vectors.json" in
  let jsonl = Yojson.Basic.Util.to_list json in
  List.iteri (fun i j ->
      let sk = read_bytes j "private" in
      let pk = read_bytes j "public" in
      let expected = read_bytes j "result" in
      let valid = read_bool j "valid" in
      let computed = Curve448.scalarmult sk pk in
      if expected = computed then Printf.printf "Curve448 Test %d passed.\n" i
      else (Printf.printf "Curve448 Test %d failed.\n" i;
          Printf.printf "expected secret: %s\n" (hex_of_bytes expected);
          Printf.printf "computed secret: %s\n" (hex_of_bytes computed));  
      ()) jsonl; 
  ()

let _ = main()
