open Yojson.Basic
open Yojson.Basic.Util

let digit_to_int c = match c with
  | '0'..'9' -> Char.code c - Char.code '0'
  | 'a'..'f' -> 10 + Char.code c - Char.code 'a'
  | 'A'..'F' -> 10 + Char.code c - Char.code 'A'
  | _ -> failwith "hex_to_char: invalid hex digit"

let hex_to_int (a:char) (b:char) =
  ((digit_to_int a) lsl 4 + digit_to_int b)

let int_to_hex n =
  let digits = "0123456789abcdef" in
  digits.[n lsr 4], digits.[n land 0x0f]

let int_list_of_hex (s:string) : FStar_UInt8.t Lib_Sequence.seq   =
  let n = String.length s in
  if n mod 2 <> 0 then
     failwith "string_of_hex: invalid length"
  else
    let rec aux i =
      if i >= n then
       []
      else (
       (hex_to_int s.[i] s.[i+1]) :: aux (i+2) 
      )
    in
    Lib_Sequence.of_list(aux 0)

let bytes_of_hex (s:string) : FStar_UInt8.t Lib_Sequence.seq = int_list_of_hex s

let rec hex_of_int_list (l: FStar_UInt8.t Lib_Sequence.seq) =
  let n = Lib_Sequence.length l in 
  let rec aux i = 
    if i >= n then ""
  else
    (
      let (h:FStar_UInt8.t) = Lib_Sequence.index n l i in 
      let a,b = int_to_hex h in
            Char.escaped a ^ Char.escaped b ^ hex_of_int_list l)
  in 
  aux (Prims.parse_int "0" )


let hex_of_bytes b = hex_of_int_list b

let uint32_of_int_list (l:FStar_UInt8.t Lib_Sequence.seq) =
  let n = Lib_Sequence.length l in 
  if n <> (Prims.parse_int "4") then 
    failwith "uint32_of_int_list: invalid length"
  else   
    let a = Lib_Sequence.index n l (Prims.parse_int "0") in 
    let b = Lib_Sequence.index n l (Prims.parse_int "1") in 
    let c = Lib_Sequence.index n l (Prims.parse_int "2") in 
    let d = Lib_Sequence.index n l (Prims.parse_int "3") in 
(*)  match l with
  | [a;b;c;d] ->*) a lsl 24 + b lsl 16 + c lsl 8 + d(*)
  | _ -> failwith "uint32_of_int_list: invalid length"*)

let uint32_of_hex h = uint32_of_int_list (int_list_of_hex h)

let read_bytes j n = j |> member n |> to_string |> bytes_of_hex

let read_uint32 j n = j |> member n |> to_string |> uint32_of_hex
let read_int j n = j |> member n |> to_int
let read_bool j n = j |> member n |> to_bool
