from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple, Callable

nat = NewType('nat', int)     # Should be a refinement type
felem = NewType('felem', int)  # Should be a refinement type


class Error(Exception):
    pass


def fail(s):
    raise Error(s)


class uintn:
    def __init__(self, x: int, bits: int) -> None:
        if x < 0:
            fail("cannot convert negative integer to uintn")
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

    def __add__(self, other: 'uintn') -> 'uintn':
        if (other.bits == self.bits):
            return uintn(self.v + other.v, self.bits)
        else:
            fail("cannot add uintn of different lengths")
            return uintn(0, self.bits)

    def __sub__(self, other: 'uintn') -> 'uintn':
        if (other.bits == self.bits):
            return uintn(self.v - other.v, self.bits)
        else:
            fail("cannot sub uintn of different lengths")
            return uintn(0, self.bits)

    def __or__(self, other: 'uintn') -> 'uintn':
        if (other.bits == self.bits):
            return uintn(self.v | other.v, self.bits)
        else:
            fail("cannot or uintn of different lengths")
            return uintn(0, self.bits)

    def __and__(self, other: 'uintn') -> 'uintn':
        if (other.bits == self.bits):
            return uintn(self.v & other.v, self.bits)
        else:
            fail("cannot and uintn of different lengths")
            return uintn(0, self.bits)

    def __xor__(self, other: 'uintn') -> 'uintn':
        if (other.bits == self.bits):
            return uintn(self.v ^ other.v, self.bits)
        else:
            fail("cannot xor uintn of different lengths")
            return uintn(0, self.bits)

    def __lshift__(self, other: int) -> 'uintn':
        if other < 0 or other >= self.max:
            fail("uintn cannot be shifted by < 0 or >= max")
            return uintn(0, self.bits,)
        else:
            return uintn(self.v << other, self.bits)

    def __rshift__(self, other: int) -> 'uintn':
        if other < 0 or other >= self.max:
            fail("uintn cannot be shifted by < 0 or >= max")
            return uintn(0, self.bits)
        else:
            return uintn(self.v >> other, self.bits)

    def __invert__(self) -> 'uintn':
        return uintn(~self.v & self.max, self.bits)

    def __eq__(self, other: Any) -> Any:
        # See https://github.com/python/mypy/issues/2783
        return (self.bits == other.bits and self.v == other.v)

    @staticmethod
    def num_bits(x: 'uintn') -> int:
        return x.bits

    @staticmethod
    def int_value(x: 'uintn') -> int:
        return x.v

    @staticmethod
    def rotate_left(x: 'uintn', other: int) -> 'uintn':
        return (x << other | x >> (x.bits - other))

    @staticmethod
    def rotate_right(x: 'uintn', other: int) -> 'uintn':
        return (x >> other | x << (x.bits - other))

    @staticmethod
    def to_bytes_be(x: 'uintn') -> 'array[uint8]':
        return array([uint8(b) for b in x.v.to_bytes(8, byteorder='big')])

    @staticmethod
    def from_u8array(x: 'array[uint8]') -> 'uintn':
        r = 0
        l = len(x) * 8
        for i, b in enumerate(x):
            r |= int(x[i].v) << (8 * (3 - i))
        return uintn(r, l)


class bit(uintn):
    def __init__(self, v: Union[int, uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 1)
        else:
            super().__init__(uintn.int_value(v), 1)


class uint8(uintn):
    def __init__(self, v: Union[int, uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 8)
        else:
            super().__init__(uintn.int_value(v), 8)


class uint16(uintn):
    def __init__(self, v: Union[int, uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 16)
        else:
            super().__init__(uintn.int_value(v), 16)


class uint32(uintn):
    def __init__(self, v: Union[int, uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 32)
        else:
            super().__init__(uintn.int_value(v), 32)


class uint64(uintn):
    def __init__(self, v: Union[int, uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 64)
        else:
            super().__init__(uintn.int_value(v), 64)


class uint128(uintn):
    def __init__(self, v: Union[int, uintn]) -> None:
        if isinstance(v, int):
            super().__init__(v, 128)
        else:
            super().__init__(uintn.int_value(v), 128)


T = TypeVar('T')
U = TypeVar('U')


class array(Iterable[T]):
    def __init__(self, x: Sequence[T]) -> None:
        self.l = list(x)

    def __len__(self) -> int:
        return len(self.l)

    def __str__(self) -> str:
        return str(self.l)

    def __repr__(self) -> str:
        return repr(self.l)

    def __iter__(self) -> Iterator[T]:
        return iter(self.l)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.l == other.l)
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return (self.l != other.l)
        else:
            return True

    def __getitem__(self, key: Union[int, slice]):
        try:
            if isinstance(key, slice):
                return array(self.l[key.start:key.stop])
            return self.l[key]
        except:
            print('Array access error:')
            print('array content:', self.l)
            print('array index:', key)
            fail('array index error')

    def __getslice__(self, i: int, j: int) -> 'array[T]':
        return array(self.l[i:j])

    def set(self, key: Union[int, Tuple[int, int]], v) -> 'array[T]':
        if isinstance(key, Tuple):
            tmp = self.l.copy()
            tmp[key[0]:key[1]] = v
            return array(tmp)
        else:
            tmp = self.l.copy()
            tmp[key] = v
            return array(tmp)

    # def append(self, x:T) -> None:
    #     self.l = self.l[len(self.l):] = [x]
    #     return None

    def extend(self, x: 'array[T]') -> 'array[T]':
        tmp = self.l.copy()
        tmp[len(tmp):] = x.l
        return array(tmp)

    def split(self, blocksize: int) -> 'array[array[T]]':
        return array([array(self.l[x:x+blocksize]) for x in range(0, len(self.l), blocksize)])

    def to_int(self) -> int:
        # This doesn't typecheck with mypy
        result_int = 0
        for (i, b) in enumerate(self.l):
            result_int |= int(b.v) << (i*32)
        return result_int

    @staticmethod
    def create(default: T, len: int) -> 'array[T]':
        return array([default] * len)

    @staticmethod
    def create_type(x: Iterable[U], T) -> 'array[T]':
        return array(list([T(el) for el in x]))

    @staticmethod
    def len(a: 'array[T]') -> int:
        return len(a.l)

    @staticmethod
    def copy(x: 'array[T]') -> 'array[T]':
        return array(x.l[:])

    @staticmethod
    def concat(x: 'array[T]', y: 'array[T]') -> 'array[T]':
        return array(x.l[:]+y.l[:])

    @staticmethod
    def zip(x: 'array[T]', y: 'array[U]') -> 'array[Tuple[T,U]]':
        return array(list(zip(x.l, y.l)))

    @staticmethod
    def enumerate(x: 'array[T]') -> 'array[Tuple[int,T]]':
        return array(list(enumerate(x.l)))

    @staticmethod
    def split_blocks(a: 'array[T]', blocksize: int) -> 'array[array[T]]':
        return array([a[x:x+blocksize] for x in range(0, len(a), blocksize)])

    @staticmethod
    def concat_blocks(blocks: 'array[array[T]]') -> 'array[T]':
        return (array([b for block in blocks for b in block]))

    @staticmethod
    def map(f: Callable[[T], U], a: 'array[T]') -> 'array[U]':
        return array(list(map(f, a.l)))

    @staticmethod
    def reduce(f: Callable[[T, U], U], a: 'array[T]', init: U) -> U:
        acc = init
        for i in range(len(a)):
            acc = f(a[i], acc)
        return acc


class bytes(array[uint8]):
    @staticmethod
    def from_ints(x: List[int]) -> array[uint8]:
        return array([uint8(i) for i in x])

    @staticmethod
    def concat_bytes(blocks: 'array[array[uint8]]') -> 'array[uint8]':
        concat = [b for block in blocks for b in block]
        return array(concat)

    @staticmethod
    def from_hex(x: str) -> array[uint8]:
        return array([uint8(int(x[i:i+2], 16)) for i in range(0, len(x), 2)])

    @staticmethod
    def from_uint32_le(x: uint32) -> array[uint8]:
        xv = uint32.int_value(x)
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
        return array([x0, x1, x2, x3])

    @staticmethod
    def to_uint32_le(x: array[uint8]) -> uint32:
        x0 = uint8.int_value(x[0])
        x1 = uint8.int_value(x[1]) << 8
        x2 = uint8.int_value(x[2]) << 16
        x3 = uint8.int_value(x[3]) << 24
        return uint32(x0 + x1 + x2 + x3)

    @staticmethod
    def from_uint64_le(x: uint64) -> array[uint8]:
        xv = uint64.int_value(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a: array[uint8] = array.create(uint8(0), 8)
        a = a.set((0, 4), bytes.from_uint32_le(x0))
        a = a.set((4, 8), bytes.from_uint32_le(x1))
        return a

    @staticmethod
    def to_uint64_le(x: array[uint8]) -> uint64:
        x0 = bytes.to_uint32_le(x[0:4])
        x1 = bytes.to_uint32_le(x[4:8])
        return uint64(uint32.int_value(x0) +
                      (uint32.int_value(x1) << 32))

    @staticmethod
    def from_uint128_le(x: uint128) -> array[uint8]:
        xv = uint128.int_value(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = array.create(uint8(0), 16)
        a = a.set((0, 8), bytes.from_uint64_le(x0))
        a = a.set((8, 16), bytes.from_uint64_le(x1))
        return a

    @staticmethod
    def to_uint128_le(x: array[uint8]) -> uint128:
        x0 = bytes.to_uint64_le(x[0:8])
        x1 = bytes.to_uint64_le(x[8:16])
        return uint128(uint64.int_value(x0) +
                       (uint64.int_value(x1) << 64))

    @staticmethod
    def from_uint32s_le(x: array[uint32]) -> array[uint8]:
        by = array([bytes.from_uint32_le(i) for i in x])
        return(array.concat_blocks(by))

    @staticmethod
    def to_uint32s_le(x: array[uint8]) -> array[uint32]:
        return(array([bytes.to_uint32_le(i) for i in array.split_blocks(x, 4)]))


def precondition(*types):
    def precondition_decorator(func):
        assert(len(types) == func.__code__.co_argcount)

        def wrapper(*args, **kwds):
            for (a, t) in zip(args, types):
                if not isinstance(t, str):
                    # Check type.
                    assert isinstance(
                        a, t), "arg %r does not match %s" % (a, t)
                else:
                    # Parse string as condition on variable
                    r = eval(str(a) + t)
                    if not r:
                        print("Precondition " + str(a) + t + " did not hold.")
                        assert False, "Precondition %r %s did not hold." % (
                            a, t)
            return func(*args, **kwds)
        wrapper.func_name = func.__name__
        return wrapper
    return precondition_decorator
