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
def refine(t: type, f: Callable[[T], bool]) -> type:
    __class__ = t
    @typechecked
    def init(self, x:t) -> None:
        if not isinstance(x, t):
            fail("ref "+str(type(x)) + " - "+str(t))
        if not isinstance(x, t) or not f(x):
            fail("Type error. You tried to use " + str(x) + " (" + str(type(x)) + ") with subtype of " + str(t) + ".")
        else:
            num_init_args = len(getfullargspec(super().__init__).args)
            if num_init_args == 1:
                super().__init__()
            elif num_init_args >= 2:
                super().__init__(x)
            elif num_init_args == 0:
                # Special case for typeguard. Don't do anything.
                return
            else:
                fail("refine super.init has more args than we expected (" + str(num_init_args) + ") for type " + str(getfullargspec(super().__init__).args))
            t(x)
    @typechecked
    def string(self) -> str:
        return str(self.__origin__)
    # We use a random string as class name here. The result of refine has to
    # get assigend to a type alias, which can be used as class name.
    u_rand = ''.join(random_string(ascii_uppercase + ascii_lowercase, k=15))
    if DEBUG:
        print("new class " + u_rand + " - " + str(t))
    cl = type(u_rand, (t,), {'__init__': init , '__origin__': t})
    __class__ = cl
    return cl

nat = refine(int, lambda x: x >= 0)
nat_t = nat


@typechecked
def range_t(min: int, max: int) -> type:
    return refine(int, lambda x: x >= min and x < max)


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



class _intn:
    @typechecked
    def __init__(self, x: Union[int,'_intn'], signed: bool, bits: int) -> None:
        xv = 0
        if bits < 1:
            fail("cannot create _intn of size <= 0 bits")
        else:
            if isinstance(x,_intn):
                xv = x.v
            else:
                xv = x
            self.bits = bits
            self.signed = signed
            self.max = ((1 << (bits - 1) - 1)) if signed else (1 << bits) - 1 
            self.min = - (1 << (bits - 1)) if signed else 0
            self.v = xv % (1 << bits) if xv >= 0 or not signed else xv % (- (1 << bits))

    @typechecked
    def __str__(self) -> str:
        return hex(self.v)

    @typechecked
    def __repr__(self) -> str:
        return hex(self.v)

    @typechecked
    def __eq__(self, other) -> bool:
        if not isinstance(other, _intn):
            fail("You can only compare two uints.")
        return (self.bits == other.bits and
                self.signed == other.signed and
                self.v == other.v)

    @staticmethod
    @typechecked
    def num_bits(x: '_intn') -> int:
        if not isinstance(x, _intn):
            fail("num_bits is only valid for _intn.")
        return x.bits

    @typechecked
    def __int__(self) -> int:
        return self.v

    @typechecked
    def __add__(self, other: '_intn') -> '_intn':
        if not isinstance(other, _intn) or \
           other.bits != self.bits or \
           other.signed != self.signed:
            fail("+ is only valid for two _intn of same bits and sign.")
        return _intn(self.v + other.v,self.signed,self.bits)

    @typechecked
    def __sub__(self, other: '_intn') -> '_intn':
        if not isinstance(other, _intn) or \
           other.bits != self.bits or \
           other.signed != self.signed:
            fail("- is only valid for two _intn of same bits and sign.")
        return _intn(self.v - other.v,self.signed,self.bits)

    @typechecked
    def __mul__(self, other: '_intn') -> '_intn':
        if not isinstance(other, _intn) or \
           other.bits != self.bits or \
           other.signed != self.signed:
            fail("* is only valid for two _intn of same bits and sign.")
        return _intn(self.v * other.v,self.signed,self.bits)

    @typechecked
    def __inv__(self) -> '_intn':
        return _intn(~ self.v,self.signed,self.bits)

    @typechecked
    def __invert__(self) -> '_intn':
        return _intn(~ self.v,self.signed,self.bits)

    @typechecked
    def __or__(self, other: '_intn') -> '_intn':
        if not isinstance(other, _intn) or \
           other.bits != self.bits or \
           other.signed != self.signed:
            fail("| is only valid for two _intn of same bits and sign.")
        return _intn(self.v | other.v,self.signed,self.bits)

    @typechecked
    def __and__(self, other: '_intn') -> '_intn':
        if not isinstance(other, _intn) or \
           other.bits != self.bits or \
           other.signed != self.signed:
            fail("& is only valid for two _intn of same bits and sign.")
        return _intn(self.v & other.v,self.signed,self.bits)

    @typechecked
    def __xor__(self, other: '_intn') -> '_intn':
        if not isinstance(other, _intn) or \
           other.bits != self.bits or \
           other.signed != self.signed:
            fail("^ is only valid for two _intn of same bits and sign.")
        return _intn(self.v ^ other.v,self.signed,self.bits)

    @typechecked
    def __lshift__(self, other: int) -> '_intn':
        if not isinstance(other, int) or other < 0 or other > self.bits:
            fail("lshift value has to be an int between 0 and bits")
        return _intn(self.v << other,self.signed,self.bits)

    @typechecked
    def __rshift__(self, other: int) -> '_intn':
        if not isinstance(other, int) or other < 0 or other > self.bits:
            fail("rshift value has to be an int between 0 and bits")
        return _intn(self.v >> other,self.signed,self.bits)


    @typechecked
    def __getitem__(self, key: Union[int, slice]):
        try:
            if isinstance(key, slice):
                return _intn(self.v >> key.start,
                             self.signed,
                             key.stop - key.start)
            else:
                return _intn(self.v >> key,self.signed,1)
        except:
            print('_intn content:', self.v)
            print('desired index:', key)
            fail('_intn bit access error')

    @typechecked
    def __getslice__(self, i: int, j: int) -> '_intn':
        return _intn(self.v >> i, self.signd, j - i)


class intn(_intn):
    @staticmethod
    @typechecked
    def to_int(x: '_intn') -> int:
        if not isinstance(x, _intn):
            fail("to_int is only valid for _intn.")
        return x.v

    @staticmethod
    @typechecked
    def to_nat(x: '_intn') -> nat_t:
        if not isinstance(x, _intn) or x.signed == True:
            fail("to_nat is only valid for unsigned _intn.")
        return nat(x.v)


    @staticmethod
    @typechecked
    def rotate_left(x: '_intn', other: int) -> 'bit':
        if not isinstance(x, _intn) or \
           not isinstance(other, int) or \
           other <= 0 or other >= x.bits:
            fail("rotate_left value has to be an int strictly between 0 and bits")
        return _intn(x.v << other | x.v >> (x.bits - other),x.signed,x.bits)

    @staticmethod
    @typechecked
    def rotate_right(x: '_intn', other: int) -> 'bit':
        if not isinstance(x, _intn) or \
           not isinstance(other, int) or \
           other <= 0 or other >= x.bits:
            fail("rotate_right value has to be an int strictly between 0 and bits")
        return _intn(x.v >> other | x.v << (x.bits - other),x.signed,x.bits)

    @staticmethod
    @typechecked
    def get_bit(x:'_intn', index:int):
        if isinstance(x,_intn) and isinstance(index,int) \
           and index >= 0 and index < x.bits:
            return x[index]
        else:
            fail("get_bit index has to be an int between 0 and bits - 1")

    @staticmethod
    @typechecked
    def set_bit(x:'_intn', index:int, value:int):
        if isinstance(x,_intn) and isinstance(index,int) \
           and index >= 0 and index < x.bits \
           and value >= 0 and value < 2:
            tmp1 = ~ (_intn(1,False,x.bits) << index)
            tmp2 = _intn(value,False,x.bits) << index
            return (x & tmp1) | tmp2
        else:
            fail("set_bit index has to be an int between 0 and bits - 1")

class uintn(intn):
    @typechecked
    def __init__(self, x: int, bits: int) -> None:
        super(uintn, self).__init__(x,False,bits)

def intn_t(signed:bool, bits:int):
    return _intn
def uintn_t(bits:int):
    return intn_t(False,bits)

def bitvector_t(bits:int):
    return uintn_t(bits)
def bitvector(n:int,bits:int):
    return uintn(n,bits)
        
bit_t = uintn_t(1)
def bit(v:int):
    if isinstance(v,int):
        return uintn(v,1)
    else:
        return uintn(intn.to_int(v),1)
uint8_t = uintn_t(8)
def uint8(v:Union[int,_intn]):
    if isinstance(v,int):
        return uintn(v,8)
    else:
        return uintn(intn.to_int(v),8)
        
uint16_t = uintn_t(16)
def uint16(v:int):
    if isinstance(v,int):
        return uintn(v,16)
    else:
        return uintn(intn.to_int(v),16)
uint32_t = uintn_t(32)
def uint32(v:int):
    if isinstance(v,int):
        return uintn(v,32)
    else:
        return uintn(intn.to_int(v),32)
uint64_t = uintn_t(64)
def uint64(v:int):
    if isinstance(v,int):
        return uintn(v,64)
    else:
        return uintn(intn.to_int(v),64)
uint128_t = uintn_t(128)
def uint128(v:int):
    if isinstance(v,int):
        return uintn(v,128)
    else:
        return uintn(intn.to_int(v),128)
            

class _array(Generic[T]):
    @typechecked
    def __init__(self, x: Union[Sequence[T], '_array[T]'], t: Type=None) -> None:
        if not (isinstance(x, Sequence) or isinstance(x, _array)):
            fail("_array() takes a sequence or _array as first argument.")
        if t:
            for e in x:
                if not isinstance(e, t) and t(e) is None:
                    fail("_array() input element has wrong type. "+\
                         "Got "+str(type(e))+" expected "+str(t)+".")
        self.l = list(x)
        self.len = len(self.l)
        self.t = t

    @typechecked
    def __len__(self) -> int:
        return len(self.l)

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
        if isinstance(other, _array) and other.t == self.t:
            return self.l == other.l
        fail("_array.__eq__ only works on two _arrays of the same type.")

    @typechecked
    def __ne__(self, other: '_array[T]') -> bool:
        if isinstance(other, _array) and other.t == self.t:
            return self.l != other.l
        fail("_array.__ne__ only works on two _arrays of the same type.")

    # TODO: Return type should be Union['_vlarray', self.t] but we don't have
    #       access to self at this point.
    @typechecked
    def __getitem__(self, key: Union[int, slice]) -> Union['_array[T]', T]:
        try:
            if isinstance(key, slice):
                return _array(self.l[key.start:key.stop],self.t)
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
            return _array(self.l[i:j],self.t)

    @typechecked
    def __setitem__(self, key: Union[int, slice], v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v
        else:
            self.l[key] = v

    
class array(_array):
#    def __init__(self) -> None:
#        fail("Don't use array() directly. Use create.")

    @staticmethod
    @typechecked
    def create(l: int, default:T) -> '_array[T]':
#        if isinstance(l, _uintn):
#            l = _uintn.to_int(l)
        res = _array([default] * l)
#        if isinstance(default, uint8_t):
#            res = vlbytes_t(res)
        return res


    @staticmethod
    @typechecked
    def length(a: '_array[T]') -> int:
        if not isinstance(a, _array):
            fail("array.length takes a _array.")
        return a.len

    @staticmethod
    @typechecked
    def copy(x: '_array[T]') -> '_array[T]':
        copy = _array(x.l[:],x.t)
        return copy

    @staticmethod
    @typechecked
    def concat(x: '_array[T]', y: '_array[T]') -> '_array[T]':
        res = _array(x.l[:]+y.l[:], x.t)
        return res

    @staticmethod
    @typechecked
    def zip(x: '_array[T]', y: '_array[U]') -> '_array[tuple2(T,U)]':
        return _array(list(zip(x.l, y.l)),tuple2(x.t,y.t))

    @staticmethod
    @typechecked
    def enumerate(x: '_array[T]') -> '_array[tuple2(int,T)]':
        return _array(list(enumerate(x.l)),tuple2(int,T))

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
                          for x in range(nblocks)],_array)
        last = _array(a[array.length(a)-rem:array.length(a)],a.t)
        return blocks, last

    @staticmethod
    @typechecked
    def concat_blocks(blocks: '_array[_array[T]]', last: '_array[T]') -> '_array[T]':
        res = array.concat(_array([b for block in blocks for b in block]),last)
        return res

    # Only used in ctr. Maybe delete
    @staticmethod
    @typechecked
    def map(f: Callable[[T], U], a: '_array[T]') -> '_array[U]':
        return _array(list(map(f, a.l)))

    @staticmethod
    @typechecked
    def create_random(l: nat_t, t: Type[_intn]) -> '_array[_intn]':
        if not isinstance(l, nat_t):
            fail("array.create_random's first argument has to be of type nat_t.")
        r = rand()
        x = t(0)
        return _array(list([t(r.randint(0, x.max)) for _ in range(0, l)]))

    
def array_t(t: type, l:int):
    return _array

def vlarray_t(t:type):
    return _array

def bytes_t(l:int):
    return _array

vlbytes_t = _array


class bytes(array):
#    def __init__(self, x: Union[Sequence[T], '_array[T]']) -> None:
#        fail("don't call bytes directly")

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
        return bytes.to_uintn_le(x)
    @staticmethod
    @typechecked
    def to_uint32_le(x: 'vlbytes_t') -> uint32_t:
        return bytes.to_uintn_le(x)
    @staticmethod
    @typechecked
    def to_uint64_le(x: 'vlbytes_t') -> uint64_t:
        return bytes.to_uintn_le(x)
    @staticmethod
    @typechecked
    def to_uint128_le(x: 'vlbytes_t') -> uint128_t:
        return bytes.to_uintn_le(x)
    @staticmethod
    @typechecked
    def to_uint16_be(x: 'vlbytes_t') -> uint16_t:
        return bytes.to_uintn_be(x)
    @staticmethod
    @typechecked
    def to_uint32_be(x: 'vlbytes_t') -> uint32_t:
        return bytes.to_uintn_be(x)
    @staticmethod
    @typechecked
    def to_uint64_be(x: 'vlbytes_t') -> uint64_t:
        return bytes.to_uintn_be(x)
    @staticmethod
    @typechecked
    def to_uint128_be(x: 'vlbytes_t') -> uint128_t:
        return bytes.to_uintn_be(x)

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
        return bytes.to_uintns_le(x,16)
    @staticmethod
    @typechecked
    def to_uint32s_le(x: 'vlbytes_t') -> _array[uint32_t]:
        return bytes.to_uintns_le(x,32)
    @staticmethod
    @typechecked
    def to_uint64s_le(x: 'vlbytes_t') -> _array[uint64_t]:
        return bytes.to_uintns_le(x,64)
    @staticmethod
    @typechecked
    def to_uint128s_le(x: 'vlbytes_t') -> _array[uint128_t]:
        return bytes.to_uintns_le(x,128)
    @staticmethod
    @typechecked
    def to_uint16s_be(x: 'vlbytes_t') -> _array[uint16_t]:
        return bytes.to_uintns_be(x,16)
    @staticmethod
    @typechecked
    def to_uint32s_be(x: 'vlbytes_t') -> _array[uint32_t]:
        return bytes.to_uintns_be(x,32)
    @staticmethod
    @typechecked
    def to_uint64s_be(x: 'vlbytes_t') -> _array[uint64_t]:
        return bytes.to_uintns_be(x,64)
    @staticmethod
    @typechecked
    def to_uint128s_be(x: 'vlbytes_t') -> _array[uint128_t]:
        return bytes.to_uintns_be(x,128)

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


class nat_mod:
    @typechecked
    def __init__(self, x: int, modulus: int) -> None:
        if x < 0 or modulus <= 0:
            fail("nat_mod only defined for nats mod pos")
        self.v = x % modulus
        self.modulus = modulus

    @typechecked
    def __str__(self) -> str:
        return str(self.v)

    @typechecked
    def __repr__(self) -> str:
        return repr(self.v)

    @typechecked
    def __add__(self, other: 'nat_mod') -> 'nat_mod':
        if not isinstance(other, nat_mod) or \
           other.modulus != self.modulus:
            fail("+ is only valid for two nat_mods with same modulus")
        return nat_mod(self.v + other.v,self.modulus)

    @typechecked
    def __sub__(self, other: 'nat_mod') -> 'nat_mod':
        if not isinstance(other, nat_mod) or \
           other.modulus != self.modulus:
            fail("- is only valid for two nat_mods with same modulus")
        return nat_mod(self.modulus + self.v - other.v,self.modulus)

    @typechecked
    def __mul__(self, other: 'nat_mod') -> 'nat_mod':
        if not isinstance(other, nat_mod) or \
           other.modulus != self.modulus:
            fail("* is only valid for two nat_mods with same modulus")
        return nat_mod(self.v * other.v,self.modulus)

    @typechecked
    def __pow__(self, other: int) -> 'nat_mod':
        if not isinstance(other, int) or \
           other < 0:
            fail("** is only valid for nat exponent")
        return nat_mod(pow(self.v,other,self.modulus),self.modulus)

def nat_mod_t(q:nat):
    return nat_mod
    
class vector(_array[nat_mod]):
    @typechecked
    def __init__(self, x: Union[Sequence[nat_mod],_array[nat_mod]]) -> None:
        if isinstance(x,Sequence):
            super().__init__(x,nat_mod)
        else:
            super().__init__(x.l,nat_mod)
            
    @typechecked
    def __add__(self, other: 'vector') -> 'vector':
        if not isinstance(other, vector) or \
           other.len != self.len:
            fail("+ is only valid for two vectors of same length")
        return vector([x + y for (x,y) in zip(self.l,other.l)])

    @typechecked
    def __sub__(self, other: 'vector') -> 'vector':
        if not isinstance(other, vector) or \
           other.len != self.len:
            fail("- is only valid for two vectors of same length")
        return vector([x - y for (x,y) in zip(self.l,other.l)])

    @typechecked
    def __mul__(self, other: 'vector') -> 'vector':
        if not isinstance(other, vector) or \
           other.len != self.len:
            fail("- is only valid for two vectors of same length")
        return vector([x * y for (x,y) in zip(self.l,other.l)])

def vector_t(t:type,len:nat):
    return vector

class matrix(_array[vector]):
    @typechecked
    def __init__(self, x: Sequence[Sequence[nat_mod]]) -> None:
        super().__init__([vector(y) for y in x],vector)

    @typechecked
    def __add__(self, other: 'matrix') -> 'matrix':
        if not isinstance(other, matrix) or \
           other.len != self.len:
            fail("+ is only valid for two matrices of same length")
        return matrix([x + y for (x,y) in zip(self.l,other.l)])

    @typechecked
    def __sub__(self, other: 'matrix') -> 'matrix':
        if not isinstance(other, matrix) or \
           other.len != self.len:
            fail("- is only valid for two matrices of same length")
        return matrix([x - y for (x,y) in zip(self.l,other.l)])

    @typechecked
    def __mul__(self, other: 'matrix') -> 'matrix':
        if not isinstance(other, matrix) or \
           other.len != self.len:
            fail("- is only valid for two matrices of same length")
        return matrix([x * y for (x,y) in zip(self.l,other.l)])
    
def matrix_t(t:type,rows:nat,columns:nat):
    return matrix
