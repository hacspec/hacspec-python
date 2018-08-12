(* -------------------------------------------------------------------- *)
open Core
open Location
open Syntax
open Ast

(* -------------------------------------------------------------------- *)
let pifold (f : 'a -> pinstr -> 'a) (x : 'a) (i : pinstr) =
  match unloc i with
  | PSFail _   | PSPass   | PSVarDecl _
  | PSReturn _ | PSExpr _ | PSAssign  _ -> x

  | PSIf ((_, b), ebs, ob) ->
      let bs = b :: List.map snd ebs @ Option.to_list ob in
      let bs = List.flatten bs in
      List.fold_left f x bs

  | PSWhile ((_, b), ob) | PSFor ((_, _, b), ob) ->
      let bs = List.flatten (b :: Option.to_list ob) in
      List.fold_left f x bs

  | PSDef pf ->
      List.fold_left f x pf.pf_body

(* -------------------------------------------------------------------- *)
let psfold (f : 'a -> pinstr -> 'a) (x : 'a) (s : pstmt) =
  List.fold_left f x s

(* -------------------------------------------------------------------- *)
let piiter (f : pinstr -> unit) (i : pinstr) =
  pifold (fun () -> f) () i

(* -------------------------------------------------------------------- *)
let ifold (f : 'a -> instr -> 'a) (x : 'a) (i : instr) =
  match i with
  | IFail _ | IReturn _ | IAssign _ -> x

  | IIf ((_, b), ebs, ob) ->
      let bs = b :: List.map snd ebs @ Option.to_list ob in
      let bs = List.flatten bs in
      List.fold_left f x bs

  | IWhile ((_, b), ob) | IFor ((_, _, b), ob) ->
      let bs = List.flatten (b :: Option.to_list ob) in
      List.fold_left f x bs

(* -------------------------------------------------------------------- *)
let sfold (f : 'a -> instr -> 'a) (x : 'a) (s : block) =
  List.fold_left f x s

(* -------------------------------------------------------------------- *)
let iiter (f : instr -> unit) (i : instr) =
  ifold (fun () -> f) () i
