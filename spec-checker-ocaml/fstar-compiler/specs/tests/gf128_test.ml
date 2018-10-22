open Yojson.Basic.Util
open Testutil

let main() =
  let json = Yojson.Basic.from_file "../../../tests/test_vectors/gf128_test_vectors.json" in
  let jsonl = Yojson.Basic.Util.to_list json in
  List.iteri (fun i j ->
      let msg = read_bytes j "input" in
      let key = read_bytes j "key" in
      let output = read_bytes j "output" in
      let computed = Gf128.gmac msg key in
      if output = computed then Printf.printf "GF128 Test %d passed.\n" i
      else (Printf.printf "GF128 Test %d failed.\n" i;
            Printf.printf "expected tag: %s\n" (hex_of_bytes output);
            Printf.printf "computed tag: %s\n" (hex_of_bytes computed));
      ()) jsonl;
  ()

let _ = main()
