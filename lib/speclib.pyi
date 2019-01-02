# We assume the following builtin functions and types
#
# fail: str -> None
# tuple_t: t1,t2,...,tn -> type
# option_t: t -> type
# vlarray_t: t -> type
# refine_t: t,f -> type         treated as t
# contract_t: t,f,g -> type     treated as t
# numeric types:
# int
# natmod_t: m -> type
# uintn_t: bits -> type
# vector_t: t,l -> type
# matrix_t: t,r,c -> type
# range_t: x,y -> type

nat_t = int
pos_t = int
bit_t = uintn_t(1)
uint8_t = uintn_t(8)
uint16_t = uintn_t(16)
uint32_t = uintn_t(32)
uint64_t = uintn_t(64)
uint128_t = uintn_t(128)
vlbytes_t = vlarray_t(uint8_t)

#operators
# +, - , *: natmod_t, natmod_t -> natmod_t
#         : uintn_t(i), uintn_t(i) -> uintn_t(i)
#         : int,int -> int
#         : vector_t(t),vector_t(t) -> vector_t(t)
#         : matrix_t(t),matrix_t(t) -> matrix_t(t)
# **      : natmod_t, int -> natmod_t
#         : uintn_t(i), int -> uintn_t(i)
#         : int,int -> int
# <<,>>   : natmod_t, int -> natmod_t
#         : uintn_t(i), int -> uintn_t(i)
#         : int,int -> int
# ~       : uintn_t(i), int -> uintn_t(i)
# |,&,^   : uintn_t(i), int -> uintn_t(i)
# []      : uintn_t(i), int -> bit
#         : vlarray_t(t), int -> t
# [ : ]   : uintn_t(i), i:int, j:int -> uintn_t(j-i)

#decl natmod(x:int,m:int) -> natmod_t(m)
#decl natmod.to_int(x:natmod_t) -> int
#decl uintn.rotate_left(x:uintn_t(i),r:int) -> uintn_t(i)
#decl uintn.rotate_right(x:uintn_t(i),r:int) -> uintn_t(i)
#decl uintn.set_bits(x:uintn_t(i),start:int,end:int,value:uintn_t(end-start)) -> uintn_t(i)
#
#decl array.create(l:int,d:t) -> array_t(t,l)
#decl array.empty() -> array_t(t,0)
#decl array.singleton(d:t) -> array_t(t,1)
#decl array.createi(l:int,f:int->t) -> array_t(t,l)
#decl array.length(a) -> int
#decl array.copy(x:array_t(t,l)) -> array_t(t,l)
#decl array.concat(x:array_t(t,l),y:array_t(t,m)) -> array_t(t,l+m)
#decl array.split(x:array_t(t,l),i:int) -> tuple_t(array_t(t,i),array_t(t,l-i))
#decl array.zip(x:array_t(t,l),y:array_t(u,l)) -> array_t(tuple_t(t,u),l)
#decl array.enumerate(x:array_t(t,l)) -> array_t(tuple_t(int,t),l)
#decl array.split_blocks(x:array_t(t,l),b:int) -> array_t(array_t(t,b),l/b)
#decl array.concat_blocks(x:array_t(array_t(t,b),n)) -> array_t(t,b*n)
#decl array.map(f:t -> u,x:array_t(t,l)) -> array_t(u,l)
#
#decl bytes.from_nat_le(x:int) -> vlbytes_t
#decl bytes.to_nat_le(x:vlbytes_t) -> int
#decl bytes.from_nat_be(x:int) -> vlbytes_t
#decl bytes.to_nat_be(x:vlbytes_t) -> int
#
#decl bytes.from_uintn_le(x:uintn_t(i)) -> vlbytes_t
#decl bytes.to_uintn_le(x:vlbytes_t) -> uintn_t(i)
#decl bytes.from_uintn_be(x:uintn_t(i)) -> vlbytes_t
#decl bytes.to_uintn_be(x:vlbytes_t) -> uintn_t(i)
#
#decl bytes.from_uintns_le(x:vlarray_t(uintn_t(i))) -> vlbytes_t
#decl bytes.to_uintns_le(x:vlbytes_t) -> vlarray_t(uintn_t(i))
#decl bytes.from_uintns_be(x:vlarray_t(uintn_t(i))) -> vlbytes_t
#decl bytes.to_uintns_be(x:vlbytes_t) -> vlarray_t(uintn_t(i))
