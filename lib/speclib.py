from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple, Callable, Type, cast
from types import FunctionType
from random import SystemRandom as rand
from random import choices as random_string
from string import ascii_uppercase, ascii_lowercase
from math import ceil, log
from importlib import import_module
import builtins
from typeguard import typechecked
from inspect import getfullargspec
from os import environ
from inspect import getsource
from copy import copy,deepcopy

DEBUG = environ.get('HACSPEC_DEBUG')

class Error(Exception):
    pass


@typechecked
def fail(s: str) -> None:
    raise Error(s)


T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
W = TypeVar('W')
X = TypeVar('X')


@typechecked
def tuple2(T: type, U: type) -> type:
    return Tuple[T, U]


@typechecked
def tuple3(T: type, U: type, V: type) -> type:
    return Tuple[T, U, V]


@typechecked
def tuple4(T: type, U: type, V: type, W: type) -> type:
    return Tuple[T, U, V, W]


@typechecked
def tuple5(T: type, U: type, V: type, W: type, X: type) -> type:
    return Tuple[T, U, V, W, X]

@typechecked
def refine(t: type, f: Callable[[T], bool]) -> tuple2(type,Callable[[T],T]):
    def refine_check(x):
        if not isinstance(x,t) or not f(x):
            print("got :"+str(args[0]))
            print("expected : x:"+str(t)+"{"+str(f)+"}")
            fail("refinement check failed")
        return x
    return (t,refine_check)

def refine_t(t:type, f:Callable[[T], bool]) -> type:
    (t,f) = refine(t,f)
    return t

nat_t,nat = refine(int, lambda x: x >= 0)
pos_t,pos = refine(nat_t, lambda x: x > 0)


@typechecked
def range_t(min: int, max: int) -> type:
    return refine_t(int, lambda x: x >= min and x < max)


# TODO: make this actually do something.
@typechecked
def contract(t: type, pre: Callable[..., bool], post: Callable[..., bool]) -> type:
    return t

@typechecked
def contract3(pre: Callable[..., bool], post: Callable[..., bool]) -> FunctionType:
    @typechecked
    def decorator(func: Callable[..., Any]) -> Any:
        # **kwargs are not allowed in hacspec.
        def wrapper(*args):
            pr = pre(*args)
            if not pr:
                fail("Precondition for " + func.__name__ + " failed.")
            res = func(*args)
            unpacked_args = list(args)
            unpacked_args.append(res)
            po = post(*unpacked_args)
            if not po:
                fail("Postcondition for " + func.__name__ + " failed.")
            return res
        return wrapper
    return decorator

class _natmod:
    @typechecked
    def __init__(self, x: Union[int,'_natmod'], modulus: int) -> None:
        if modulus < 1:
            fail("cannot create _natmod with modulus <= 0")
        else:
            xv = 0
            if isinstance(x,_natmod):
                xv = x.v
            else:
                xv = x
            self.modulus = modulus
            self.v = xv % modulus 

    @typechecked
    def __str__(self) -> str:
        return hex(self.v)

    @typechecked
    def __repr__(self) -> str:
        return hex(self.v)

    @typechecked
    def __int__(self) -> int:
        return self.v

    @typechecked
    def __eq__(self, other) -> bool:
        if not isinstance(other, _natmod):
            fail("You can only compare two natmods.")
        return (self.modulus == other.modulus and
                self.v == other.v)

    @typechecked
    def __int__(self) -> int:
        return self.v

    @typechecked
    def __add__(self, other: '_natmod') -> '_natmod':
        if not isinstance(other, _natmod) or \
           other.__class__ != self.__class__ or \
           other.modulus != self.modulus:
            fail("+ is only valid for two _natmod of same modulus.")
        res = copy(self)
        res.v = (res.v+other.v) % res.modulus
        return res

    @typechecked
    def __sub__(self, other: '_natmod') -> '_natmod':
        if not isinstance(other, _natmod) or \
           other.__class__ != self.__class__ or \
           other.modulus != self.modulus:
            fail("- is only valid for two _natmod of same modulus.")
        res = copy(self)
        res.v = (res.v-other.v) % res.modulus
        return res

    @typechecked
    def __mul__(self, other: '_natmod') -> '_natmod':
        if not isinstance(other, _natmod) or \
           other.__class__ != self.__class__ or \
           other.modulus != self.modulus:
            fail("* is only valid for two _natmod of same modulus.")
        res = copy(self)
        res.v = (res.v*other.v) % res.modulus
        return res

    @typechecked
    def __pow__(self, other: nat_t) -> '_natmod':
        if not isinstance(other, nat_t) or other < 0:
            fail("* is only valid for two positive exponents")
        res = copy(self)
        res.v = pow(res.v,other,res.modulus)
        return res

    @staticmethod
    @typechecked
    def to_int(x: '_natmod') -> nat_t:
        if not isinstance(x, _natmod):
            fail("to_int is only valid for _natmod.")
        return x.v

    @staticmethod
    @typechecked
    def to_nat(x: '_natmod') -> nat_t:
        if not isinstance(x, _natmod):
            fail("to_nat is only valid for _natmod.")
        return x.v


class _uintn(_natmod):
    @typechecked
    def __init__(self, x: Union[int,'_uintn'], bits: int) -> None:
        modulus = 1 << bits
        _natmod.__init__(self,x,modulus)
        self.bits = bits

    def __eq__(self, other) -> bool:
        if not isinstance(other, _uintn):
            fail("You can only compare two uints.")
        return (self.bits == other.bits and
                self.v == other.v)

    @staticmethod
    @typechecked
    def num_bits(x: '_uintn') -> int:
        if not isinstance(x, _uintn):
            fail("num_bits is only valid for _uintn.")
        return x.bits

    @typechecked
    def __inv__(self) -> '_uintn':
        res = copy(self)
        res.v = ~res.v
        return res

    @typechecked
    def __invert__(self) -> '_uintn':
        res = copy(self)
        res.v = ~res.v
        return res

    @typechecked
    def __or__(self, other: '_uintn') -> '_uintn':
        if not isinstance(other, _uintn) or \
           other.__class__ != self.__class__ or \
           other.bits != self.bits:
            fail("| is only valid for two _uintn of same bits.")
        res = copy(self)
        res.v = res.v | other.v
        return res

    @typechecked
    def __and__(self, other: '_uintn') -> '_uintn':
        if not isinstance(other, _uintn) or \
           other.__class__ != self.__class__ or \
           other.bits != self.bits:
            fail("& is only valid for two _uintn of same bits.")
        res = copy(self)
        res.v = res.v & other.v
        return res

    @typechecked
    def __xor__(self, other: '_uintn') -> '_uintn':
        if not isinstance(other, _uintn) or \
           other.__class__ != self.__class__ or \
           other.bits != self.bits:
            fail("^ is only valid for two _uintn of same bits.")
        res = copy(self)
        res.v = res.v ^ other.v
        return res


    @typechecked
    def __lshift__(self, other: int) -> '_uintn':
        if not isinstance(other, int) or other < 0 or other > self.bits:
            fail("lshift value has to be an int between 0 and bits")
        res = copy(self)
        res.v = (res.v << other) & (res.modulus - 1)
        return res

    @typechecked
    def __rshift__(self, other: int) -> '_uintn':
        if not isinstance(other, int) or other < 0 or other > self.bits:
            fail("lshift value has to be an int between 0 and bits")
        res = copy(self)
        res.v = (res.v >> other) & (res.modulus - 1)
        return res

    @typechecked
    def __getitem__(self, key: Union[int, slice]) -> '_uintn':
        try:
            if isinstance(key, slice):
                return _uintn(self.v >> key.start,
                              key.stop - key.start)
            else:
                return _uintn(self.v >> key,1)
        except:
            print('_uintn content:', self.v)
            print('desired index:', key)
            fail('_uintn bit access error')

    @typechecked
    def __getslice__(self, i: int, j: int) -> '_uintn':
        return _uintn(self.v >> i, j - i)

    @staticmethod
    @typechecked
    def rotate_left(x: '_uintn', other: int) -> '_uintn':
        if not isinstance(x, _uintn) or \
           not isinstance(other, int) or \
           other <= 0 or other >= x.bits:
            fail("rotate_left value has to be an int strictly between 0 and bits")
        return (x << other) | (x >> (x.bits - other))

    @staticmethod
    @typechecked
    def rotate_right(x: '_uintn', other: int) -> '_uintn':
        if not isinstance(x, _uintn) or \
           not isinstance(other, int) or \
           other <= 0 or other >= x.bits:
            fail("rotate_left value has to be an int strictly between 0 and bits")
        return (x >> other) | (x << (x.bits - other))

    @staticmethod
    @typechecked
    def reverse(x: '_uintn') -> '_uintn':
        if not isinstance(x, _uintn): 
            fail("reverse only works for _uintn")
        b = '{:0{width}b}'.format(x.v, width=bits)
        res = copy(x)
        res.v = int(b[::-1], 2)
        return res

    @staticmethod
    @typechecked
    def get_bit(x:'_uintn', index:int):
        if isinstance(x,_uintn) and isinstance(index,int) \
           and index >= 0 and index < x.bits:
            return x[index]
        else:
            fail("get_bit index has to be an int between 0 and bits - 1")

    @staticmethod
    @typechecked
    def set_bit(x:'_uintn', index:int, value:int):
        if isinstance(x,_uintn) and isinstance(index,int) \
           and index >= 0 and index < x.bits \
           and value >= 0 and value < 2:
            tmp1 = ~ (_uintn(1,x.bits) << index)
            tmp2 = _uintn(value,x.bits) << index
            return (x & tmp1) | tmp2
        else:
            fail("set_bit index has to be an int between 0 and bits - 1")

    @staticmethod
    @typechecked
    def set_bits(x:'_uintn', start:int, end:int, value:'_uintn'):
        if isinstance(x,_uintn) and isinstance(start,int) \
           and isinstance(end,int) and isinstance(value,_uintn) \
           and start >= 0 and start <= end \
           and end <= x.bits and start < x.bits \
           and value.bits == end - start:
            tmp1 = ~ (_uintn((1 << (end - start)) - 1,x.bits) << start)
            tmp2 = _uintn(value,x.bits) << start
            return (x & tmp1) | tmp2
        else:
            fail("set_bits has to be an interval between 0 and bits - 1")


def uintn_t(bits:int):
    return refine_t(_uintn,lambda x: x.bits == bits)
uintn = _uintn

def natmod_t(modulus:int):
    return refine_t(_natmod,lambda x: x.modulus == modulus)
natmod = _natmod

bitvector_t = uintn_t
bitvector   = uintn

class bit(_uintn):
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,1)
bit_t = uintn_t(1)

class uint8(_uintn):
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,8)
uint8_t = uintn_t(8)

class uint16(_uintn):
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,16)
uint16_t = uintn_t(16)

class uint32(_uintn):
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,32)
uint32_t = uintn_t(32)

class uint64(_uintn):
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,64)
uint64_t = uintn_t(64)

class uint128(_uintn):
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,128)
uint128_t = uintn_t(128)


class _array(Generic[T]):
    @typechecked
    def __init__(self, x: Union[Sequence[T], List[T], '_array[T]']) -> None:
        if (not isinstance(x, Sequence)) and (not isinstance(x, _array)) and (not isinstance(x,List)):
            fail("_array() takes a list or sequence or _array as first argument.")
        self.l = list(x)
        self.len = len(self.l)

    @typechecked
    def __len__(self) -> int:
        return self.len

    @typechecked
    def __str__(self) -> str:
        return str(self.l)

    @typechecked
    def __repr__(self) -> str:
        return repr(self.l)

    @typechecked
    def __iter__(self) -> Iterator[T]:
        return iter(self.l)

    @typechecked
    def __eq__(self, other: '_array[T]') -> bool:
        if isinstance(other, _array):
            return self.l == other.l
        fail("_array.__eq__ only works on two _arrays.")

    @typechecked
    def __ne__(self, other: '_array[T]') -> bool:
        if isinstance(other, _array):
            return self.l != other.l
        fail("_array.__ne__ only works on two _arrays.")

    @typechecked
    def __getitem__(self, key: Union[int, slice]) -> Union['_array[T]', T]:
        try:
            if isinstance(key, slice):
                return _array(self.l[key.start:key.stop])
            elif isinstance(key,int) and key >= 0 and key < self.len:
                return self.l[key]
        except:
            print('array access error:')
            print('array content:', self.l)
            print('array index:', key)
            fail('array index error')

    @typechecked
    def __getslice__(self, i: int, j: int) -> '_array[T]':
        if i >= 0 and i < self.len and \
           i <= j and j <= self.len:
            return _array(self.l[i:j])

    @typechecked
    def __setitem__(self, key: Union[int, slice], v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v
        else:
            self.l[key] = v

    @staticmethod
    @typechecked
    def create(l: int, default:T) -> '_array[T]':
        res = _array([default] * l)
        return res


    @staticmethod
    @typechecked
    def length(a: '_array[T]') -> int:
        if not isinstance(a, _array):
            fail("array.length takes a _array.")
        return len(a)

    @staticmethod
    @typechecked
    def copy(x: '_array[T]') -> '_array[T]':
        return deepcopy(x)

    @staticmethod
    @typechecked
    def concat(x: '_array[T]', y: '_array[T]') -> '_array[T]':
        res = _array(x.l[:]+y.l[:])
        return res

    @staticmethod
    @typechecked
    def zip(x: '_array[T]', y: '_array[U]') -> '_array[tuple2(T,U)]':
        return _array(list(zip(x.l, y.l)))

    @staticmethod
    @typechecked
    def enumerate(x: '_array[T]') -> '_array[tuple2(int,T)]':
        return _array(list(enumerate(x.l)))

    @staticmethod
    @typechecked
    def split_blocks(a: '_array[T]', blocksize: int) -> 'Tuple[_array[_array[T]],_array[T]]':
        if not isinstance(a, _array):
            fail("split_blocks takes a _array as first argument.")
        if not isinstance(blocksize, int):
            fail("split_blocks takes an int as second argument.")
        nblocks = array.length(a) // blocksize
        rem = array.length(a) % blocksize
        blocks = _array([a[x*blocksize:(x+1)*blocksize]
                          for x in range(nblocks)])
        last = _array(a[array.length(a)-rem:array.length(a)])
        return blocks, last

    @staticmethod
    @typechecked
    def concat_blocks(blocks: '_array[_array[T]]', last: '_array[T]') -> '_array[T]':
        res = array.concat(_array([b for block in blocks for b in block]),last)
        return res

    @staticmethod
    @typechecked
    def map(f: Callable[[T], U], a: '_array[T]') -> '_array[U]':
        return _array(list(map(f, a.l)))

    @staticmethod
    @typechecked
    def create_random(l: nat_t, t: Type[_uintn]) -> '_array[_uintn]':
        if not isinstance(l, nat_t):
            fail("array.create_random's first argument has to be of type nat_t.")
        r = rand()
        x = t(0)
        return _array(list([t(r.randint(0, x.max)) for _ in range(0, l)]))


def vlarray_t(t:type):
    return refine_t(_array,lambda x: all(isinstance(z,t) for z in x))
vlarray = _array

def array_t(t: type, l:int):
   return refine_t(vlarray_t(t),lambda x: x.len == l)
array = _array

vlbytes_t = vlarray_t(uint8_t)
def bytes_t(l:int):
    return array_t(uint8_t,l)


class bytes(_array):
    @staticmethod
    @typechecked
    def from_ints(x: List[int]) -> 'vlbytes_t':
        res = vlbytes_t([uint8(i) for i in x])
        return res

    @staticmethod
    @typechecked
    def concat_bytes(blocks: '_array[vlbytes_t]') -> 'vlbytes_t':
        concat = [b for block in blocks for b in block]
        return vlbytes_t(concat)

    @staticmethod
    @typechecked
    def from_hex(x: str) -> 'vlbytes_t':
        return vlbytes_t([uint8(int(x[i:i+2], 16)) for i in range(0, len(x), 2)])

    @staticmethod
    @typechecked
    def to_hex(a: 'vlbytes_t') -> str:
        return "".join(['{:02x}'.format(uintn.to_int(x)) for x in a])

    @staticmethod
    @typechecked
    def from_nat_le(x: int, l: int=0) -> 'vlbytes_t':
        if not isinstance(x, int):
            fail("bytes.from_nat_le's argument has to be of type nat, not "+str(type(x)))
        b = x.to_bytes((x.bit_length() + 7) // 8, 'little') or b'\0'
        pad = _array([uint8(0) for i in range(0, max(0, l-len(b)))])
        result = vlbytes_t([uint8(i) for i in b])
        return vlbytes_t(array.concat(pad, result))


    @staticmethod
    @typechecked
    def to_nat_le(x: 'vlbytes_t') -> nat_t:
        b = builtins.bytes([uintn.to_int(u) for u in x])
        return int.from_bytes(b, 'little')

    @staticmethod
    @typechecked
    def from_nat_be(x: int, l: int=0) -> 'vlbytes_t':
        if not isinstance(x, int):
            fail("bytes.from_nat_be's first argument has to be of type nat_t.")
        if not isinstance(l, int):
            fail("bytes.from_nat_be's second argument has to be of type nat_t.")
        b = x.to_bytes((x.bit_length() + 7) // 8, 'big') or b'\0'
        pad = _array([uint8(0) for i in range(0, max(0, l-len(b)))])
        result = _array([uint8(i) for i in b])
        return vlbytes_t(array.concat(pad, result))

    @staticmethod
    @typechecked
    def to_nat_be(x: 'vlbytes_t') -> nat_t:
        b = builtins.bytes([uintn.to_int(u) for u in x])
        return int.from_bytes(b, 'big')

    @staticmethod
    @typechecked
    def from_uintn_le(x: uintn_t) -> 'vlbytes_t':
        nbytes = (x.bits - 1) // 8 + 1
        by = bytes.create(nbytes,uint8(0))
        xv = uintn.to_nat(x)
        for i in range(nbytes):
            by[i] = uint8(xv & 255)
            xv = xv >> 8
        return by

    @staticmethod
    @typechecked
    def to_uintn_le(x: 'vlbytes_t') -> uintn_t:
        nbits = 8 * bytes.length(x)
        xv = uintn(0,nbits)
        for i in range(bytes.length(x)):
            xv += uintn(x[i],nbits) << (i * 8)
        return xv

    @staticmethod
    @typechecked
    def from_uintn_be(x: uintn_t) -> 'vlbytes_t':
        nbytes = (x.bits - 1) // 8 + 1
        by = bytes.create(nbytes,uint8(0))
        xv = uintn.to_nat(x)
        for i in range(nbytes):
            by[nbytes-i-1] = uint8(xv)
            xv = xv // 256
        return by

    @staticmethod
    @typechecked
    def to_uintn_be(x: 'vlbytes_t') -> uintn_t:
        nbits = 8 * bytes.length(x)
        xv = uintn(0,nbits)
        nbytes = bytes.length(x)
        for i in range(nbytes):
            xv += uintn(x[nbytes - i - 1],nbits) << (i * 8)
        return xv

    @staticmethod
    @typechecked
    def from_uintns_le(x: 'vlarray_t(uintn_t)') -> 'vlbytes_t':
        by = _array([bytes.from_uintn_le(i) for i in x])
        return bytes.concat_bytes(by)

    @staticmethod
    @typechecked
    def from_uintns_be(x: 'vlarray_t(uintn_t)') -> 'vlbytes_t':
        by = _array([bytes.from_uintn_be(i) for i in x])
        return bytes.concat_bytes(by)

    @staticmethod
    @typechecked
    def to_uintns_le(x: 'vlbytes_t',bits:int) -> vlarray_t(uintn_t):
        if bits % 8 != 0 or len(x) * 8 % bits != 0:
            fail("bytearray length not a multiple of bits//8")
        nums, x = array.split_blocks(x, bits//8)
        return(_array([bytes.to_uintn_le(i) for i in nums]))

    @staticmethod
    @typechecked
    def to_uintns_be(x: 'vlbytes_t',bits:int) -> vlarray_t(uintn_t):
        if bits % 8 != 0 or len(x) * 8 % bits != 0:
            fail("bytearray length not a multiple of bits/8")
        nums, x = array.split_blocks(x, bits//8)
        return(_array([bytes.to_uintn_be(i) for i in nums]))

    @staticmethod
    @typechecked
    def to_uint16_le(x: 'vlbytes_t') -> uint16_t:
        return uint16(bytes.to_uintn_le(x))
    @staticmethod
    @typechecked
    def to_uint32_le(x: 'vlbytes_t') -> uint32_t:
        return uint32(bytes.to_uintn_le(x))
    @staticmethod
    @typechecked
    def to_uint64_le(x: 'vlbytes_t') -> uint64_t:
        return uint64(bytes.to_uintn_le(x))
    @staticmethod
    @typechecked
    def to_uint128_le(x: 'vlbytes_t') -> uint128_t:
        return uint128(bytes.to_uintn_le(x))
    @staticmethod
    @typechecked
    def to_uint16_be(x: 'vlbytes_t') -> uint16_t:
        return uint16(bytes.to_uintn_be(x))
    @staticmethod
    @typechecked
    def to_uint32_be(x: 'vlbytes_t') -> uint32_t:
        return uint32(bytes.to_uintn_be(x))
    @staticmethod
    @typechecked
    def to_uint64_be(x: 'vlbytes_t') -> uint64_t:
        return uint64(bytes.to_uintn_be(x))
    @staticmethod
    @typechecked
    def to_uint128_be(x: 'vlbytes_t') -> uint128_t:
        return uint128(bytes.to_uintn_be(x))

    @staticmethod
    @typechecked
    def from_uint16_le(x: 'uint16_t') -> vlbytes_t:
        return bytes.from_uintn_le(x)
    @staticmethod
    @typechecked
    def from_uint32_le(x: 'uint32_t') -> vlbytes_t:
        return bytes.from_uintn_le(x)
    @staticmethod
    @typechecked
    def from_uint64_le(x: 'uint64_t') -> vlbytes_t:
        return bytes.from_uintn_le(x)
    @staticmethod
    @typechecked
    def from_uint128_le(x: 'uint128_t') -> vlbytes_t:
        return bytes.from_uintn_le(x)
    @staticmethod
    @typechecked
    def from_uint16_be(x: 'uint16_t') -> vlbytes_t:
        return bytes.from_uintn_be(x)
    @staticmethod
    @typechecked
    def from_uint32_be(x: 'uint32_t') -> vlbytes_t:
        return bytes.from_uintn_be(x)
    @staticmethod
    @typechecked
    def from_uint64_be(x: 'uint64_t') -> vlbytes_t:
        return bytes.from_uintn_be(x)
    @staticmethod
    @typechecked
    def from_uint128_be(x: 'uint128_t') -> vlbytes_t:
        return bytes.from_uintn_be(x)

    @staticmethod
    @typechecked
    def to_uint16s_le(x: 'vlbytes_t') -> _array[uint16_t]:
        return array.map(uint16,bytes.to_uintns_le(x,16))
    @staticmethod
    @typechecked
    def to_uint32s_le(x: 'vlbytes_t') -> _array[uint32_t]:
        return array.map(uint32,bytes.to_uintns_le(x,32))
    @staticmethod
    @typechecked
    def to_uint64s_le(x: 'vlbytes_t') -> _array[uint64_t]:
        return array.map(uint64,bytes.to_uintns_le(x,64))
    @staticmethod
    @typechecked
    def to_uint128s_le(x: 'vlbytes_t') -> _array[uint128_t]:
        return array.map(uint128,bytes.to_uintns_le(x,128))
    @staticmethod
    @typechecked
    def to_uint16s_be(x: 'vlbytes_t') -> _array[uint16_t]:
        return array.map(uint16,bytes.to_uintns_be(x,16))
    @staticmethod
    @typechecked
    def to_uint32s_be(x: 'vlbytes_t') -> _array[uint32_t]:
        return array.map(uint32,bytes.to_uintns_be(x,32))
    @staticmethod
    @typechecked
    def to_uint64s_be(x: 'vlbytes_t') -> _array[uint64_t]:
        return array.map(uint64,bytes.to_uintns_be(x,64))
    @staticmethod
    @typechecked
    def to_uint128s_be(x: 'vlbytes_t') -> _array[uint128_t]:
        return array.map(uint128,bytes.to_uintns_be(x,128))

    @staticmethod
    @typechecked
    def from_uint16s_le(x: '_array[uint16_t]') -> vlbytes_t:
        return bytes.from_uintns_le(x)
    @staticmethod
    @typechecked
    def from_uint32s_le(x: '_array[uint32_t]') -> vlbytes_t:
        return bytes.from_uintns_le(x)
    @staticmethod
    @typechecked
    def from_uint64s_le(x: '_array[uint64_t]') -> vlbytes_t:
        return bytes.from_uintns_le(x)
    @staticmethod
    @typechecked
    def from_uint128s_le(x: '_array[uint128_t]') -> vlbytes_t:
        return bytes.from_uintns_le(x)
    @staticmethod
    @typechecked
    def from_uint16s_be(x: '_array[uint16_t]') -> vlbytes_t:
        return bytes.from_uintns_be(x)
    @staticmethod
    @typechecked
    def from_uint32s_be(x: '_array[uint32_t]') -> vlbytes_t:
        return bytes.from_uintns_be(x)
    @staticmethod
    @typechecked
    def from_uint64s_be(x: '_array[uint64_t]') -> vlbytes_t:
        return bytes.from_uintns_be(x)
    @staticmethod
    @typechecked
    def from_uint128s_be(x: '_array[uint128_t]') -> vlbytes_t:
        return bytes.from_uintns_be(x)

    @staticmethod
    @typechecked
    def create_random_bytes(len: nat) -> 'vlbytes_t':
        r = rand()
        return vlbytes_t(list([uint8(r.randint(0, 0xFF)) for _ in range(0, len)]))

class _vector(_array[T]):
    @staticmethod
    @typechecked
    def create(l: int, default:T) -> '_vector[T]':
        res = _vector([default] * l)
        return res

    @typechecked
    def __add__(self, other: '_vector') -> '_vector':
        if not isinstance(other, _vector) or \
           other.__class__ != self.__class__ or \
           other.len != self.len:
            fail("+ is only valid for two _vectors of same length")
        res = deepcopy(self)
        res.l = [x + y for (x,y) in zip(self.l,other.l)]
        return res            

    @typechecked
    def __sub__(self, other: '_vector') -> '_vector':
        if not isinstance(other, _vector) or \
           other.__class__ != self.__class__ or \
           other.len != self.len:
            fail("/ is only valid for two _vectors of same length")
        res = deepcopy(self)
        res.l = [x - y for (x,y) in zip(self.l,other.l)]
        return res            

    @typechecked
    def __mul__(self, other: '_vector') -> '_vector':
        if not isinstance(other, _vector) or \
           other.__class__ != self.__class__ or \
           other.len != self.len:
            fail("* is only valid for two _vectors of same length")
        res = deepcopy(self)
        res.l = [x * y for (x,y) in zip(self.l,other.l)]
        return res            

def vector_t(t:type,len:nat):
    return array_t(t,len)
vector = _vector

class _matrix(_vector[_vector[T]]):
    @typechecked
    def __init__(self, x: Union[Sequence[Sequence[T]],List[List[T]],_array[_array[T]]], rows:int, columns:int) -> None:
        super().__init__(self,[_vector(r) for r in x])
        if all(r.len == columns for r in self.l) and self.len == rows:
            self.rows = rows
            self.cols = columns
        else:
            fail("matrix with wrong number of rows and columns")
            
    @staticmethod
    @typechecked
    def create(r: int, c:int, default:T) -> '_matrix[T]':
        col = _vector(c,default)
        mat = _vector(r,c)
        for i in range(r):
            mat[i] = _vector(c,default)
        return mat

    @staticmethod
    @typechecked
    def map(f: Callable[[T], U], a: '_matrix[T]') -> '_matrix[U]':
        return _vector([array.map(f,x) for x in a.l])

    
def matrix_t(t:type,rows:nat,columns:nat):
    return vector_t(vector_t(t,columns),rows)

matrix = _matrix
