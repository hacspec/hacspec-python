(* -------------------------------------------------------------------- *)
open Syntax
open Ast

(* -------------------------------------------------------------------- *)
val piiter : (pinstr -> unit) -> pinstr -> unit
val pifold : ('a -> pinstr -> 'a) -> 'a -> pinstr -> 'a
val psfold : ('a -> pinstr -> 'a) -> 'a -> pstmt -> 'a

(* -------------------------------------------------------------------- *)
val iiter : (instr -> unit) -> instr -> unit
val ifold : ('a -> instr -> 'a) -> 'a -> instr -> 'a
val sfold : ('a -> instr -> 'a) -> 'a -> block -> 'a
