(* -------------------------------------------------------------------- *)
type reader

(* -------------------------------------------------------------------- *)
val from_channel : name:string -> in_channel -> reader
val from_file    : string -> reader
val from_string  : string -> reader
val finalize     : reader -> unit

(* -------------------------------------------------------------------- *)
val parse_spec : reader -> Syntax.pspec
