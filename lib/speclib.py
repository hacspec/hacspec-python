from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple, Callable, Type, cast
from types import FunctionType
from random import SystemRandom as rand
from random import choices as random_string
from string import ascii_uppercase, ascii_lowercase
from math import ceil, log, floor
from importlib import import_module
import builtins
from typeguard import typechecked
from inspect import getfullargspec
from os import environ
from inspect import getsource
from copy import copy

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
def tuple_t(*args) -> type:
    if len(args) == 1:
        return Tuple[args[0]]
    elif len(args) == 2:
        return Tuple[args[0],args[1]]
    elif len(args) == 3:
        return Tuple[args[0],args[1],args[2]]
    elif len(args) == 4:
        return Tuple[args[0],args[1],args[2],args[3]]
    elif len(args) == 5:
        return Tuple[args[0],args[1],args[2],args[3],args[4]]
    elif len(args) == 6:
        return Tuple[args[0],args[1],args[2],args[3],args[4],args[5]]
    else:
        fail("only implemented tuples up to size 6")

class _result(Generic[T]):
    @typechecked
    def __init__(self, is_valid:bool, value:Union[T,str]) -> None:
        self.is_valid = True;
        self.value = value

    @staticmethod
    @typechecked
    def retval(v:T) -> '_result[T]':
        return _result(True,v)    

    @staticmethod
    @typechecked
    def error(v:str) -> '_result[T]':
        return _result(False,v)

    @staticmethod
    @typechecked
    def is_valid(a:'_result[T]') -> bool:
        return a.is_valid

    @staticmethod
    @typechecked
    def get_value(a:'_result[T]') -> T:
        if a.is_valid:
            return a.value
        else:
            fail ("cannot call get_value on error result")

    @staticmethod
    @typechecked
    def get_error(a:'_result[T]') -> T:
        if a.is_valid:
            fail ("cannot call get_error on valid result")
        else:
            return a.value

result = _result
@typechecked
def result_t(T: type):
    return _result

@typechecked
def option_t(T: type) -> Union[T, None]:
    return Union[T, None]

@typechecked
def refine(t: type, f: Callable[[T], bool]) -> Tuple[type,Callable[[T],T]]:
    def refine_check(x):
        if not isinstance(x,t) or not f(x):
            print("got :"+str(x))
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
    __slots__ = ['v', 'modulus']
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
            print(type(other))
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
        return _natmod.set_val(self, (self.v+other.v) % self.modulus)

    @typechecked
    def __sub__(self, other: '_natmod') -> '_natmod':
        if not isinstance(other, _natmod) or \
           other.__class__ != self.__class__ or \
           other.modulus != self.modulus:
            fail("- is only valid for two _natmod of same modulus.")
        return _natmod.set_val(self, (self.modulus + self.v - other.v) % self.modulus)

    @typechecked
    def __mul__(self, other: '_natmod') -> '_natmod':
        if not isinstance(other, _natmod) or \
           other.__class__ != self.__class__ or \
           other.modulus != self.modulus:
            fail("* is only valid for two _natmod of same modulus.")
        return _natmod.set_val(self, (self.v*other.v) % self.modulus)

    @typechecked
    def __pow__(self, other: nat_t) -> '_natmod':
        if not isinstance(other, nat_t) or other < 0:
            fail("* is only valid for two positive exponents")
        if other == 0:
            return _natmod.set_val(self, 1)
        elif other == 1:
            return copy(self)
        if other == 2:
            return self * self
        return _natmod.set_val(self, pow(self.v,other,self.modulus))


    @staticmethod
    @typechecked
    def to_int(x: '_natmod') -> nat_t:
        if not isinstance(x, _natmod):
            fail("to_int is only valid for _natmod.")
        return x.v
    
    @staticmethod
    @typechecked
    def set_val(x: '_natmod',v:int) -> '_natmod':
        result = x.__class__.__new__(x.__class__)
        for s in x.__slots__:
            setattr(result, s, getattr(x, s))
        result.v = v
        return result

    def __copy__(self):
        result = self.__class__.__new__(self.__class__)
        for s in self.__slots__:
            setattr(result, s, copy(getattr(self, s)))
        return result

    @staticmethod
    @typechecked
    def to_nat(x: '_natmod') -> nat_t:
        if not isinstance(x, _natmod):
            fail("to_nat is only valid for _natmod.")
        return x.v


class _uintn(_natmod):
    __slots__ = ['v', 'modulus', 'bits']
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
        return _uintn.set_val(self,~self.v)

    @typechecked
    def __invert__(self) -> '_uintn':
        return _uintn.set_val(self,~self.v)

    @typechecked
    def __or__(self, other: '_uintn') -> '_uintn':
        if not isinstance(other, _uintn) or \
           other.__class__ != self.__class__ or \
           other.bits != self.bits:
            fail("| is only valid for two _uintn of same bits.")
        return _uintn.set_val(self,self.v | other.v)

    @typechecked
    def __and__(self, other: '_uintn') -> '_uintn':
        if not isinstance(other, _uintn) or \
           other.__class__ != self.__class__ or \
           other.bits != self.bits:
            fail("& is only valid for two _uintn of same bits.")
        return _uintn.set_val(self,self.v & other.v)


    @typechecked
    def __xor__(self, other: '_uintn') -> '_uintn':
        if not isinstance(other, _uintn) or \
           other.__class__ != self.__class__ or \
           other.bits != self.bits:
            fail("^ is only valid for two _uintn of same bits.")
        return _uintn.set_val(self,self.v ^ other.v)


    @typechecked
    def __lshift__(self, other: int) -> '_uintn':
        if not isinstance(other, int) or other < 0 or other > self.bits:
            fail("lshift value has to be an int between 0 and bits")
        return _uintn.set_val(self,self.v << other & (self.modulus - 1))

    @typechecked
    def __rshift__(self, other: int) -> '_uintn':
        if not isinstance(other, int) or other < 0 or other > self.bits:
            fail("lshift value has to be an int between 0 and bits")
        return _uintn.set_val(self,self.v >> other & (self.modulus - 1))


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
        b = '{:0{width}b}'.format(x.v, width=x.bits)
        return _uintn.set_val(x,int(b[::-1],2))

    @staticmethod
    @typechecked
    def bit_count(x:'_uintn') -> int:
        if isinstance(x,_uintn):
            cnt = 0
            for i in range(x.bits):
                cnt += uintn.to_int(x[i])
            return cnt
        else:
            fail("bit_count arg must be a uintn")

    @staticmethod
    @typechecked
    def get_bit(x:'_uintn', index:int) -> '_uintn':
        if isinstance(x,_uintn) and isinstance(index,int) \
           and index >= 0 and index < x.bits:
            return x[index]
        else:
            fail("get_bit index has to be an int between 0 and bits - 1")

    
    @staticmethod
    @typechecked
    def set_bit(x:'_uintn', index:int, value:int) -> '_uintn':
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
    def set_bits(x:'_uintn', start:int, end:int, value:'_uintn') -> '_uintn':
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


def uintn_t(bits:int) -> type:
    return refine_t(_uintn,lambda x: x.bits == bits)
uintn = _uintn

def natmod_t(modulus:int) -> type:
    return refine_t(_natmod,lambda x: x.modulus == modulus)
natmod = _natmod

bitvector_t = uintn_t
bitvector   = uintn

class bit(_uintn):
#    __slots__ = []
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,1)
bit_t = uintn_t(1)

class uint8(_uintn):
#    __slots__ = []
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,8)
uint8_t = uintn_t(8)

class uint16(_uintn):
#    __slots__ = []
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,16)
uint16_t = uintn_t(16)

class uint32(_uintn):
#    __slots__ = []
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,32)
uint32_t = uintn_t(32)

class uint64(_uintn):
#    __slots__ = []
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,64)
uint64_t = uintn_t(64)

class uint128(_uintn):
#    __slots__ = []
    def __init__(self, x: Union[int,'_uintn']) -> None:
        _uintn.__init__(self,x,128)
uint128_t = uintn_t(128)


class _array(Generic[T]):
    __slots__ = ['l','len']
    @typechecked
    def __init__(self, x: Union[Sequence[T], List[T], '_array[T]']) -> None:
        if (not isinstance(x, Sequence)) and (not isinstance(x, _array)) and (not isinstance(x,List)):
            fail("_array() takes a list or sequence or _array as first argument.")
        if isinstance(x,_array):
            self.l = x.l
        elif isinstance(x,list):
            self.l = x
        else:
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

    @typechecked
    def __copy__(self) -> '_array[T]':
        result = self.__class__.__new__(self.__class__)
        for s in self.__slots__:
            setattr(result, s, copy(getattr(self, s)))
        return result

    @staticmethod
    @typechecked
    def create(l: int, default:T) -> '_array[T]':
        res = _array([default] * l)
        return res


    @staticmethod
    @typechecked
    def empty() -> '_array[T]':
        return _array([])

    @staticmethod
    @typechecked
    def singleton(x:T) -> '_array[T]':
        return _array([x])


    @staticmethod
    @typechecked
    def createi(l: int, f:Callable[[int],T]) -> '_array[T]':
        return _array([f(i) for i in range(l)])


    @staticmethod
    @typechecked
    def length(a: '_array[T]') -> int:
        if not isinstance(a, _array):
            fail("array.length takes a _array.")
        return len(a)

    @staticmethod
    @typechecked
    def copy(x: '_array[T]') -> '_array[T]':
        return copy(x)

    @staticmethod
    @typechecked
    def concat(x: '_array[T]', y: '_array[T]') -> '_array[T]':
        res1 = copy(x)
        res1.l = res1.l + list([copy(yi) for yi in y.l])
        res1.len += y.len
        return res1

    @staticmethod
    @typechecked
    def split(x: '_array[T]', len:int) -> Tuple['_array[T]','_array[T]']:
        res1 = copy(x)
        res2 = copy(x)
        res1.len = len
        res2.len = x.len - len
        res1.l = x.l[0:len]
        res2.l = x.l[len:x.len]
        return res1,res2

    @staticmethod
    @typechecked
    def zip(x: '_array[T]', y: '_array[U]') -> '_array[Tuple[T,U]]':
        return _array(list(zip(x.l, y.l)))

    @staticmethod
    @typechecked
    def enumerate(x: '_array[T]') -> '_array[Tuple[int,T]]':
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
        res = _array.concat(_array([b for block in blocks for b in block]),last)
        return res

    @staticmethod
    @typechecked
    def map(f: Callable[[T], U], a: '_array[T]') -> '_array[U]':
        res = copy(a)
        res.l = list(map(f,res.l))
        return res

    @staticmethod
    @typechecked
    def create_random(l: nat_t, t: Type[_uintn]) -> '_array[_uintn]':
        if not isinstance(l, nat_t):
            fail("array.create_random's first argument has to be of type nat_t.")
        r = rand()
        return _array(list([t(r.randint(0, 2 << _uintn.num_bits(t(0)))) for _ in range(0, l)]))


def vlarray_t(t:type) -> type:
    return refine_t(_array,lambda x: all(isinstance(z,t) for z in x))
vlarray = _array

def array_t(t: type, l:int) -> type:
   return refine_t(vlarray_t(t),lambda x: x.len == l)
array = _array

vlbytes_t = vlarray_t(uint8_t)
def bytes_t(l:int) -> type:
    return array_t(uint8_t,l)


class bytes(_array):
#    __slots__ = []
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
#    __slots__ = []
    def __init__(self, x: _array[T], zero:T) -> None:
        self.l = x.l
        self.len = x.len
        self.zero = zero
        if not (isinstance(zero,int) or
                isinstance(zero,_natmod) or
                isinstance(zero,_vector)):
            fail("vector must have values of numeric type")
        if not (all(v.__class__ == zero.__class__ for v in self.l)):
            for v in self.l:
                print(str(v.__class__) + " - " + str(zero.__class__))
            fail("vector must have all valus of same type as zero")

    @staticmethod
    @typechecked
    def create(l: int, zero:T) -> '_vector[T]':
        a = _array([zero] * l)
        res = _vector(a,zero)
        return res

    @staticmethod
    @typechecked
    def createi(l: int, zero:T, f:Callable[[int],T]) -> '_vector[T]':
        return _vector(_array.createi(l,f),zero)


    @typechecked
    def __add__(self, other: '_vector[T]') -> '_vector[T]':
        if not isinstance(other, _vector) or \
           other.__class__ != self.__class__ or \
           other.len != self.len:
            fail("+ is only valid for two _vectors of same length")
        res = copy(self)
        res.l = [x + y for (x,y) in zip(self.l,other.l)]
        return res            

    @typechecked
    def __sub__(self, other: '_vector[T]') -> '_vector[T]':
        if not isinstance(other, _vector) or \
           other.__class__ != self.__class__ or \
           other.len != self.len:
            fail("/ is only valid for two _vectors of same length")
        res = copy(self)
        res.l = [x - y for (x,y) in zip(self.l,other.l)]
        return res            

    @typechecked
    def __mul__(self, other: '_vector[T]') -> '_vector[T]':
        if not isinstance(other, _vector) or \
           other.__class__ != self.__class__ or \
           other.len != self.len:
            fail("* is only valid for two _vectors of same length")
        res = copy(self)
        res.l = [x * y for (x,y) in zip(self.l,other.l)]
        return res            

    @staticmethod
    @typechecked
    def poly_mul(x:'_vector[T]', other: '_vector[T]', zero:T) -> '_vector[T]':
        if not isinstance(other, _vector) or \
           other.__class__ != x.__class__ or \
           other.len != x.len:
            fail("poly_mul is only valid for two _vectors of same length")
        res = _vector.create(x.len + other.len, zero)
        for i in range(x.len):
            for j in range(other.len):
                res[i+j] += x[i] * other[j]
        return res            

    @staticmethod
    @typechecked
    def mapz(f: Callable[[T], U], a: '_vector[T]', z:U) -> '_vector[U]':
        return _vector(array.map(f,a),z)


@typechecked
def vlvector_t(t:type) -> type:
    return vlarray_t(t)
@typechecked
def vector_t(t:type,len:nat) -> type:
    return array_t(t,len)
vector = _vector

class _matrix(_vector[_vector[T]]):
#    __slots__ = ['rows','cols']
    @typechecked
    def __init__(self, x: _vector[_vector[T]]) -> None:
        self.l = x.l
        self.len = x.len
        if x.len == 0 or x.l[0].len == 0:
            fail("matrix must be non-empty and have non-empty vectors")
        self.rows = x.len
        self.cols = x[0].len
        self.zero = x[0].zero
        if any(not isinstance(v,_vector) or v.len != self.cols or v.zero != self.zero for v in self.l):
            fail("matrix must have columns that are vectors of same lengths and type")

    def __matmul__(self,other:'_matrix[T]') -> '_matrix[T]':
        if not isinstance(other, _matrix) or \
           other.__class__ != self.__class__ or \
           other.rows != self.cols or \
           other.zero != self.zero :
            fail("@ is only valid for matrices of size M*N and N*K")
        res = _matrix.create(self.rows,other.cols,self.zero)
        for i in range(res.rows):
            for k in range(res.cols):
                tmp = res.zero
                for j in range(self.cols):
                    tmp += self[i][j] * other[j][k]
                res[i][k] = tmp
        return res
        
    @staticmethod
    @typechecked
    def create(r: int, c:int, default:T) -> '_matrix[T]':
        col = _vector.create(c,default)
        mat = _vector.create(r,col)
        for i in range(r):
            mat[i] = _vector.create(c,default)
        return _matrix(mat)

    @staticmethod
    @typechecked
    def createi(r: int, c:int, f:Callable[[int,int],T]) -> '_matrix[T]':
        v = f(0,0)
        res = _matrix.create(r,c,v)
        for i in range(r):
            for j in range(c):
                res[i][j] = f(i,j)
        return res

    @staticmethod
    @typechecked
    def copy(x: '_matrix[T]') -> '_matrix[T]':
        return _matrix.createi(x.rows,x.cols,lambda ij: x[ij[0]][ij[1]])

def matrix_t(t:type,rows:nat,columns:nat) -> type:
    return vector_t(vector_t(t,columns),rows)

matrix = _matrix

# Typed versions of all python functions that can be used in specs.
class speclib:
    @typechecked
    def ceil(x: int) -> nat_t:
        return nat(ceil(x))

    @typechecked
    def log(x: int, b: int) -> float:
        return log(x, b)

    @typechecked
    def floor(x: int) -> int:
        return floor(x)
