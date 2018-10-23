(* --------------------------------------------------------------------
 * Copyright (c) - 2012--2016 - IMDEA Software Institute
 * Copyright (c) - 2012--2018 - Inria
 * Copyright (c) - 2012--2018 - Ecole Polytechnique
 *
 * Distributed under the terms of the CeCILL-C-V1 license
 * -------------------------------------------------------------------- *)

(* -------------------------------------------------------------------- *)
open Lexing

(* -------------------------------------------------------------------- *)
type t = {
  loc_fname : string;
  loc_start : int * int;
  loc_end   : int * int;
  loc_bchar : int;
  loc_echar : int;
}

(* -------------------------------------------------------------------- *)
val _dummy    : t
val make      : position -> position -> t
val oflexbuf  : lexbuf -> t
val tostring  : t -> string
val merge     : t -> t -> t
val mergeall  : t list -> t
val isdummy   : t -> bool

(* -------------------------------------------------------------------- *)
type 'a located = { pl_loc  : t; pl_data : 'a; }

val loc    : 'a located -> t
val unloc  : 'a located -> 'a
val unlocs : ('a located) list -> 'a list
val mkloc  : t -> 'a -> 'a located
val lmap   : ('a -> 'b) -> 'a located -> 'b located

(* -------------------------------------------------------------------- *)
exception LocError of t * exn

val locate_error : t -> exn -> 'a

val set_loc  : t -> ('a -> 'b) -> 'a -> 'b
val set_oloc : t option -> ('a -> 'b) -> 'a -> 'b
