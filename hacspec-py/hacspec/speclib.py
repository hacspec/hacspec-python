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
            elif num_init_args == 2:
                super().__init__(x)
            elif num_init_args == 0:
                # Special case for typeguard. Don't do anything.
                return
            else:
                fail("refine super.init has more args than we expected (" + str(num_init_args) + ")")
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

class _uintn:
    @typechecked
    def __init__(self, x: int, bits: int) -> None:
        if x < 0:
            fail("cannot convert negative integer to _uintn")
        elif bits < 1:
            fail("cannot create uint of size <= 0 bits")
        else:
            self.bits = bits
            self.max = (1 << bits) - 1
            self.v = x & self.max

    @typechecked
    def __str__(self) -> str:
        return hex(self.v)

    @typechecked
    def __repr__(self) -> str:
        return hex(self.v)

    @typechecked
    def __eq__(self, other) -> bool:
        if not isinstance(other, _uintn):
            fail("You can only compare two uints.")
        return (self.bits == other.bits and self.v == other.v)

    @staticmethod
    @typechecked
    def num_bits(x: '_uintn') -> int:
        if not isinstance(x, _uintn):
            fail("num_bits is only valid for uintN.")
        return x.bits

    @typechecked
    def __int__(self) -> int:
        return self.v

    @staticmethod
    @typechecked
    def to_int(x: '_uintn') -> int:
        if not isinstance(x, _uintn):
            fail("to_int is only valid for uintN.")
        return x.v

    @staticmethod
    @typechecked
    def to_nat(x: '_uintn') -> nat_t:
        if not isinstance(x, _uintn):
            fail("to_int is only valid for uintN.")
        return nat(x.v)


class bit(_uintn):
    @typechecked
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 1)
        else:
            if not isinstance(v, _uintn):
                fail("bit() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 1)

    @typechecked
    def __add__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("+ is only valid for two bit.")
        return bit(self.v + other.v)

    @typechecked
    def __sub__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("- is only valid for two bit.")
        return bit(self.v - other.v)

    @typechecked
    def __mul__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("* is only valid for two bit.")
        return bit(self.v * other.v)

    @typechecked
    def __inv__(self) -> 'bit':
        return bit(~ self.v)

    @typechecked
    def __invert__(self) -> 'bit':
        return bit(~ self.v & self.max)

    @typechecked
    def __or__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("| is only valid for two bit.")
        return bit(self.v | other.v)

    @typechecked
    def __and__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("& is only valid for two bit.")
        return bit(self.v & other.v)

    @typechecked
    def __xor__(self, other: 'bit') -> 'bit':
        if not isinstance(other, bit):
            fail("^ is only valid for two bit.")
        return bit(self.v ^ other.v)

    @typechecked
    def __lshift__(self, other: int) -> 'bit':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return bit(self.v << other)

    @typechecked
    def __rshift__(self, other: int) -> 'bit':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return bit(self.v >> other)

    @staticmethod
    @typechecked
    def rotate_left(x: 'bit', other: int) -> 'bit':
        if not isinstance(x, bit):
            fail("rotate_left is only valid for bit.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    @typechecked
    def rotate_right(x: 'bit', other: int) -> 'bit':
        if not isinstance(x, bit):
            fail("rotate_right is only valid for bit.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint8(_uintn):
    @typechecked
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 8)
        else:
            if not isinstance(v, _uintn):
                fail("uint8() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 8)

    @typechecked
    def __add__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("+ is only valid for two uint8_t.")
        return uint8(self.v + other.v)

    @typechecked
    def __sub__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("- is only valid for two uint8_t.")
        return uint8(self.v - other.v)

    @typechecked
    def __mul__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("* is only valid for two uint8_t.")
        return uint8(self.v * other.v)

    @typechecked
    def __inv__(self) -> 'uint8':
        return uint8(~ self.v)

    @typechecked
    def __invert__(self) -> 'uint8':
        return uint8(~ self.v & self.max)

    @typechecked
    def __or__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("| is only valid for two uint8_t.")
        return uint8(self.v | other.v)

    @typechecked
    def __and__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("& is only valid for two uint8_t.")
        return uint8(self.v & other.v)

    @typechecked
    def __xor__(self, other: 'uint8') -> 'uint8':
        if not isinstance(other, uint8):
            fail("^ is only valid for two uint8_t.")
        return uint8(self.v ^ other.v)

    @typechecked
    def __lshift__(self, other: int) -> 'uint8':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint8(self.v << other)

    @typechecked
    def __rshift__(self, other: int) -> 'uint8':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint8(self.v >> other)

    @staticmethod
    @typechecked
    def rotate_left(x: 'uint8', other: int) -> 'uint8':
        if not isinstance(x, uint8):
            fail("rotate_left is only valid for uint8_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    @typechecked
    def rotate_right(x: 'uint8', other: int) -> 'uint8':
        if not isinstance(x, uint8):
            fail("rotate_right is only valid for uint8_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint16(_uintn):
    @typechecked
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 16)
        else:
            if not isinstance(v, _uintn):
                fail("uint16() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 16)

    @typechecked
    def __add__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("+ is only valid for two uint16_t.")
        return uint16(self.v + other.v)

    @typechecked
    def __sub__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("- is only valid for two uint16_t.")
        return uint16(self.v - other.v)

    @typechecked
    def __mul__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("* is only valid for two uint16_t.")
        return uint16(self.v * other.v)

    @typechecked
    def __inv__(self) -> 'uint16':
        return uint16(~ self.v)

    @typechecked
    def __invert__(self) -> 'uint16':
        return uint16(~ self.v & self.max)

    @typechecked
    def __or__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("| is only valid for two uint16_t.")
        return uint16(self.v | other.v)

    @typechecked
    def __and__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("& is only valid for two uint16_t.")
        return uint16(self.v & other.v)

    @typechecked
    def __xor__(self, other: 'uint16') -> 'uint16':
        if not isinstance(other, uint16):
            fail("^ is only valid for two uint16_t.")
        return uint16(self.v ^ other.v)

    @typechecked
    def __lshift__(self, other: int) -> 'uint16':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint16(self.v << other)

    @typechecked
    def __rshift__(self, other: int) -> 'uint16':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint16(self.v >> other)

    @staticmethod
    @typechecked
    def rotate_left(x: 'uint16', other: int) -> 'uint16':
        if not isinstance(x, uint16):
            fail("rotate_left is only valid for uint16_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    @typechecked
    def rotate_right(x: 'uint16', other: int) -> 'uint16':
        if not isinstance(x, uint16):
            fail("rotate_right is only valid for uint16_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint32(_uintn):
    @typechecked
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 32)
        else:
            if not isinstance(v, _uintn):
                fail("uint32() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 32)

    @typechecked
    def __add__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("+ is only valid for two uint32_t.")
        return uint32(self.v + other.v)

    @typechecked
    def __sub__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("- is only valid for two uint32_t.")
        return uint32(self.v - other.v)

    @typechecked
    def __mul__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("* is only valid for two uint32_t.")
        return uint32(self.v * other.v)

    @typechecked
    def __inv__(self) -> 'uint32':
        return uint32(~ self.v)

    @typechecked
    def __invert__(self) -> 'uint32':
        return uint32(~ self.v & self.max)

    @typechecked
    def __or__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("| is only valid for two uint32_t.")
        return uint32(self.v | other.v)

    @typechecked
    def __and__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("& is only valid for two uint32_t.")
        return uint32(self.v & other.v)

    @typechecked
    def __xor__(self, other: 'uint32') -> 'uint32':
        if not isinstance(other, uint32):
            fail("^ is only valid for two uint32_t.")
        return uint32(self.v ^ other.v)

    @typechecked
    def __lshift__(self, other: int) -> 'uint32':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint32(self.v << other)

    @typechecked
    def __rshift__(self, other: int) -> 'uint32':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint32(self.v >> other)

    @staticmethod
    @typechecked
    def rotate_left(x: 'uint32', other: int) -> 'uint32':
        if not isinstance(x, uint32):
            fail("rotate_left is only valid for uint32_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    @typechecked
    def rotate_right(x: 'uint32', other: int) -> 'uint32':
        if not isinstance(x, uint32):
            fail("rotate_right is only valid for uint32_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint64(_uintn):
    @typechecked
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 64)
        else:
            if not isinstance(v, _uintn):
                fail("uint64() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 64)

    @typechecked
    def __add__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("+ is only valid for two uint64_t.")
        return uint64(self.v + other.v)

    @typechecked
    def __sub__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("- is only valid for two uint64_t.")
        return uint64(self.v - other.v)

    @typechecked
    def __mul__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("* is only valid for two uint64_t.")
        return uint64(self.v * other.v)

    @typechecked
    def __inv__(self) -> 'uint64':
        return uint64(~ self.v)

    @typechecked
    def __invert__(self) -> 'uint64':
        return uint64(~ self.v & self.max)

    @typechecked
    def __or__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("| is only valid for two uint64_t.")
        return uint64(self.v | other.v)

    @typechecked
    def __and__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("& is only valid for two uint64_t.")
        return uint64(self.v & other.v)

    @typechecked
    def __xor__(self, other: 'uint64') -> 'uint64':
        if not isinstance(other, uint64):
            fail("^ is only valid for two uint64_t. other is "+str(other))
        return uint64(self.v ^ other.v)

    @typechecked
    def __lshift__(self, other: int) -> 'uint64':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint64(self.v << other)

    @typechecked
    def __rshift__(self, other: int) -> 'uint64':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint64(self.v >> other)

    @staticmethod
    @typechecked
    def rotate_left(x: 'uint64', other: int) -> 'uint64':
        if not isinstance(x, uint64):
            fail("rotate_left is only valid for uint64_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    @typechecked
    def rotate_right(x: 'uint64', other: int) -> 'uint64':
        if not isinstance(x, uint64):
            fail("rotate_right is only valid for uint64_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class uint128(_uintn):
    @typechecked
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 128)
        else:
            if not isinstance(v, _uintn):
                fail("uint128() is only valid for int or uintN.")
            super().__init__(_uintn.to_int(v), 128)

    @typechecked
    def __add__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("+ is only valid for two uint128_t.")
        return uint128(self.v + other.v)

    @typechecked
    def __sub__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("- is only valid for two uint128_t.")
        return uint128(self.v - other.v)

    @typechecked
    def __mul__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("* is only valid for two uint128_t.")
        return uint128(self.v * other.v)

    @typechecked
    def __inv__(self) -> 'uint128':
        return uint128(~ self.v)

    @typechecked
    def __invert__(self) -> 'uint128':
        return uint128(~ self.v & self.max)

    @typechecked
    def __or__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("| is only valid for two uint128_t.")
        return uint128(self.v | other.v)

    @typechecked
    def __and__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("& is only valid for two uint128_t.")
        return uint128(self.v & other.v)

    @typechecked
    def __xor__(self, other: 'uint128') -> 'uint128':
        if not isinstance(other, uint128):
            fail("^ is only valid for two uint128_t.")
        return uint128(self.v ^ other.v)

    @typechecked
    def __lshift__(self, other: int) -> 'uint128':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint128(self.v << other)

    @typechecked
    def __rshift__(self, other: int) -> 'uint128':
        if not isinstance(other, int):
            fail("Shift value has to be int.")
        return uint128(self.v >> other)

    @staticmethod
    @typechecked
    def rotate_left(x: 'uint128', other: int) -> 'uint128':
        if not isinstance(x, uint128):
            fail("rotate_left is only valid for uint128_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x << other | x >> (x.bits - other))

    @staticmethod
    @typechecked
    def rotate_right(x: 'uint128', other: int) -> 'uint128':
        if not isinstance(x, uint128):
            fail("rotate_right is only valid for uint128_t.")
        if not isinstance(other, int):
            fail("Rotate value has to be int.")
        return (x >> other | x << (x.bits - other))


class _bitvector(_uintn):
    @typechecked
    def __init__(self, v: Union[int, _uintn], bits: int) -> None:
        if isinstance(v, int):
            super().__init__(v, bits)
        else:
            super().__init__(_uintn.to_int(v), bits)

    @staticmethod
    @typechecked
    def init(v: Union[int, _uintn]) -> '_bitvector':
        return _bitvector(v, 0)

    @typechecked
    def __add__(self, other: '_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
            return _bitvector(self.v + other.v, self.bits)
        else:
            fail("cannot add _bitvector of different lengths")
            return _bitvector(0, self.bits)

    @typechecked
    def __sub__(self, other: '_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
            return _bitvector(self.v - other.v, self.bits)
        else:
            fail("cannot sub _bitvector of different lengths")
            return _bitvector(0, self.bits)

    @typechecked
    def __inv__(self) -> '_bitvector':
        return _bitvector(~self.v, self.bits)

    @typechecked
    def __invert__(self) -> '_bitvector':
        return _bitvector(~self.v & self.max, self.bits)

    @typechecked
    def __or__(self, other: '_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
            return _bitvector(self.v | other.v, self.bits)
        else:
            fail("cannot or _bitvector of different lengths")
            return _bitvector(0, self.bits)

    @typechecked
    def __and__(self, other: '_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
            return _bitvector(self.v & other.v, self.bits)
        else:
            fail("cannot and _bitvector of different lengths")
            return _bitvector(0, self.bits)

    @typechecked
    def __xor__(self, other: '_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
            return _bitvector(self.v ^ other.v, self.bits)
        else:
            fail("cannot xor _bitvector of different lengths")
            return _bitvector(0, self.bits)

    @typechecked
    def __lshift__(self, other: int) -> '_bitvector':
        if other < 0 or other >= self.bits:
            fail("_bitvector cannot be shifted by < 0 or >= bits")
            return _bitvector(0, self.bits,)
        else:
            return _bitvector(self.v << other, self.bits)

    @typechecked
    def __rshift__(self, other: int) -> '_bitvector':
        if other < 0 or other >= self.bits:
            fail("_bitvector cannot be shifted by < 0 or >= bits")
            return _bitvector(0, self.bits)
        else:
            return _bitvector(self.v >> other, self.bits)

    @staticmethod
    @typechecked
    def rotate_left(x: '_bitvector', other: int) -> '_bitvector':
        return (x << other | x >> (x.bits - other))

    @staticmethod
    @typechecked
    def rotate_right(x: '_bitvector', other: int) -> '_bitvector':
        return (x >> other | x << (x.bits - other))

    @typechecked
    def __getitem__(self, key: Union[int, slice]):
        try:
            if isinstance(key, slice):
                return _bitvector(self.v >> key.start,
                                 key.stop - key.start)
            else:
                return bit(self.v >> key)
        except:
            print('_bitvector content:', self.v)
            print('_bitvector index:', key)
            fail('_bitvector access error')

    @typechecked
    def __getslice__(self, i: int, j: int) -> '_bitvector':
        return _bitvector(self.v >> i, j - i)


class array():
    def __init__(self) -> None:
        fail("Don't use array directly. Define one with array_t(your_type)")

    @staticmethod
    @typechecked
    def create(l: Union[int, _uintn], default) -> '_vlarray':
        if isinstance(l, _uintn):
            l = _uintn.to_int(l)
        res = _vlarray([default] * l)
        if isinstance(default, uint8_t):
            res = vlbytes_t(res)
        return res

    @staticmethod
    @typechecked
    def length(a: '_vlarray') -> int:
        if not isinstance(a, _vlarray):
            fail("array.length takes a _vlarray.")
        return len(a.l)

    @staticmethod
    @typechecked
    def copy(x: '_vlarray') -> '_vlarray':
        copy = _vlarray(x.l[:])
        if x.t and x.t.__name__ == "uint8":
            copy = vlbytes_t(copy)
        return copy

    @staticmethod
    @typechecked
    def concat(x: '_vlarray', y: '_vlarray') -> '_vlarray':
        if x.t and \
           (str(x.t.__name__) == "vlbytes_t" or str(x.t.__name__) == "_vlarray"):
            tmp = x.l[:]
            # TODO: only works with vlbytes_t
            tmp.append(vlbytes_t(y.l[:]))
            return _vlarray(tmp, x.t)
        res = _vlarray(x.l[:]+y.l[:], x.t)
        if x.t is uint8_t:
            res = vlbytes(res)
        return res

    @staticmethod
    @typechecked
    def zip(x: '_vlarray', y: '_vlarray') -> '_vlarray':
        return _vlarray(list(zip(x.l, y.l)))

    @staticmethod
    @typechecked
    def enumerate(x: '_vlarray') -> '_vlarray':
        return _vlarray(list(enumerate(x.l)))

    @staticmethod
    @typechecked
    def split_blocks(a: '_vlarray', blocksize: int) -> 'Tuple[_vlarray,_vlarray]':
        if not isinstance(a, _vlarray):
            fail("split_blocks takes a _vlarray as first argument.")
        if not isinstance(blocksize, int):
            fail("split_blocks takes an int as second argument.")
        nblocks = len(a) // blocksize
        blocks = _vlarray([a[x*blocksize:(x+1)*blocksize]
                          for x in range(nblocks)])
        last = _vlarray(a[len(a) - (len(a) % blocksize):len(a)])
        if not isinstance(blocks, vlbytes_t) and a.t and a.t.__name__ is "uint8":
            # Cast result to vlbytes_t if necessary.
            if isinstance(last, _vlarray):
                last = vlbytes_t(last)
        return blocks, last

    @staticmethod
    @typechecked
    def concat_blocks(blocks: '_vlarray', last: '_vlarray') -> '_vlarray':
        res = _vlarray.concat(_vlarray([b for block in blocks for b in block]), last)
        # TODO: make sure blcoska and last both have a type t
        if last.t and last.t.__name__ == "uint8":
            res = vlbytes_t(res)
        return res

    # Only used in ctr. Maybe delete
    @staticmethod
    @typechecked
    def map(f: Callable[[T], U], a: '_vlarray') -> '_vlarray':
        return _vlarray(list(map(f, a.l)))

    @staticmethod
    @typechecked
    def create_random(l: nat_t, t: Type[_uintn]) -> '_vlarray':
        if not isinstance(l, nat_t):
            fail("array.create_random's first argument has to be of type nat_t.")
        r = rand()
        x = t(0)
        return array(list([t(r.randint(0, x.max)) for _ in range(0, l)]))


class _vlarray(array):
    # TODO: make t arg mandatory
    @typechecked
    def __init__(self, x: Union[Sequence[T], '_vlarray'], t: Type=None) -> None:
        if not (isinstance(x, Sequence) or isinstance(x, _vlarray)):
            fail("_vlarray() takes a sequence or _vlarray as first argument.")
        if t:
            for e in x:
                if not isinstance(e, t) and t(e) is None:
                    fail("_vlarray() input element has wrong type. "+\
                         "Got "+str(type(e))+" expected "+str(t)+".")
        self.l = list(x)
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
    def __eq__(self, other: '_vlarray'):
        if isinstance(self, other.__class__) or isinstance(other, self.__class__):
            return self.l == other.l
        fail("_vlarray.__eq__ only works on two _vlarray.")

    @typechecked
    def __ne__(self, other: '_vlarray'):
        if isinstance(self, other.__class__) or isinstance(other, self.__class__):
            return self.l != other.l
        fail("_vlarray.__ne__ only works on two _vlarray.")

    # TODO: Return type should be Union['_vlarray', self.t] but we don't have
    #       access to self at this point.
    @typechecked
    def __getitem__(self, key: Union[int, slice]) -> Union['_vlarray', T]:
        try:
            if isinstance(key, slice):
                return _vlarray(self.l[key.start:key.stop])
            return self.l[key]
        except:
            print('_vlarray access error:')
            print('_vlarray content:', self.l)
            print('_vlarray index:', key)
            fail('_vlarray index error')

    @typechecked
    def __getslice__(self, i: int, j: int) -> '_vlarray':
        return _vlarray(self.l[i:j])

    @typechecked
    def __setitem__(self, key: Union[int, slice], v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v
        else:
            self.l[key] = v

class vlbytes_t(_vlarray):
    # FIXME
    # @typechecked
    def __init__(self, x: Union[Sequence[T], 'vlbytes_t']) -> None:
        super(vlbytes_t, self).__init__(x, uint8_t)

    # TODO: this wouldn't be necessary if we could return the correct type in _vlarray.
    @typechecked
    def __getitem__(self, key: Union[int, slice]) -> Union['vlbytes_t', T]:
        try:
            if isinstance(key, slice):
                return vlbytes_t(self.l[key.start:key.stop])
            return self.l[key]
        except:
            print('_vlarray access error:')
            print('_vlarray content:', self.l)
            print('_vlarray index:', key)
            fail('_vlarray index error')

    @staticmethod
    @typechecked
    def from_ints(x: List[int]) -> 'vlbytes_t':
        return vlbytes_t([uint8(i) for i in x])

    @staticmethod
    @typechecked
    def concat_bytes(blocks: '_vlarray') -> 'vlbytes_t':
        concat = [b for block in blocks for b in block]
        return vlbytes_t(concat)

    @staticmethod
    @typechecked
    def from_hex(x: str) -> 'vlbytes_t':
        return vlbytes_t([uint8(int(x[i:i+2], 16)) for i in range(0, len(x), 2)])

    @staticmethod
    @typechecked
    def to_hex(a: 'vlbytes_t') -> str:
        return "".join(['{:02x}'.format(uint8.to_int(x)) for x in a])

    @staticmethod
    @typechecked
    def from_nat_le(x: nat_t, l: nat_t=nat(0)) -> 'vlbytes_t':
        if not isinstance(x, nat_t):
            fail("bytes.from_nat_le's argument has to be of type nat.")
        b = x.to_bytes((x.bit_length() + 7) // 8, 'little') or b'\0'
        pad = _vlarray([uint8(0) for i in range(0, max(0, l-len(b)))])
        result = vlbytes_t([uint8(i) for i in b])
        return vlbytes_t(array.concat(pad, result))

    @staticmethod
    @typechecked
    def to_int_le(x: 'vlbytes_t') -> int:
        b = builtins.bytes([uint8.to_int(u) for u in x])
        return int.from_bytes(b, 'little')

    @staticmethod
    @typechecked
    def to_nat_le(x: 'vlbytes_t') -> nat_t:
        return nat(vlbytes_t.to_int_le(x))

    @staticmethod
    @typechecked
    def from_nat_be(x: nat_t, l: nat_t=nat(0)) -> 'vlbytes_t':
        if not isinstance(x, nat_t):
            fail("bytes.from_nat_be's first argument has to be of type nat_t.")
        if not isinstance(l, nat_t):
            fail("bytes.from_nat_be's second argument has to be of type nat_t.")
        b = x.to_bytes((x.bit_length() + 7) // 8, 'big') or b'\0'
        pad = _vlarray([uint8(0) for i in range(0, max(0, l-len(b)))])
        result = _vlarray([uint8(i) for i in b])
        return vlbytes_t(array.concat(pad, result))

    @staticmethod
    @typechecked
    def to_nat_be(x: 'vlbytes_t') -> nat_t:
        b = builtins.bytes([uint8.to_int(u) for u in x])
        return int.from_bytes(b, 'big')

    @staticmethod
    @typechecked
    def from_uint32_le(x: uint32) -> 'vlbytes_t':
        xv = uint32.to_int(x)
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
        return vlbytes_t([x0, x1, x2, x3])

    @staticmethod
    @typechecked
    def to_uint32_le(x: 'vlbytes_t') -> uint32:
        x0 = uint8.to_int(x[0])
        x1 = uint8.to_int(x[1]) << 8
        x2 = uint8.to_int(x[2]) << 16
        x3 = uint8.to_int(x[3]) << 24
        return uint32(x0 + x1 + x2 + x3)

    @staticmethod
    @typechecked
    def from_uint64_le(x: uint64) -> 'vlbytes_t':
        xv = uint64.to_int(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a: vlbytes_t = _vlarray.create(8, uint8(0))
        a[0:4] = vlbytes_t.from_uint32_le(x0)
        a[4:8] = vlbytes_t.from_uint32_le(x1)
        return a

    @staticmethod
    @typechecked
    def to_uint64_le(x: 'vlbytes_t') -> uint64:
        x0 = vlbytes_t.to_uint32_le(x[0:4])
        x1 = vlbytes_t.to_uint32_le(x[4:8])
        return uint64(uint32.to_int(x0) +
                      (uint32.to_int(x1) << 32))

    @staticmethod
    @typechecked
    def from_uint128_le(x: uint128) -> 'vlbytes_t':
        xv = uint128.to_int(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = _vlarray.create(16, uint8(0))
        a[0:8] = vlbytes_t.from_uint64_le(x0)
        a[8:16] = vlbytes_t.from_uint64_le(x1)
        return vlbytes_t(a)

    @staticmethod
    @typechecked
    def to_uint128_le(x: 'vlbytes_t') -> uint128:
        x0 = vlbytes_t.to_uint64_le(x[0:8])
        x1 = vlbytes_t.to_uint64_le(x[8:16])
        return uint128(uint64.to_int(x0) +
                       (uint64.to_int(x1) << 64))

    @staticmethod
    @typechecked
    def from_uint32_be(x: uint32) -> 'vlbytes_t':
        xv = uint32.to_int(x)
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
        return vlbytes_t([x3, x2, x1, x0])

    @staticmethod
    @typechecked
    def to_uint32_be(x: 'vlbytes_t') -> uint32:
        x0 = uint8.to_int(x[0]) << 24
        x1 = uint8.to_int(x[1]) << 16
        x2 = uint8.to_int(x[2]) << 8
        x3 = uint8.to_int(x[3])
        return uint32(x3 + x2 + x1 + x0)

    @staticmethod
    @typechecked
    def from_uint64_be(x: uint64) -> 'vlbytes_t':
        xv = uint64.to_int(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a: vlbytes_t = _vlarray.create(8, uint8(0))
        a[0:4] = vlbytes_t.from_uint32_be(x1)
        a[4:8] = vlbytes_t.from_uint32_be(x0)
        return a

    @staticmethod
    @typechecked
    def to_uint64_be(x: 'vlbytes_t') -> uint64:
        x0 = vlbytes_t.to_uint32_be(x[0:4])
        x1 = vlbytes_t.to_uint32_be(x[4:8])
        return uint64(uint32.to_int(x1) +
                      (uint32.to_int(x0) << 32))

    @staticmethod
    @typechecked
    def from_uint128_be(x: uint128) -> 'vlbytes_t':
        xv = uint128.to_int(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = vlbytes_t(_vlarray.create(16, uint8(0)))
        a[0:8] = vlbytes_t.from_uint64_be(x1)
        a[8:16] = vlbytes_t.from_uint64_be(x0)
        return a

    @staticmethod
    @typechecked
    def to_uint128_be(x: 'vlbytes_t') -> uint128:
        x0 = vlbytes_t.to_uint64_be(x[0:8])
        x1 = vlbytes_t.to_uint64_be(x[8:16])
        return uint128(uint64.to_int(x1) +
                       (uint64.to_int(x0) << 64))

    @staticmethod
    @typechecked
    def from_uint32s_le(x: _vlarray) -> 'vlbytes_t':
        by = _vlarray([vlbytes_t.from_uint32_le(i) for i in x])
        return vlbytes_t(_vlarray.concat_blocks(by, _vlarray([])))

    @staticmethod
    @typechecked
    def to_uint32s_le(x: 'vlbytes_t') -> _vlarray:
        nums, x = _vlarray.split_blocks(x, 4)
        if len(x) > 0:
            fail("array length not a multiple of 4")
        else:
            return(_vlarray([vlbytes_t.to_uint32_le(i) for i in nums]))

    @staticmethod
    @typechecked
    def from_uint32s_be(x: _vlarray) -> 'vlbytes_t':
        by = _vlarray([vlbytes_t.from_uint32_be(i) for i in x])
        return vlbytes_t(_vlarray.concat_blocks(by, _vlarray([])))

    @staticmethod
    @typechecked
    def to_uint32s_be(x: 'vlbytes_t') -> _vlarray:
        nums, x = _vlarray.split_blocks(x, 4)
        if len(x) > 0:
            fail("array length not a multiple of 4")
        else:
            return _vlarray([vlbytes_t.to_uint32_be(i) for i in nums])

    @staticmethod
    @typechecked
    def from_uint64s_be(x: _vlarray) -> 'vlbytes_t':
        by = _vlarray([vlbytes_t.from_uint64_be(i) for i in x])
        return vlbytes_t(_vlarray.concat_blocks(by, _vlarray([])))

    @staticmethod
    @typechecked
    def to_uint64s_be(x: 'vlbytes_t') -> _vlarray:
        nums, x = _vlarray.split_blocks(x, 8)
        if len(x) > 0:
            fail("array length not a multple of 8")
        else:
            return(_vlarray([vlbytes_t.to_uint64_be(i) for i in nums]))

    @staticmethod
    @typechecked
    def from_uint64s_le(x: _vlarray) -> 'vlbytes_t':
        by = _vlarray([vlbytes_t.from_uint64_le(i) for i in x])
        return vlbytes_t(_vlarray.concat_blocks(by, _vlarray([])))

    @staticmethod
    @typechecked
    def to_uint64s_le(x: 'vlbytes_t') -> _vlarray:
        nums, x = _vlarray.split_blocks(x, 8)
        if len(x) > 0:
            fail("array length not a multple of 8")
        else:
            return _vlarray([vlbytes_t.to_uint64_le(i) for i in nums])

    @staticmethod
    @typechecked
    def create_random_bytes(len: nat) -> 'vlbytes_t':
        r = rand()
        return vlbytes_t(list([uint8(r.randint(0, 0xFF)) for _ in range(0, len)]))


@typechecked
def bytes_t(l:int) -> type:
    __class__ = vlbytes_t
    @typechecked
    def init(self, x: Union[vlbytes_t, Sequence[T]]) -> None:
        if not (isinstance(x, Sequence) or isinstance(x, _vlarray)) or not len(x) == l:
            fail("Type error. You tried to use " + str(x) + " (" + str(type(x)) + ") with subtype of " + str(vlbytes_t) + ".")
        else:
            super().__init__(x)
            vlbytes_t(x)
    @typechecked
    def string(self) -> str:
        return str(self.__origin__)
    # We use a random string as class name here. The result of refine has to
    # get assigend to a type alias, which can be used as class name.
    u_rand = ''.join(random_string(ascii_uppercase + ascii_lowercase, k=15))
    if DEBUG:
        print("new class " + u_rand + " - " + str(vlbytes_t))
    cl = type(u_rand, (vlbytes_t,), {'__init__': init , '__origin__': vlbytes_t})
    __class__ = cl
    return cl


def bitvector_t(l:int):
    @typechecked
    def refine_bitvec() -> type:
        __class__ = _bitvector
        @typechecked
        def f(x:Union[int, _uintn]):
            return int(x) <= ((1 << l) - 1)
        @typechecked
        def init(self, x:Union[int, _uintn]) -> None:
            if not (isinstance(x, int) or isinstance(x, _uintn)) or not f(x):
                fail("Type error. You tried to use " + str(x) + " (" + str(type(x)) + ") with subtype of _bitvector.")
            else:
                super().__init__(x, l)
                _bitvector(x, l)
        @typechecked
        def string(self) -> str:
            return str(self.__origin__)
        # We use a random string as class name here. The result has to
        # get assigend to a type alias, which can be used as class name.
        u_rand = ''.join(random_string(ascii_uppercase + ascii_lowercase, k=15))
        if DEBUG:
            print("new class " + u_rand + " - " + str(_bitvector))
        cl = type(u_rand, (_bitvector,), {'__init__': init , '__origin__': _bitvector, '__str__': string})
        __class__ = cl
        return cl
    refinement = refine_bitvec()
    return refinement


@typechecked
def vlarray_t(t: type) -> type:
    @typechecked
    def refine_array() -> type:
        __class__ = _vlarray
        @typechecked
        def init(self, x: Union[Sequence[T], _vlarray]) -> None:
            if not (isinstance(x, Sequence) or isinstance(x, _vlarray)):
                fail("Type error. You tried to use " + str(x) + " (" + str(type(x)) + ") with subtype of array_t.")
            else:
                super().__init__(x, t)
                _vlarray(x, t)
        @typechecked
        def string(self) -> str:
            return str(self.__origin__)
        # We use a random string as class name here. The result has to
        # get assigend to a type alias, which can be used as class name.
        u_rand = ''.join(random_string(ascii_uppercase + ascii_lowercase, k=15))
        if DEBUG:
            print("new class " + u_rand + " - " + str(_vlarray))
        cl = type(u_rand, (_vlarray,), {'__init__': init , '__origin__': _vlarray})
        __class__ = cl
        return cl
    refinement = refine_array()
    return refinement


@typechecked
def array_t(t: type, l: int) -> type:
    @typechecked
    def refine_array() -> type:
        __class__ = _vlarray
        @typechecked
        def init(self, x: Union[Sequence[T], _vlarray]) -> None:
            if not (isinstance(x, Sequence) or isinstance(x, _vlarray)) or not len(x) == self.l:
                fail("Type error. You tried to use " + str(x) + " (" + str(type(x)) + ") with subtype of array_t.")
            else:
                super().__init__(x, t)
                _vlarray(x, t)
        @typechecked
        def string(self) -> str:
            return str(self.__origin__)
        # We use a random string as class name here. The result has to
        # get assigend to a type alias, which can be used as class name.
        u_rand = ''.join(random_string(ascii_uppercase + ascii_lowercase, k=15))
        if DEBUG:
            print("new class " + u_rand + " - " + str(_vlarray))
        cl = type(u_rand, (_vlarray,), {'__init__': init , '__origin__': _vlarray, '__str__': string, 'l': l})
        __class__ = cl
        return cl
    refinement = refine_array()
    return refinement


bit_t = bit
uint8_t = uint8
uint16_t = uint16
uint32_t = uint32
uint64_t = uint64
uint128_t = uint128

bytes = vlbytes_t
vlbytes = vlbytes_t


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
    def __init__(self, x: _bitvector, irred: _bitvector) -> None:
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
            return gfelem(_bitvector(0, self.bits), self.irred)

    def __sub__(self, other: 'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred):
            return gfelem(self.v ^ other.v, self.irred)
        else:
            fail("cannot sub gfelem of different fields")
            return gfelem(_bitvector(0, self.bits), self.irred)

    def __mul__(self, other: 'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred):
            bits = self.bits
            irred = self.irred
            a = self.v
            b = other.v
            p = _bitvector(0, bits)
            for i in range(bits):
                if (_bitvector.to_int(b) & 1 == 1):
                    p = p ^ a
                b = b >> 1
                c = a >> (bits - 1)
                a = a << 1
                if (_bitvector.to_int(a) == 1):
                    a = a ^ irred
            return gfelem(p, irred)
        else:
            fail("cannot mul gfelem of different fields")
            return gfelem(_bitvector(0, self.bits), self.irred)

    def __pow__(self, other: int) -> 'gfelem':
        if (other < 0):
            fail("cannot exp with negative number")
            return gfelem(_bitvector(0, self.bits), self.irred)
        else:
            def exp(a, x):
                if (x == 0):
                    return gfelem(_bitvector(1, self.bits), self.irred)
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

        def degree(v: _bitvector, bits: int):
            if (v == 0 or bits == 0):
                return 0
            elif (_bitvector.to_int(v >> (bits - 1)) == 1):
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
        v = gfelem(_bitvector(0, bits), irred)
        u = gfelem(_bitvector(1, bits), irred)
        if (dr == 0):
            return u
        else:
            s_ = s ^ (r << (ds - dr))
            v_ = v ^ (r << (ds - dr))
            return gfelem(gfgcd(s_, r, v_, u), irred)

    def __int__(self) -> int:
        return _bitvector.to_int(self.v)

    @staticmethod
    def to_int(x: 'gfelem') -> int:
        return _bitvector.to_int(x.v)


# Typed versions of all python functions that can be used in specs.
class speclib:
    @typechecked
    def ceil(x: int) -> nat_t:
        return nat(ceil(x))

    @typechecked
    def log(x: int, b: int) -> float:
        return log(x, b)
