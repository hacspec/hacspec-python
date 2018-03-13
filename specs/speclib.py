from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple, Callable

nat = NewType('nat', int)     # Should be a refinement type
felem = NewType('felem', int)  # Should be a refinement type


class Error(Exception):
    pass


def fail(s):
    raise Error(s)


class uint8:
    def __init__(self, x: int) -> None:
        if x < 0:
            fail("cannot convert negative integer to uint8")
        else:
            self.v = x & 0xff

    def __str__(self) -> str:
        return hex(self.v)

    def __repr__(self) -> str:
        return hex(self.v)

    def __add__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v + other.v)

    def __sub__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v - other.v)

    def __or__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v | other.v)

    def __and__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v & other.v)

    def __xor__(self, other: 'uint8') -> 'uint8':
        return uint8(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint8':
        if other < 0 or other >= 8:
            fail("uint8 cannot be shifted by < 0 or >= 8")
        return uint8(self.v << other)

    def __rshift__(self, other: int) -> 'uint8':
        if other < 0 or other >= 8:
            fail("uint8 cannot be shifted by < 0 or >= 8")
        return uint8((self.v & 0xff) >> other)
    # See https://github.com/python/mypy/issues/2783

    def __eq__(self, other: Any) -> Any:
        return self.v == other.v

    @staticmethod
    def rotate_left(x: 'uint8', other: int) -> 'uint8':
        return (x << other | x >> (8 - other))

    @staticmethod
    def rotate_right(x: 'uint8', other: int) -> 'uint8':
        return (x >> other | x << (8 - other))

    @staticmethod
    def int_value(x: 'uint8') -> int:
        return x.v


class uint32:
    def __init__(self, x: int) -> None:
        if x < 0:
            fail("cannot convert negative integer to uint32")
        else:
            self.v = x & 0xffffffff

    def __str__(self) -> str:
        return hex(self.v)

    def __repr__(self) -> str:
        return hex(self.v)

    def __add__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v + other.v)

    def __sub__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v - other.v)

    def __or__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v | other.v)

    def __and__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v & other.v)

    def __xor__(self, other: 'uint32') -> 'uint32':
        return uint32(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint32':
        if other < 0 or other >= 32:
            fail("uint32 cannot be shifted by < 0 or >= 32")
        return uint32(self.v << other)

    def __rshift__(self, other: int) -> 'uint32':
        if other < 0 or other >= 32:
            fail("uint32 cannot be shifted by < 0 or >= 32")
        return uint32((self.v & 0xffffffff) >> other)
    # See https://github.com/python/mypy/issues/2783

    def __eq__(self, other: Any) -> Any:
        return self.v == other.v

    def __invert__(self) -> 'uint32':
        return uint32(~self.v & 0xffffffff)

    @staticmethod
    def rotate_left(x: 'uint32', other: int) -> 'uint32':
        return (x << other | x >> (32 - other))

    @staticmethod
    def rotate_right(x: 'uint32', other: int) -> 'uint32':
        return (x >> other | x << (32 - other))

    @staticmethod
    def int_value(x: 'uint32') -> int:
        return x.v


class uint64:
    def __init__(self, x: int) -> None:
        if x < 0:
            fail("cannot convert negative integer to uint64")
        else:
            self.v = x & 0xffffffffffffffff

    def __str__(self) -> str:
        return hex(self.v)

    def __repr__(self) -> str:
        return hex(self.v)

    def __add__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v + other.v)

    def __sub__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v - other.v)

    def __or__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v | other.v)

    def __and__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v & other.v)

    def __xor__(self, other: 'uint64') -> 'uint64':
        return uint64(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint64':
        if other < 0 or other >= 64:
            fail("uint64 cannot be shifted by < 0 or >= 64")
        return uint64(self.v << other)

    def __rshift__(self, other: int) -> 'uint64':
        if other < 0 or other >= 64:
            fail("uint64 cannot be shifted by < 0 or >= 64")
        return uint64((self.v & 0xffffffff) >> other)
    # See https://github.com/python/mypy/issues/2783

    def __eq__(self, other: Any) -> Any:
        return self.v == other.v

    @staticmethod
    def rotate_left(x: 'uint64', other: int) -> 'uint64':
        return (x << other | x >> (64 - other))

    @staticmethod
    def rotate_right(x: 'uint64', other: int) -> 'uint64':
        return (x >> other | x << (64 - other))

    @staticmethod
    def int_value(x: 'uint64') -> int:
        return x.v


class uint128:
    def __init__(self, x: int) -> None:
        if x < 0:
            fail("cannot convert negative integer to uint128")
        else:
            self.v = x & 0xffffffffffffffffffffffffffffffff

    def __str__(self) -> str:
        return hex(self.v)

    def __repr__(self) -> str:
        return hex(self.v)

    def __add__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v + other.v)

    def __sub__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v - other.v)

    def __or__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v | other.v)

    def __and__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v & other.v)

    def __xor__(self, other: 'uint128') -> 'uint128':
        return uint128(self.v ^ other.v)

    def __lshift__(self, other: int) -> 'uint128':
        if other < 0 or other >= 128:
            fail("uint128 cannot be shifted by < 0 or >= 128")
        return uint128(self.v << other)

    def __rshift__(self, other: int) -> 'uint128':
        if other < 0 or other >= 128:
            fail("uint128 cannot be shifted by < 0 or >= 128")
        return uint128((self.v & 0xffffffff) >> other)
    # See https://github.com/python/mypy/issues/2783

    def __eq__(self, other: Any) -> Any:
        return self.v == other.v

    @staticmethod
    def rotate_left(x: 'uint128', other: int) -> 'uint128':
        return (x << other | x >> (128 - other))

    @staticmethod
    def rotate_right(x: 'uint128', other: int) -> 'uint128':
        return (x >> other | x << (128 - other))

    @staticmethod
    def int_value(x: 'uint128') -> int:
        return x.v


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

    def __setitem__(self, key: Union[int, slice], v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v
        else:
            self.l[key] = v

    def append(self, x: T) -> None:
        self.l = self.l[len(self.l):] = [x]
        return None

    def extend(self, x: 'array[T]') -> None:
        self.l[len(self.l):] = x.l
        return None

    def split(self, blocksize: int) -> 'array[array[T]]':
        return array([array(self.l[x:x+blocksize]) for x in range(0, len(self.l), blocksize)])

    @staticmethod
    def to_int(x: 'array[uint32]') -> int:
        result_int = 0
        for (i, b) in enumerate(x):
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
    def zip(x: 'array[T]', y: 'array[U]') -> 'array[Tuple[T,U]]':
        return array(list(zip(x.l, y.l)))

    @staticmethod
    def enumerate(x: 'array[T]') -> 'array[Tuple[int,T]]':
        return array(list(enumerate(x.l)))

    @staticmethod
    def map(f: Callable[[T], U], a: 'array[T]') -> 'array[U]':
        return array(list(map(f, a)))

    @staticmethod
    def split_blocks(a: 'array[T]', blocksize: int) -> 'array[array[T]]':
        return array([a[x:x+blocksize] for x in range(0, len(a), blocksize)])

    @staticmethod
    def concat_blocks(blocks: 'array[array[T]]') -> 'array[T]':
        return (array([b for block in blocks for b in block]))


class bytes(array[uint8]):
    @staticmethod
    def from_ints(x: List[int]) -> array[uint8]:
        return array([uint8(i) for i in x])

    @staticmethod
    def concat(blocks: 'array[array[uint8]]') -> 'array[uint8]':
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
        a[0:4] = bytes.from_uint32_le(x0)
        a[4:8] = bytes.from_uint32_le(x1)
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
        a[0:8] = bytes.from_uint64_le(x0)
        a[8:16] = bytes.from_uint64_le(x1)
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
