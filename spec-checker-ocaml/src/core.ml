(* -------------------------------------------------------------------- *)
include BatPervasives

(* -------------------------------------------------------------------- *)
module Big_int = BatBig_int
module Hashtbl = BatHashtbl
module Map     = BatMap
module IO      = BatIO

(* -------------------------------------------------------------------- *)
let fst_map f = function (x, y) -> (f x, y)
let snd_map f = function (x, y) -> (x, f y)

(* -------------------------------------------------------------------- *)
module Option : sig
  include module type of BatOption

  val split : ('a * 'b) option -> 'a option * 'b option
end = struct
  include BatOption

  let split (xy : ('a * 'b) option) =
    match xy with
    | None -> None, None
    | Some (x, y) -> Some x, Some y
end

(* -------------------------------------------------------------------- *)
module String : sig
  include module type of BatString

  val count : (char -> bool) -> string -> int
end = struct
  include BatString

  let count (f : char -> bool) (s : string) =
    let aout = ref 0 in
    String.iter (fun c -> if f c then incr aout) s; !aout
end

(* -------------------------------------------------------------------- *)
module Mstr = Map.Make(String)

(* -------------------------------------------------------------------- *)
module List : sig
  include module type of BatList

  type 'a pivot = 'a list * 'a * 'a list

  val pivot    : ('a -> bool) -> 'a list -> 'a pivot
  val pivoti   : (int -> 'a -> bool) -> 'a list -> 'a pivot
  val pivot_at : int -> 'a list -> 'a pivot
end = struct
  include BatList

  type 'a pivot = 'a list * 'a * 'a list

  let pivoti (f : int -> 'a -> bool) =
    let rec aux i pre s =
      match s with
      | [] -> invalid_arg "List.pivoti"
      | x :: s ->
          if f i x then
            (List.rev pre, x, s)
          else aux (i+1) (x :: pre) s
    in fun (s : 'a list) -> aux 0 [] s

  let pivot (f : 'a -> bool) (s : 'a list) =
    pivoti (fun _ -> f) s

  let pivot_at (i : int) (s : 'a list) =
    pivoti (fun j _ -> i = j) s
end

(* -------------------------------------------------------------------- *)
type uid = int

module Uid : sig
  val fresh : unit -> uid
end = struct
  let fresh () : uid =
    Oo.id (object end)
end

(* -------------------------------------------------------------------- *)
module Disposable : sig
  type 'a t

  exception Disposed

  val create  : ?cb:('a -> unit) -> 'a -> 'a t
  val get     : 'a t -> 'a
  val dispose : 'a t -> unit
end = struct
  type 'a t = ((('a -> unit) option * 'a) option) ref

  exception Disposed

  let get (p : 'a t) =
    match !p with
    | None -> raise Disposed
    | Some (_, x) -> x

  let dispose (p : 'a t) =
    let do_dispose p =
      match p with
      | Some (Some cb, x) -> cb x
      | _ -> ()
    in

    let oldp = !p in
      p := None; do_dispose oldp

  let create ?(cb : ('a -> unit) option) (x : 'a) =
    let r = ref (Some (cb, x)) in
    Gc.finalise (fun r -> dispose r) r; r
end

(* -------------------------------------------------------------------- *)
let curry   f (x, y) = f x y
let uncurry f x y = f (x, y)

let (^~) f = fun x y -> f y x

let (/>) (x : 'a option) (f : 'a -> 'b) =
  Option.map f x

let ueta (f : unit -> 'a) : 'b -> 'a =
  fun _ -> f ()
