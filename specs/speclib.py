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


def fail(s: str) -> None:
    raise Error(s)


T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
W = TypeVar('W')
X = TypeVar('X')


def tuple2(T: type, U: type) -> Tuple[T, U]:
    return Tuple[T, U]


def tuple3(T: type, U: type, V: type) -> Tuple[T, U, V]:
    return Tuple[T, U, V]


def tuple4(T: type, U: type, V: type, W: type) -> Tuple[T, U, V, W]:
    return Tuple[T, U, V, W]


def tuple5(T: type, U: type, V: type, W: type, X: type) -> Tuple[T, U, V, W, X]:
    return Tuple[T, U, V, W, X]


def refine3(t: type, f: Callable[[T], bool]) -> type:
    __class__ = t
    def init(self, x:t) -> None:
        if not isinstance(x, t):
            print("ref "+str(type(x)))
        if not isinstance(x, t) or not f(x):
            fail("Type error. You tried to use " + str(x) + " (" + str(type(x)) + ") with subtype of " + str(t) + ".")
        else:
            num_init_args = len(getfullargspec(super().__init__).args)
            if num_init_args == 1:
                super().__init__()
            elif num_init_args == 2:
                super().__init__(x)
            else:
                fail("refine3 super.init has more args than we expected (" + str(num_init_args) + ")")
            t(x)
    def string(self) -> str:
        return str(self.__origin__)
    # We use a random string as class name here. The result of refine3 has to
    # get assigend to a type alias, which can be used as class name.
    u_rand = ''.join(random_string(ascii_uppercase + ascii_lowercase, k=15))
    if DEBUG:
        print("new class " + u_rand + " - " + str(t))
    cl = type(u_rand, (t,), {'__init__': init , '__origin__': t})
    __class__ = cl
    return cl

# nat = refine2('nat_t', int, lambda x: x >= 0)
# class nat_t(int): pass
nat = refine3(int, lambda x: x >= 0)
nat_t = nat


def range_t(min, max) -> type:
    return refine3(int, lambda x: x >= min and x < max)


def contract(T: Type[T], pre, post):
    return T


class _uintn:
    def __init__(self, x: int, bits: int) -> None:
        if x < 0:
            fail("cannot convert negative integer to _uintn")
        elif bits < 1:
            fail("cannot create uint of size <= 0 bits")
        else:
            self.bits = bits
            self.max = (1 << bits) - 1
            self.v = x & self.max

    def __str__(self) -> str:
        return hex(self.v)

    def __repr__(self) -> str:
        return hex(self.v)

    def __eq__(self, other) -> bool:
        if not isinstance(other, _uintn):
            fail("You can only compare two uints.")
        return (self.bits == other.bits and self.v == other.v)

    @staticmethod
    def num_bits(x: '_uintn') -> int:
        if not isinstance(x, _uintn):
            fail("num_bits is only valid for uintN.")
        return x.bits

    def __int__(self) -> int:
        return self.v

    @staticmethod
    def to_int(x: '_uintn') -> int:
        if not isinstance(x, _uintn):
            fail("to_int is only valid for uintN.")
        return x.v

    @staticmethod
    def to_nat(x: '_uintn') -> nat_t:
        if not isinstance(x, _uintn):
            fail("to_int is only valid for uintN.")
        return nat(x.v)


class bit(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 1)
        else:
            if not isinstance(v, _uintn):
                fail("bit() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 1)

    def __add__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("+ is only valid for two bit.")
        return bit(self.v + other.v)

    def __sub__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("- is only valid for two bit.")
        return bit(self.v - other.v)

    def __mul__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("* is only valid for two bit.")
        return bit(self.v * other.v)

    def __inv__(self) -> 'bit':
        return bit(~ self.v)

    def __invert__(self) -> 'bit':
        return bit(~ self.v & self.max)

    def __or__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("| is only valid for two bit.")
        return bit(self.v | other.v)

    def __and__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("& is only valid for two bit.")
        return bit(self.v & other.v)

    def __xor__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("^ is only valid for two bit.")
        return bit(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'bit':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return bit(self.v << other)

    def __rshift__(self, other: int) -> 'bit':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return bit(self.v >> other)

    @staticmethod
    def rotate_left(x: 'bit', other: int) -> 'bit':
        if not isinstance(x, bit):
            fail("rotate_left is only valid for bit.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'bit', other: int) -> 'bit':
        if not isinstance(x, bit):
            fail("rotate_right is only valid for bit.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint8(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 8)
        else:
            if not isinstance(v, _uintn):
                fail("uint8() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 8)

    def __add__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("+ is only valid for two uint8_t.")
        return uint8(self.v + other.v)

    def __sub__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("- is only valid for two uint8_t.")
        return uint8(self.v - other.v)

    def __mul__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("* is only valid for two uint8_t.")
        return uint8(self.v * other.v)

    def __inv__(self) -> 'uint8':
        return uint8(~ self.v)

    def __invert__(self) -> 'uint8':
        return uint8(~ self.v & self.max)


    def __or__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("| is only valid for two uint8_t.")
        return uint8(self.v | other.v)

    def __and__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("& is only valid for two uint8_t.")
        return uint8(self.v & other.v)

    def __xor__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("^ is only valid for two uint8_t.")
        return uint8(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint8':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint8(self.v << other)

    def __rshift__(self, other: int) -> 'uint8':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint8(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint8', other: int) -> 'uint8':
        if not isinstance(x, uint8):
            fail("rotate_left is only valid for uint8_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint8', other: int) -> 'uint8':
        if not isinstance(x, uint8):
            fail("rotate_right is only valid for uint8_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint16(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 16)
        else:
            if not isinstance(v, _uintn):
                fail("uint16() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 16)

    def __add__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("+ is only valid for two uint16_t.")
        return uint16(self.v + other.v)

    def __sub__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("- is only valid for two uint16_t.")
        return uint16(self.v - other.v)

    def __mul__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("* is only valid for two uint16_t.")
        return uint16(self.v * other.v)

    def __inv__(self) -> 'uint16':
        return uint16(~ self.v)

    def __invert__(self) -> 'uint16':
        return uint16(~ self.v & self.max)

    def __or__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("| is only valid for two uint16_t.")
        return uint16(self.v | other.v)

    def __and__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("& is only valid for two uint16_t.")
        return uint16(self.v & other.v)

    def __xor__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("^ is only valid for two uint16_t.")
        return uint16(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint16':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint16(self.v << other)

    def __rshift__(self, other: int) -> 'uint16':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint16(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint16', other: int) -> 'uint16':
        if not isinstance(x, uint16):
            fail("rotate_left is only valid for uint16_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint16', other: int) -> 'uint16':
        if not isinstance(x, uint16):
            fail("rotate_right is only valid for uint16_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint32(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 32)
        else:
            if not isinstance(v, _uintn):
                fail("uint32() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 32)

    def __add__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("+ is only valid for two uint32_t.")
        return uint32(self.v + other.v)

    def __sub__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("- is only valid for two uint32_t.")
        return uint32(self.v - other.v)

    def __mul__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("* is only valid for two uint32_t.")
        return uint32(self.v * other.v)

    def __inv__(self) -> 'uint32':
        return uint32(~ self.v)

    def __invert__(self) -> 'uint32':
        return uint32(~ self.v & self.max)

    def __or__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("| is only valid for two uint32_t.")
        return uint32(self.v | other.v)

    def __and__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("& is only valid for two uint32_t.")
        return uint32(self.v & other.v)

    def __xor__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("^ is only valid for two uint32_t.")
        return uint32(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint32':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint32(self.v << other)

    def __rshift__(self, other: int) -> 'uint32':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint32(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint32', other: int) -> 'uint32':
        if not isinstance(x, uint32):
            fail("rotate_left is only valid for uint32_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint32', other: int) -> 'uint32':
        if not isinstance(x, uint32):
            fail("rotate_right is only valid for uint32_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint64(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 64)
        else:
            if not isinstance(v, _uintn):
                fail("uint64() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 64)

    def __add__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("+ is only valid for two uint64_t.")
        return uint64(self.v + other.v)

    def __sub__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("- is only valid for two uint64_t.")
        return uint64(self.v - other.v)

    def __mul__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("* is only valid for two uint64_t.")
        return uint64(self.v * other.v)

    def __inv__(self) -> 'uint64':
        return uint64(~ self.v)

    def __invert__(self) -> 'uint64':
        return uint64(~ self.v & self.max)

    def __or__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("| is only valid for two uint64_t.")
        return uint64(self.v | other.v)

    def __and__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("& is only valid for two uint64_t.")
        return uint64(self.v & other.v)

    def __xor__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("^ is only valid for two uint64_t. other is "+str(other))
        return uint64(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint64':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint64(self.v << other)

    def __rshift__(self, other: int) -> 'uint64':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint64(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint64', other: int) -> 'uint64':
        if not isinstance(x, uint64):
            fail("rotate_left is only valid for uint64_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint64', other: int) -> 'uint64':
        if not isinstance(x, uint64):
            fail("rotate_right is only valid for uint64_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint128(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 128)
        else:
            if not isinstance(v, _uintn):
                fail("uint128() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 128)

    def __add__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("+ is only valid for two uint128_t.")
        return uint128(self.v + other.v)

    def __sub__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("- is only valid for two uint128_t.")
        return uint128(self.v - other.v)

    def __mul__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("* is only valid for two uint128_t.")
        return uint128(self.v * other.v)

    def __inv__(self) -> 'uint128':
        return uint128(~ self.v)

    def __invert__(self) -> 'uint128':
        return uint128(~ self.v & self.max)


    def __or__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("| is only valid for two uint128_t.")
        return uint128(self.v | other.v)

    def __and__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("& is only valid for two uint128_t.")
        return uint128(self.v & other.v)

    def __xor__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("^ is only valid for two uint128_t.")
        return uint128(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint128':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint128(self.v << other)

    def __rshift__(self, other: int) -> 'uint128':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint128(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint128', other: int) -> 'uint128':
        if not isinstance(x, uint128):
            fail("rotate_left is only valid for uint128_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint128', other: int) -> 'uint128':
        if not isinstance(x, uint128):
            fail("rotate_right is only valid for uint128_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class bitvector(_uintn):
    def __init__(self, v: Union[int, _uintn], bits: int) -> None:
        if isinstance(v, int):
            super().__init__(v, bits)
        else:
            super().__init__(_uintn.to_int(v), bits)

    @staticmethod
    def init(v: Union[int, _uintn]) -> 'bitvector':
        return bitvector(v, 0)

    def __add__(self, other: 'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
            return bitvector(self.v + other.v, self.bits)
        else:
            fail("cannot add bitvector of different lengths")
            return bitvector(0, self.bits)

    def __sub__(self, other: 'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
            return bitvector(self.v - other.v, self.bits)
        else:
            fail("cannot sub bitvector of different lengths")
            return bitvector(0, self.bits)

    def __inv__(self) -> 'bitvector':
        return bitvector(~self.v, self.bits)

    def __invert__(self) -> 'bitvector':
        return bitvector(~self.v & self.max, self.bits)

    def __or__(self, other: 'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
            return bitvector(self.v | other.v, self.bits)
        else:
            fail("cannot or bitvector of different lengths")
            return bitvector(0, self.bits)

    def __and__(self, other: 'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
            return bitvector(self.v & other.v, self.bits)
        else:
            fail("cannot and bitvector of different lengths")
            return bitvector(0, self.bits)

    def __xor__(self, other: 'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
            return bitvector(self.v ^ other.v, self.bits)
        else:
            fail("cannot xor bitvector of different lengths")
            return bitvector(0, self.bits)

    def __lshift__(self, other: int) -> 'bitvector':
        if other < 0 or other >= self.bits:
            fail("bitvector cannot be shifted by < 0 or >= bits")
            return bitvector(0, self.bits,)
        else:
            return bitvector(self.v << other, self.bits)

    def __rshift__(self, other: int) -> 'bitvector':
        if other < 0 or other >= self.bits:
            fail("bitvector cannot be shifted by < 0 or >= bits")
            return bitvector(0, self.bits)
        else:
            return bitvector(self.v >> other, self.bits)

    @staticmethod
    def rotate_left(x: 'bitvector', other: int) -> 'bitvector':
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'bitvector', other: int) -> 'bitvector':
        return (x >> other | x << (x.bits - other))

    def __getitem__(self, key: Union[int, slice]):
        try:
            if isinstance(key, slice):
                return bitvector(self.v >> key.start,
                                 key.stop - key.start)
            else:
                return bit(self.v >> key)
        except:
            print('bitvector content:', self.v)
            print('bitvector index:', key)
            fail('bitvector access error')

    def __getslice__(self, i: int, j: int) -> 'bitvector':
        return bitvector(self.v >> i, j - i)


class vlarray():
    # TODO: make t arg mandatory
    def __init__(self, x: Union[Sequence[T], 'vlarray'], t: Type=None) -> None:
        if not (isinstance(x, Sequence) or isinstance(x, vlarray)):
            fail("vlarray() takes a sequence or vlarray as first argument.")
        if t:
            for e in x:
                if not isinstance(e, t):
                    fail("vlarray() input element has wrong type. "+\
                         "Got "+str(type(e))+" expected "+str(t)+".")
        self.l = list(x)
        self.t = t

    def __len__(self) -> int:
        return len(self.l)

    def __str__(self) -> str:
        return str(self.l)

    def __repr__(self) -> str:
        return repr(self.l)

    def __iter__(self) -> Iterator[T]:
        return iter(self.l)

    def __eq__(self, other):
        if not isinstance(self, vlarray) or not isinstance(other, vlarray):
            fail("vlarray.__eq__ only works on two vlarray.")
        # if str(other.t) == "speclib.vlbytes" or str(other.t) == "speclib.vlarray" \
        #    or isinstance(other, vlbytes) or isinstance(other, vlarray):
        return self.l == other.l
        # else:
        #     return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.l != other.l
        else:
            return True

    def __getitem__(self, key: Union[int, slice]) -> 'vlarray':
        try:
            if isinstance(key, slice):
                return vlarray(self.l[key.start:key.stop])
            return self.l[key]
        except:
            print('vlarray access error:')
            print('vlarray content:', self.l)
            print('vlarray index:', key)
            fail('vlarray index error')

    def __getslice__(self, i: int, j: int) -> 'vlarray':
        return vlarray(self.l[i:j])

    def __setitem__(self, key: Union[int, slice], v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v
        else:
            self.l[key] = v

    @staticmethod
    def create(len: int, default) -> 'vlarray':
        return vlarray([default] * len)

    @staticmethod
    def create_type(x: Iterable[U], t: type) -> 'vlarray':
        return vlarray(list([t(el) for el in x]), t)

    @staticmethod
    def length(a: 'vlarray') -> int:
        if not isinstance(a, vlarray):
            fail("array.length takes a vlarray.")
        return len(a.l)

    @staticmethod
    def copy(x: 'vlarray') -> 'vlarray':
        return vlarray(x.l[:])

    @staticmethod
    def concat(x: 'vlarray', y: 'vlarray') -> 'vlarray':
        if x.t and \
           (str(x.t.__name__) == "vlbytes" or str(x.t.__name__) == "vlarray"):
            tmp = x.l[:]
            # TODO: only works with bytes
            tmp.append(vlbytes(y.l[:]))
            return vlarray(tmp, x.t)
        return vlarray(x.l[:]+y.l[:], x.t)

    @staticmethod
    def zip(x: 'vlarray', y: 'vlarray') -> 'vlarray':
        return vlarray(list(zip(x.l, y.l)))

    @staticmethod
    def enumerate(x: 'vlarray') -> 'vlarray':
        return vlarray(list(enumerate(x.l)))

    @staticmethod
    def split_blocks(a: 'vlarray', blocksize: int) -> 'Tuple[vlarray,vlarray]':
        if not isinstance(a, vlarray):
            fail("split_blocks takes a vlarray as first argument.")
        if not isinstance(blocksize, int):
            fail("split_blocks takes an int as second argument.")
        nblocks = len(a) // blocksize
        blocks = vlarray([a[x*blocksize:(x+1)*blocksize]
                          for x in range(nblocks)])
        last = vlarray(a[len(a) - (len(a) % blocksize):len(a)])
        return (blocks, last)

    @staticmethod
    def concat_blocks(blocks: 'vlarray', last: 'vlarray') -> 'vlarray':
        return (vlarray.concat(vlarray([b for block in blocks for b in block]), last))

    # Only used in ctr. Maybe delete
    @staticmethod
    def map(f: Callable[[T], U], a: 'vlarray') -> 'vlarray':
        return vlarray(list(map(f, a.l)))

    @staticmethod
    def create_random(l: nat_t, t: Type[_uintn]) -> 'vlarray':
        if not isinstance(l, nat_t):
            fail("array.create_random's first argument has to be of type nat_t.")
        r = rand()
        x = t(0)
        return array(list([t(r.randint(0, x.max)) for _ in range(0, l)]))


class vlbytes(vlarray):
    def __init__(self, x: Union[Sequence[T], 'vlbytes']) -> None:
        super(vlbytes, self).__init__(x, uint8_t)

    # TODO: this wouldn't be necessary if we could return the correct type in vlarray.
    def __getitem__(self, key: Union[int, slice]) -> 'vlbytes':
        try:
            if isinstance(key, slice):
                return vlbytes(self.l[key.start:key.stop])
            return self.l[key]
        except:
            print('vlarray access error:')
            print('vlarray content:', self.l)
            print('vlarray index:', key)
            fail('vlarray index error')

    @staticmethod
    def from_ints(x: List[int]) -> 'vlbytes':
        return vlbytes([uint8(i) for i in x])

    @staticmethod
    def concat_bytes(blocks: 'vlarray') -> 'vlbytes':
        concat = [b for block in blocks for b in block]
        return vlbytes(concat)

    @staticmethod
    def from_hex(x: str) -> 'vlbytes':
        return vlbytes([uint8(int(x[i:i+2], 16)) for i in range(0, len(x), 2)])

    @staticmethod
    def to_hex(a: 'vlbytes') -> str:
        return "".join(['{:02x}'.format(uint8.to_int(x)) for x in a])

    @staticmethod
    def from_nat_le(x: nat_t) -> 'vlbytes':
        if not isinstance(x, nat_t):
            fail("bytes.from_nat_le's argument has to be of type nat_t.")
        b = x.to_bytes((x.bit_length() + 7) // 8, 'little') or b'\0'
        return vlbytes([uint8(i) for i in b])

    @staticmethod
    def to_int_le(x: 'vlbytes') -> int:
        b = builtins.bytes([uint8.to_int(u) for u in x])
        return int.from_bytes(b, 'little')

    @staticmethod
    def to_nat_le(x: 'vlbytes') -> nat_t:
        return nat(vlbytes.to_int_le(x))

    @staticmethod
    def from_nat_be(x: nat_t, l: nat_t=nat(0)) -> 'vlbytes':
        if not isinstance(x, nat_t):
            fail("bytes.from_nat_be's first argument has to be of type nat_t.")
        if not isinstance(l, nat_t):
            fail("bytes.from_nat_be's second argument has to be of type nat_t.")
        b = x.to_bytes((x.bit_length() + 7) // 8, 'big') or b'\0'
        pad = vlarray([uint8(0) for i in range(0, max(0, l-len(b)))])
        result = vlarray([uint8(i) for i in b])
        return bytes(array.concat(pad, result))

    @staticmethod
    def to_nat_be(x: 'vlbytes') -> nat_t:
        b = builtins.bytes([uint8.to_int(u) for u in x])
        return int.from_bytes(b, 'big')

    @staticmethod
    def from_uint32_le(x: uint32) -> 'vlbytes':
        xv = uint32.to_int(x)
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
        return vlarray([x0, x1, x2, x3])

    @staticmethod
    def to_uint32_le(x: 'vlbytes') -> uint32:
        x0 = uint8.to_int(x[0])
        x1 = uint8.to_int(x[1]) << 8
        x2 = uint8.to_int(x[2]) << 16
        x3 = uint8.to_int(x[3]) << 24
        return uint32(x0 + x1 + x2 + x3)

    @staticmethod
    def from_uint64_le(x: uint64) -> 'vlbytes':
        xv = uint64.to_int(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a: vlbytes = vlarray.create(8, uint8(0))
        a[0:4] = vlbytes.from_uint32_le(x0)
        a[4:8] = vlbytes.from_uint32_le(x1)
        return a

    @staticmethod
    def to_uint64_le(x: 'vlbytes') -> uint64:
        x0 = vlbytes.to_uint32_le(x[0:4])
        x1 = vlbytes.to_uint32_le(x[4:8])
        return uint64(uint32.to_int(x0) +
                      (uint32.to_int(x1) << 32))

    @staticmethod
    def from_uint128_le(x: uint128) -> 'vlbytes':
        xv = uint128.to_int(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = vlarray.create(16, uint8(0))
        a[0:8] = vlbytes.from_uint64_le(x0)
        a[8:16] = vlbytes.from_uint64_le(x1)
        return bytes(a)

    @staticmethod
    def to_uint128_le(x: 'vlbytes') -> uint128:
        x0 = vlbytes.to_uint64_le(x[0:8])
        x1 = vlbytes.to_uint64_le(x[8:16])
        return uint128(uint64.to_int(x0) +
                       (uint64.to_int(x1) << 64))

    @staticmethod
    def from_uint32_be(x: uint32) -> 'vlbytes':
        xv = uint32.to_int(x)
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
        return vlbytes([x3, x2, x1, x0])

    @staticmethod
    def to_uint32_be(x: 'vlbytes') -> uint32:
        x0 = uint8.to_int(x[0]) << 24
        x1 = uint8.to_int(x[1]) << 16
        x2 = uint8.to_int(x[2]) << 8
        x3 = uint8.to_int(x[3])
        return uint32(x3 + x2 + x1 + x0)

    @staticmethod
    def from_uint64_be(x: uint64) -> 'vlbytes':
        xv = uint64.to_int(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a: vlbytes = vlarray.create(8, uint8(0))
        a[0:4] = vlbytes.from_uint32_be(x1)
        a[4:8] = vlbytes.from_uint32_be(x0)
        return a

    @staticmethod
    def to_uint64_be(x: 'vlbytes') -> uint64:
        x0 = vlbytes.to_uint32_be(x[0:4])
        x1 = vlbytes.to_uint32_be(x[4:8])
        return uint64(uint32.to_int(x1) +
                      (uint32.to_int(x0) << 32))

    @staticmethod
    def from_uint128_be(x: uint128) -> 'vlbytes':
        xv = uint128.to_int(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = bytes(vlarray.create(16, uint8(0)))
        a[0:8] = vlbytes.from_uint64_be(x1)
        a[8:16] = vlbytes.from_uint64_be(x0)
        return a

    @staticmethod
    def to_uint128_be(x: 'vlbytes') -> uint128:
        x0 = vlbytes.to_uint64_be(x[0:8])
        x1 = vlbytes.to_uint64_be(x[8:16])
        return uint128(uint64.to_int(x1) +
                       (uint64.to_int(x0) << 64))

    @staticmethod
    def from_uint32s_le(x: vlarray) -> 'vlbytes':
        by = vlarray([vlbytes.from_uint32_le(i) for i in x])
        return bytes(vlarray.concat_blocks(by, vlarray([])))

    @staticmethod
    def to_uint32s_le(x: 'vlbytes') -> vlarray:
        nums, x = vlarray.split_blocks(x, 4)
        if len(x) > 0:
            fail("array length not a multiple of 4")
        else:
            return(vlarray([vlbytes.to_uint32_le(i) for i in nums]))

    @staticmethod
    def from_uint32s_be(x: vlarray) -> 'vlbytes':
        by = vlarray([vlbytes.from_uint32_be(i) for i in x])
        return vlbytes(vlarray.concat_blocks(by, vlarray([])))

    @staticmethod
    def to_uint32s_be(x: 'vlbytes') -> vlarray:
        nums, x = vlarray.split_blocks(x, 4)
        if len(x) > 0:
            fail("array length not a multiple of 4")
        else:
            return vlarray([vlbytes.to_uint32_be(i) for i in nums])

    @staticmethod
    def from_uint64s_be(x: vlarray) -> 'vlbytes':
        by = vlarray([vlbytes.from_uint64_be(i) for i in x])
        return vlbytes(vlarray.concat_blocks(by, vlarray([])))

    @staticmethod
    def to_uint64s_be(x: 'vlbytes') -> vlarray:
        nums, x = vlarray.split_blocks(x, 8)
        if len(x) > 0:
            fail("array length not a multple of 8")
        else:
            return(vlarray([vlbytes.to_uint64_be(i) for i in nums]))

    @staticmethod
    def from_uint64s_le(x: vlarray) -> 'vlbytes':
        by = vlarray([vlbytes.from_uint64_le(i) for i in x])
        return vlbytes(vlarray.concat_blocks(by, vlarray([])))

    @staticmethod
    def to_uint64s_le(x: 'vlbytes') -> vlarray:
        nums, x = vlarray.split_blocks(x, 8)
        if len(x) > 0:
            fail("array length not a multple of 8")
        else:
            return vlarray([vlbytes.to_uint64_le(i) for i in nums])

    @staticmethod
    def create_random_bytes(len: nat) -> 'vlbytes':
        r = rand()
        return bytes(list([uint8(r.randint(0, 0xFF)) for _ in range(0, len)]))


def vlbytes_t(T):
    return vlbytes


def bytes_t(l:int):
    return refine3(vlbytes, lambda x: vlbytes.length(x) <= l)


def bitvector_t(l:int):
    def refine_bitvec() -> type:
        __class__ = bitvector
        def f(x:Union[int, _uintn]):
            return int(x) <= ((1 << l) - 1)
        def init(self, x:Union[int, _uintn]) -> None:
            if not (isinstance(x, int) or isinstance(x, _uintn)) or not f(x):
                fail("Type error. You tried to use " + str(x) + " (" + str(type(x)) + ") with subtype of bitvector.")
            else:
                super().__init__(x, l)
                bitvector(x, l)
        def string(self) -> str:
            return str(self.__origin__)
        # We use a random string as class name here. The result of refine3 has to
        # get assigend to a type alias, which can be used as class name.
        u_rand = ''.join(random_string(ascii_uppercase + ascii_lowercase, k=15))
        if DEBUG:
            print("new class " + u_rand + " - " + str(bitvector))
        cl = type(u_rand, (bitvector,), {'__init__': init , '__origin__': bitvector, '__str__': string})
        __class__ = cl
        return cl
    refinement = refine_bitvec()
    return refinement


def vlarray_t(t: type):
    return vlarray


def array_t(t: type, len: int) -> vlarray:
    return vlarray


bit_t = bit
uint8_t = uint8
uint16_t = uint16
uint32_t = uint32
uint64_t = uint64
uint128_t = uint128

array = vlarray
bytes = vlbytes


# The libraries below are experimental and need more thought
class pfelem:
    def __init__(self, x: int, p: int) -> None:
        if x < 0:
            fail("cannot convert negative integer to pfelem")
        elif p < 1:
            fail("cannot use prime < 1")
        else:
            self.p = p
            self.v = x % p

    def __str__(self) -> str:
        return hex(self.v)

    def __repr__(self) -> str:
        return hex(self.v)

    def __add__(self, other: 'pfelem') -> 'pfelem':
        if (other.p == self.p):
            return pfelem(self.v + other.v, self.p)
        else:
            fail("cannot add pfelem of different fields")
            return pfelem(0, self.p)

    def __sub__(self, other: 'pfelem') -> 'pfelem':
        if (other.p == self.p):
            return pfelem(self.v - other.v, self.p)
        else:
            fail("cannot sub pfelem of different fields")
            return pfelem(0, self.p)

    def __mul__(self, other: 'pfelem') -> 'pfelem':
        if (other.p == self.p):
            return pfelem(self.v * other.v, self.p)
        else:
            fail("cannot sub pfelem of different fields")
            return pfelem(0, self.p)

    def __pow__(self, other: int) -> 'pfelem':
        if (other >= 0):
            return pfelem(pow(self.v, other, self.p), self.p)
        else:
            fail("cannot exp with negative number")
            return pfelem(0, self.p)

    # See https://github.com/python/mypy/issues/2783
    def __eq__(self, other: Any) -> Any:
        return (self.p == other.p and self.v == other.v)

    @staticmethod
    def pfadd(x: 'pfelem', y: 'pfelem') -> 'pfelem':
        return (x+y)

    @staticmethod
    def pfmul(x: 'pfelem', y: 'pfelem') -> 'pfelem':
        return (x*y)

    @staticmethod
    def pfsub(x: 'pfelem', y: 'pfelem') -> 'pfelem':
        return (x-y)

    @staticmethod
    def pfinv(x: 'pfelem') -> 'pfelem':
        def egcd(a, b):
            if a == 0:
                return (b, 0, 1)
            else:
                g, y, x = egcd(b % a, a)
            return (g, x - (b // a) * y, y)

        def modinv(a, m):
            g, x, y = egcd(a, m)
            if g != 1:
                raise Exception('modular inverse does not exist')
            else:
                return x % m

        return pfelem(modinv(x.v, x.p), x.p)

    @staticmethod
    def prime(x: 'pfelem') -> int:
        return x.p

    def __int__(self) -> int:
        return self.v

    @staticmethod
    def to_int(x: 'pfelem') -> int:
        return x.v


pfelem_t = pfelem


def prime_field(prime: nat):
    return pfelem_t, (lambda x: pfelem(x, prime)), pfelem.to_int


class gfelem:
    def __init__(self, x: bitvector, irred: bitvector) -> None:
        if x.v < 0:
            fail("cannot convert negative integer to gfelem")
        elif x.bits < 1:
            fail("cannot create gfelem with bits < 1")
        elif x.bits != irred.bits:
            fail("cannot create gfelem with x.bits <> irred.bits")
        else:
            self.bits = x.bits
            self.irred = irred
            self.v = x

    def __str__(self) -> str:
        return str(self.v)

    def __repr__(self) -> str:
        return str(self.v)

    def __add__(self, other: 'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred):
            return gfelem(self.v ^ other.v, self.irred)
        else:
            fail("cannot add gfelem of different fields")
            return gfelem(bitvector(0, self.bits), self.irred)

    def __sub__(self, other: 'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred):
            return gfelem(self.v ^ other.v, self.irred)
        else:
            fail("cannot sub gfelem of different fields")
            return gfelem(bitvector(0, self.bits), self.irred)

    def __mul__(self, other: 'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred):
            bits = self.bits
            irred = self.irred
            a = self.v
            b = other.v
            p = bitvector(0, bits)
            for i in range(bits):
                if (bitvector.to_int(b) & 1 == 1):
                    p = p ^ a
                b = b >> 1
                c = a >> (bits - 1)
                a = a << 1
                if (bitvector.to_int(a) == 1):
                    a = a ^ irred
            return gfelem(p, irred)
        else:
            fail("cannot mul gfelem of different fields")
            return gfelem(bitvector(0, self.bits), self.irred)

    def __pow__(self, other: int) -> 'gfelem':
        if (other < 0):
            fail("cannot exp with negative number")
            return gfelem(bitvector(0, self.bits), self.irred)
        else:
            def exp(a, x):
                if (x == 0):
                    return gfelem(bitvector(1, self.bits), self.irred)
                elif (x == 1):
                    return a
                elif (x == 2):
                    return a * a
                else:
                    r = exp(a, x/2)
                    r_ = r * r
                    if (x % 2 == 0):
                        return r_
                    else:
                        return (a * r_)
            return exp(self, other)

    # See https://github.com/python/mypy/issues/2783
    def __eq__(self, other: Any) -> Any:
        return (self.bits == other.bits and self.v == other.v)

    @staticmethod
    def gfadd(x: 'gfelem', y: 'gfelem') -> 'gfelem':
        return (x + y)

    @staticmethod
    def gfsub(x: 'gfelem', y: 'gfelem') -> 'gfelem':
        return (x - y)

    @staticmethod
    def gfmul(x: 'gfelem', y: 'gfelem') -> 'gfelem':
        return (x * y)

    @staticmethod
    def gfexp(x: 'gfelem', y: int) -> 'gfelem':
        return (x ** y)

    @staticmethod
    def gfinv(x: 'gfelem') -> 'gfelem':
        bits = x.bits
        irred = x.irred

        def degree(v: bitvector, bits: int):
            if (v == 0 or bits == 0):
                return 0
            elif (bitvector.to_int(v >> (bits - 1)) == 1):
                return (bits - 1)
            else:
                return degree(v >> 1, bits - 1)

        def gfgcd(s, r, v, u):
            dr = degree(r, bits)
            ds = degree(s, bits)
            if (dr == 0):
                return u
            elif (ds >= dr):
                s_ = s ^ (r << (ds - dr))
                v_ = v ^ (u << (ds - dr))
                return gfgcd(s_, r, v_, u)
            else:
                r_ = s
                s_ = r
                v_ = u
                u_ = v
                s_ = s_ ^ (r_ << (dr - ds))
                v_ = v_ ^ (u_ << (dr - ds))
                return gfgcd(s_, r_, v_, u_)
        r = x.v
        s = irred
        dr = degree(r, bits)
        ds = degree(s, bits)
        v = gfelem(bitvector(0, bits), irred)
        u = gfelem(bitvector(1, bits), irred)
        if (dr == 0):
            return u
        else:
            s_ = s ^ (r << (ds - dr))
            v_ = v ^ (r << (ds - dr))
            return gfelem(gfgcd(s_, r, v_, u), irred)

    def __int__(self) -> int:
        return bitvector.to_int(self.v)

    @staticmethod
    def to_int(x: 'gfelem') -> int:
        return bitvector.to_int(x.v)


# Typed versions of all python functions that can be used in specs.
class speclib:
    def ceil(x: int) -> nat_t:
        return nat(ceil(x))

    def log(x: int, b: int) -> int:
        return log(x, b)
