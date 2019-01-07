open Yojson.Basic.Util
open Testutil
   
let main () =
  let json = Yojson.Basic.from_file "../../../tests/test_vectors/chacha20_test_vectors.json" in
  let jsonl = Yojson.Basic.Util.to_list json in
  List.iteri (fun i j ->
      let key = read_bytes j "key" in
      let nonce = read_bytes j  "nonce" in
      let counter = read_int j "counter" in
      let input = read_bytes j "input" in
      let output = read_bytes j "output" in
      let computed = Chacha20.chacha20_encrypt_bytes key counter nonce input in
      if output = computed then Printf.printf "Chacha20 Test %d passed.\n" i
      else (Printf.printf "Chacha20 Test %d failed.\n" i;
            Printf.printf "expected ciphertext: %s\n" (hex_of_bytes output);
            Printf.printf "computed ciphertext: %s\n" (hex_of_bytes computed));
      ()) jsonl;
  ()

let _ = main()
