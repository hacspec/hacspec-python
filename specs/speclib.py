from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple, Callable, Type, cast
from random import SystemRandom as rand
from math import ceil, log
from importlib import import_module
import builtins


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


def refine(t: type, f: Callable[[T], bool]) -> type:
    return t


def refine2(u: str, t: type, f: Callable[[T], bool]) -> Callable[[T], T]:
    def check(x) -> t:
        if not (isinstance(x, t) or f(x)):
            fail("Type error. You tried to use " + str(x) + " with " + u + ".")
        else:
            class_ = getattr(import_module("speclib"), u)
            return class_(x)
    return check

def refine3(u: str, t: type, f: Callable[[T], bool]) -> type:
    def init(s, x:t) -> None:
        if not (isinstance(x, t) or f(x)):
            fail("Type error. You tried to use " + str(x) + " with " + u + ".")
        else:
            t(x)
    cl = type(u, (t,), {'__init__': init})
    return cl

# nat = refine2('nat_t', int, lambda x: x >= 0)
# class nat_t(int): pass
nat = refine3('nat_t', int, lambda x: x >= 0)
nat_t = nat


def range_t(min, max):
    return refine(int, lambda x: x >= min and x < max)


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
        return x.bits

    def __int__(self) -> int:
        return self.v

    @staticmethod
    def to_int(x: '_uintn') -> int:
        return x.v


class bit(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 1)
        else:
            super().__init__(_uintn.to_int(v), 1)

    def __add__(self, other: 'bit') -> 'bit':
        return bit(self.v + other.v)

    def __sub__(self, other: 'bit') -> 'bit':
        return bit(self.v - other.v)

    def __mul__(self, other: 'bit') -> 'bit':
        return bit(self.v * other.v)

    def __inv__(self) -> 'bit':
        return bit(~ self.v)

    def __or__(self, other: 'bit') -> 'bit':
        return bit(self.v | other.v)

    def __and__(self, other: 'bit') -> 'bit':
        return bit(self.v & other.v)

    def __xor__(self, other: 'bit') -> 'bit':
        return bit(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'bit':
        return bit(self.v << other)

    def __rshift__(self, other: int) -> 'bit':
        return bit(self.v >> other)

    @staticmethod
    def rotate_left(x: 'bit', other: int) -> 'bit':
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'bit', other: int) -> 'bit':
        return (x >> other | x << (x.bits - other))


class uint8(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 8)
        else:
            super().__init__(_uintn.to_int(v), 8)

    def __add__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v + other.v)

    def __sub__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v - other.v)

    def __mul__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v * other.v)

    def __inv__(self) -> 'uint8':
        return uint8(~ self.v)

    def __or__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v | other.v)

    def __and__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v & other.v)

    def __xor__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint8':
        return uint8(self.v << other)

    def __rshift__(self, other: int) -> 'uint8':
        return uint8(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint8', other: int) -> 'uint8':
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint8', other: int) -> 'uint8':
        return (x >> other | x << (x.bits - other))


class uint16(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 16)
        else:
            super().__init__(_uintn.to_int(v), 16)

    def __add__(self, other: 'uint16') -> 'uint16':
        return uint16(self.v + other.v)

    def __sub__(self, other: 'uint16') -> 'uint16':
        return uint16(self.v - other.v)

    def __mul__(self, other: 'uint16') -> 'uint16':
        return uint16(self.v * other.v)

    def __inv__(self) -> 'uint16':
        return uint16(~ self.v)

    def __or__(self, other: 'uint16') -> 'uint16':
        return uint16(self.v | other.v)

    def __and__(self, other: 'uint16') -> 'uint16':
        return uint16(self.v & other.v)

    def __xor__(self, other: 'uint16') -> 'uint16':
        return uint16(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint16':
        return uint16(self.v << other)

    def __rshift__(self, other: int) -> 'uint16':
        return uint16(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint16', other: int) -> 'uint16':
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint16', other: int) -> 'uint16':
        return (x >> other | x << (x.bits - other))


class uint32(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 32)
        else:
            super().__init__(_uintn.to_int(v), 32)

    def __add__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v + other.v)

    def __sub__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v - other.v)

    def __mul__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v * other.v)

    def __inv__(self) -> 'uint32':
        return uint32(~ self.v)

    def __invert__(self) -> 'uint32':
        return uint32(~ self.v & self.max)

    def __or__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v | other.v)

    def __and__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v & other.v)

    def __xor__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint32':
        return uint32(self.v << other)

    def __rshift__(self, other: int) -> 'uint32':
        return uint32(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint32', other: int) -> 'uint32':
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint32', other: int) -> 'uint32':
        return (x >> other | x << (x.bits - other))


class uint64(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 64)
        else:
            super().__init__(_uintn.to_int(v), 64)

    def __add__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v + other.v)

    def __sub__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v - other.v)

    def __mul__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v * other.v)

    def __inv__(self) -> 'uint64':
        return uint64(~ self.v)

    def __invert__(self) -> 'uint64':
        return uint64(~ self.v & self.max)

    def __or__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v | other.v)

    def __and__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v & other.v)

    def __xor__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint64':
        return uint64(self.v << other)

    def __rshift__(self, other: int) -> 'uint64':
        return uint64(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint64', other: int) -> 'uint64':
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint64', other: int) -> 'uint64':
        return (x >> other | x << (x.bits - other))


class uint128(_uintn):
    def __init__(self, v: Union[int, _uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 128)
        else:
            super().__init__(_uintn.to_int(v), 128)

    def __add__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v + other.v)

    def __sub__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v - other.v)

    def __mul__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v * other.v)

    def __inv__(self) -> 'uint128':
        return uint128(~ self.v)

    def __or__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v | other.v)

    def __and__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v & other.v)

    def __xor__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint128':
        return uint128(self.v << other)

    def __rshift__(self, other: int) -> 'uint128':
        return uint128(self.v >> other)

    @staticmethod
    def rotate_left(x: 'uint128', other: int) -> 'uint128':
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uint128', other: int) -> 'uint128':
        return (x >> other | x << (x.bits - other))


class bitvector(_uintn):
    def __init__(self, v: Union[int, _uintn], bits: int) -> None:
        if isinstance(v, int):
            super().__init__(v, bits)
        else:
            super().__init__(_uintn.to_int(v), bits)

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


class vlarray(Iterable[T]):
    def __init__(self, x: Sequence[T], t: Type=None) -> None:
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
        # TODO: this shouldn't be necessary if we type check.
        if not isinstance(self, vlarray) or not isinstance(other, vlarray):
            fail("vlarray.__eq__ only works on two vlarray.")
        if str(other.t) == "speclib.vlbytes" or str(other.t) == "speclib.vlarray" \
           or str(type(other)) == "speclib.vlbytes" or str(type(other)) == "speclib.vlarray":
            return self.l == other.l
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.l != other.l
        else:
            return True

    def __getitem__(self, key: Union[int, slice]):
        try:
            if isinstance(key, slice):
                return vlarray(self.l[key.start:key.stop])
            return self.l[key]
        except:
            print('vlarray access error:')
            print('vlarray content:', self.l)
            print('vlarray index:', key)
            fail('vlarray index error')

    def __getslice__(self, i: int, j: int) -> 'vlarray[T]':
        return vlarray(self.l[i:j])

    def __setitem__(self, key: Union[int, slice], v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v
        else:
            self.l[key] = v

    @staticmethod
    def create(len: int, default) -> 'vlarray[T]':
        return vlarray([default] * len)

    @staticmethod
    def create_type(x: Iterable[U], t: type) -> 'vlarray[T]':
        return vlarray(list([t(el) for el in x]), t)

    @staticmethod
    def length(a: 'vlarray[T]') -> int:
        return len(a.l)

    @staticmethod
    def copy(x: 'vlarray[T]') -> 'vlarray[T]':
        return vlarray(x.l[:])

    @staticmethod
    def concat(x: 'vlarray[T]', y: 'vlarray[U]') -> 'vlarray[T]':
        if str(x.t) == "speclib.vlbytes" or str(x.t) == "speclib.vlarray":
            tmp = x.l[:]
            tmp.append(vlarray(y.l[:], type(y)))
            return vlarray(tmp, x.t)
        return vlarray(x.l[:]+y.l[:])

    @staticmethod
    def zip(x: 'vlarray[T]', y: 'vlarray[U]') -> 'vlarray[Tuple[T,U]]':
        return vlarray(list(zip(x.l, y.l)))

    @staticmethod
    def enumerate(x: 'vlarray[T]') -> 'vlarray[Tuple[int,T]]':
        return vlarray(list(enumerate(x.l)))

    @staticmethod
    def split_blocks(a: 'vlarray[T]', blocksize: int) -> 'Tuple[vlarray[vlarray[T]],vlarray[T]]':
        nblocks = len(a) // blocksize
        blocks = vlarray([a[x*blocksize:(x+1)*blocksize]
                          for x in range(nblocks)])
        last = vlarray(a[len(a) - (len(a) % blocksize):len(a)])
        return (blocks, last)

    @staticmethod
    def concat_blocks(blocks: 'vlarray[vlarray[T]]', last: 'vlarray[T]') -> 'vlarray[T]':
        return (vlarray.concat(vlarray([b for block in blocks for b in block]), last))

    # Only used in ctr. Maybe delete
    @staticmethod
    def map(f: Callable[[T], U], a: 'vlarray[T]') -> 'vlarray[U]':
        return vlarray(list(map(f, a.l)))

    @staticmethod
    def create_random(l: nat_t, t: Type[_uintn]) -> 'vlarray[t]':
        if not isinstance(l, nat_t):
            fail("array.create_random's first argument has to be of type nat_t.")
        r = rand()
        x = t(0)
        return array(list([t(r.randint(0, x.max)) for _ in range(0, l)]))


class vlbytes(vlarray[uint8]):
    @staticmethod
    def from_ints(x: List[int]) -> 'vlbytes':
        return vlarray([uint8(i) for i in x])

    @staticmethod
    def concat_bytes(blocks: 'vlarray[vlbytes]') -> 'vlbytes':
        concat = [b for block in blocks for b in block]
        return vlarray(concat)

    @staticmethod
    def from_hex(x: str) -> vlarray[uint8]:
        return vlarray([uint8(int(x[i:i+2], 16)) for i in range(0, len(x), 2)])

    @staticmethod
    def to_hex(a: vlarray[uint8]) -> str:
        return "".join(['{:02x}'.format(uint8.to_int(x)) for x in a])

    @staticmethod
    def from_nat_le(x: nat_t) -> 'vlbytes':
        if not isinstance(x, nat_t):
            fail("bytes.from_nat_le's argument has to be of type nat_t.")
        b = x.to_bytes((x.bit_length() + 7) // 8, 'little') or b'\0'
        return vlarray([uint8(i) for i in b])

    @staticmethod
    def to_nat_le(x: vlarray[uint8]) -> nat_t:
        b = builtins.bytes([uint8.to_int(u) for u in x])
        return nat(int.from_bytes(b, 'little'))

    @staticmethod
    def from_nat_be(x: nat_t, l: nat_t=nat(0)) -> 'vlbytes':
        if not isinstance(x, nat_t):
            fail("bytes.from_nat_be's first argument has to be of type nat_t.")
        if not isinstance(l, nat_t):
            fail("bytes.from_nat_be's second argument has to be of type nat_t.")
        b = x.to_bytes((x.bit_length() + 7) // 8, 'big') or b'\0'
        pad = vlarray([uint8(0) for i in range(0, max(0, l-len(b)))])
        result = vlarray([uint8(i) for i in b])
        return array.concat(pad, result)

    @staticmethod
    def to_nat_be(x: vlarray[uint8]) -> nat_t:
        b = builtins.bytes([uint8.to_int(u) for u in x])
        return int.from_bytes(b, 'big')

    @staticmethod
    def from_uint32_le(x: uint32) -> vlarray[uint8]:
        xv = uint32.to_int(x)
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
        return vlarray([x0, x1, x2, x3])

    @staticmethod
    def to_uint32_le(x: vlarray[uint8]) -> uint32:
        x0 = uint8.to_int(x[0])
        x1 = uint8.to_int(x[1]) << 8
        x2 = uint8.to_int(x[2]) << 16
        x3 = uint8.to_int(x[3]) << 24
        return uint32(x0 + x1 + x2 + x3)

    @staticmethod
    def from_uint64_le(x: uint64) -> vlarray[uint8]:
        xv = uint64.to_int(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a: vlarray[uint8] = vlarray.create(8, uint8(0))
        a[0:4] = vlbytes.from_uint32_le(x0)
        a[4:8] = vlbytes.from_uint32_le(x1)
        return a

    @staticmethod
    def to_uint64_le(x: vlarray[uint8]) -> uint64:
        x0 = vlbytes.to_uint32_le(x[0:4])
        x1 = vlbytes.to_uint32_le(x[4:8])
        return uint64(uint32.to_int(x0) +
                      (uint32.to_int(x1) << 32))

    @staticmethod
    def from_uint128_le(x: uint128) -> vlarray[uint8]:
        xv = uint128.to_int(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = vlarray.create(16, uint8(0))
        a[0:8] = vlbytes.from_uint64_le(x0)
        a[8:16] = vlbytes.from_uint64_le(x1)
        return a

    @staticmethod
    def to_uint128_le(x: vlarray[uint8]) -> uint128:
        x0 = vlbytes.to_uint64_le(x[0:8])
        x1 = vlbytes.to_uint64_le(x[8:16])
        return uint128(uint64.to_int(x0) +
                       (uint64.to_int(x1) << 64))

    @staticmethod
    def from_uint32_be(x: uint32) -> vlarray[uint8]:
        xv = uint32.to_int(x)
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
        return vlarray([x3, x2, x1, x0])

    @staticmethod
    def to_uint32_be(x: vlarray[uint8]) -> uint32:
        x0 = uint8.to_int(x[0]) << 24
        x1 = uint8.to_int(x[1]) << 16
        x2 = uint8.to_int(x[2]) << 8
        x3 = uint8.to_int(x[3])
        return uint32(x3 + x2 + x1 + x0)

    @staticmethod
    def from_uint64_be(x: uint64) -> vlarray[uint8]:
        xv = uint64.to_int(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a: vlarray[uint8] = vlarray.create(8, uint8(0))
        a[0:4] = vlbytes.from_uint32_be(x1)
        a[4:8] = vlbytes.from_uint32_be(x0)
        return a

    @staticmethod
    def to_uint64_be(x: vlarray[uint8]) -> uint64:
        x0 = vlbytes.to_uint32_be(x[0:4])
        x1 = vlbytes.to_uint32_be(x[4:8])
        return uint64(uint32.to_int(x1) +
                      (uint32.to_int(x0) << 32))

    @staticmethod
    def from_uint128_be(x: uint128) -> vlarray[uint8]:
        xv = uint128.to_int(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = vlarray.create(16, uint8(0))
        a[0:8] = vlbytes.from_uint64_be(x1)
        a[8:16] = vlbytes.from_uint64_be(x0)
        return a

    @staticmethod
    def to_uint128_be(x: vlarray[uint8]) -> uint128:
        x0 = vlbytes.to_uint64_be(x[0:8])
        x1 = vlbytes.to_uint64_be(x[8:16])
        return uint128(uint64.to_int(x1) +
                       (uint64.to_int(x0) << 64))

    @staticmethod
    def from_uint32s_le(x: vlarray[uint32]) -> vlarray[uint8]:
        by = vlarray([vlbytes.from_uint32_le(i) for i in x])
        return(vlarray.concat_blocks(by, vlarray([])))

    @staticmethod
    def to_uint32s_le(x: vlarray[uint8]) -> vlarray[uint32]:
        nums, x = vlarray.split_blocks(x, 4)
        if len(x) > 0:
            fail("array length not a multiple of 4")
        else:
            return(vlarray([vlbytes.to_uint32_le(i) for i in nums]))

    @staticmethod
    def from_uint32s_be(x: vlarray[uint32]) -> vlarray[uint8]:
        by = vlarray([vlbytes.from_uint32_be(i) for i in x])
        return(vlarray.concat_blocks(by, vlarray([])))

    @staticmethod
    def to_uint32s_be(x: vlarray[uint8]) -> vlarray[uint32]:
        nums, x = vlarray.split_blocks(x, 4)
        if len(x) > 0:
            fail("array length not a multiple of 4")
        else:
            return(vlarray([vlbytes.to_uint32_be(i) for i in nums]))

    @staticmethod
    def from_uint64s_be(x: vlarray[uint64]) -> vlarray[uint8]:
        by = vlarray([vlbytes.from_uint64_be(i) for i in x])
        return(vlarray.concat_blocks(by, vlarray([])))

    @staticmethod
    def to_uint64s_be(x: vlarray[uint8]) -> vlarray[uint64]:
        nums, x = vlarray.split_blocks(x, 8)
        if len(x) > 0:
            fail("array length not a multple of 8")
        else:
            return(vlarray([vlbytes.to_uint64_be(i) for i in nums]))

    @staticmethod
    def from_uint64s_le(x: vlarray[uint64]) -> vlarray[uint8]:
        by = vlarray([vlbytes.from_uint64_le(i) for i in x])
        return(vlarray.concat_blocks(by, vlarray([])))

    @staticmethod
    def to_uint64s_le(x: vlarray[uint8]) -> vlarray[uint64]:
        nums, x = vlarray.split_blocks(x, 8)
        if len(x) > 0:
            fail("array length not a multple of 8")
        else:
            return(vlarray([vlbytes.to_uint64_le(i) for i in nums]))

    @staticmethod
    def create_random_bytes(len: nat) -> 'vlarray[uint8]':
        r = rand()
        return array(list([uint8(r.randint(0, 0xFF)) for _ in range(0, len)]))


def vlbytes_t(T):
    return vlbytes


def bytes_t(len):
    return vlbytes


def bitvector_t(len: nat):
    return bitvector


def vlarray_t(t: type):
    return vlarray[t]


def array_t(t: type, len: int) -> vlarray[Any]:
    return vlarray[t]


bit_t = bit
uint8_t = uint8
uint16_t = uint16
uint32_t = uint32
uint64_t = uint64
uint128_t = uint128

array = vlarray
vlbytes = vlbytes
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

    def log(x: int, b: int) -> nat_t:
        return nat(log(x, b))
