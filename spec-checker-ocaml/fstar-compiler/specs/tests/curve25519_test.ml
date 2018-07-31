open Yojson.Basic.Util
open Testutil
   
let main () =
  let json = Yojson.Basic.from_file "../../../tests/test_vectors/curve25519_test_vectors.json" in
  let jsonl = Yojson.Basic.Util.to_list json in
  List.iteri (fun i j ->
      let sk = read_bytes j "private" in
      let pk = read_bytes j "public" in
      let expected = read_bytes j "result" in
      let valid = read_bool j "valid" in
      if not (Curve25519.is_on_curve pk) then
        if valid then
          Printf.printf "Curve25519 Test %d failed (public key failed is_on_curve).\n" i
        else
          Printf.printf "Curve25519 Test %d passed (public key failed is_on_curve).\n" i
      else  (
        let computed = Curve25519.scalarmult sk pk in
        if expected = computed then Printf.printf "Curve25519 Test %d passed.\n" i
        else (Printf.printf "Curve25519 Test %d failed.\n" i;
            Printf.printf "expected secret: %s\n" (hex_of_bytes expected);
            Printf.printf "computed secret: %s\n" (hex_of_bytes computed));  
      ())) jsonl; 
  ()

let _ = main()
