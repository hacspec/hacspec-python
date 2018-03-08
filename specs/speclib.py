from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple

nat    = NewType('nat',int)     # Should be a refinement type
felem  = NewType('felem',int) # Should be a refinement type

class Error(Exception): pass

def fail(s):
    raise Error(s)

class uint8:
    def __init__(self,x:int) -> None:
        if x < 0:
            fail("cannot convert negative integer to uint8")
        else:
            self.v = x & 0xff
    def __str__(self) -> str:
        return hex(self.v)
    def __repr__(self) -> str:
        return hex(self.v)
    def __add__(self,other:'uint8') -> 'uint8':
        return uint8(self.v + other.v)
    def __sub__(self,other:'uint8') -> 'uint8':
        return uint8(self.v - other.v)
    def __or__(self,other:'uint8') -> 'uint8':
        return uint8(self.v | other.v)
    def __and__(self,other:'uint8') -> 'uint8':
        return uint8(self.v & other.v)
    def __xor__(self,other:'uint8') -> 'uint8':
        return uint8(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'uint8':
        if other < 0 or other >= 8:
            fail("uint8 cannot be shifted by < 0 or >= 8")
        return uint8(self.v << other)
    def __rshift__(self,other:int) -> 'uint8':
        if other < 0 or other >= 8:
            fail("uint8 cannot be shifted by < 0 or >= 8")
        return uint8((self.v & 0xff) >> other)
    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return self.v == other.v

    @staticmethod
    def rotate_left(x:'uint8',other:int) -> 'uint8':
        return (x << other | x >> (8 - other))
    @staticmethod
    def rotate_right(x:'uint8',other:int) -> 'uint8':
        return (x >> other | x << (8 - other))
    @staticmethod
    def int_value(x:'uint8') -> int:
        return x.v
    @staticmethod
    def from_bytes_le(n:bytes) -> 'uint8':
        return uint8(int.from_bytes(n,byteorder='little'))
    @staticmethod
    def to_bytes_le(x:'uint8') -> bytes:
        return x.v.to_bytes(1,byteorder='little')


class uint32:
    def __init__(self,x:int) -> None:
        if x < 0:
            fail("cannot convert negative integer to uint32")
        else:
            self.v = x & 0xffffffff
    def __str__(self) -> str:
        return hex(self.v)
    def __repr__(self) -> str:
        return hex(self.v)
    def __add__(self,other:'uint32') -> 'uint32':
        return uint32(self.v + other.v)
    def __sub__(self,other:'uint32') -> 'uint32':
        return uint32(self.v - other.v)
    def __or__(self,other:'uint32') -> 'uint32':
        return uint32(self.v | other.v)
    def __and__(self,other:'uint32') -> 'uint32':
        return uint32(self.v & other.v)
    def __xor__(self,other:'uint32') -> 'uint32':
        return uint32(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'uint32':
        if other < 0 or other >= 32:
            fail("uint32 cannot be shifted by < 0 or >= 32")
        return uint32(self.v << other)
    def __rshift__(self,other:int) -> 'uint32':
        if other < 0 or other >= 32:
            fail("uint32 cannot be shifted by < 0 or >= 32")
        return uint32((self.v & 0xffffffff) >> other)
    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return self.v == other.v
    def __invert__(self) -> 'uint32':
        return uint32(~self.v & 0xffffffff)

    @staticmethod
    def rotate_left(x:'uint32',other:int) -> 'uint32':
        return (x << other | x >> (32 - other))
    @staticmethod
    def rotate_right(x:'uint32',other:int) -> 'uint32':
        return (x >> other | x << (32 - other))
    @staticmethod
    def int_value(x:'uint32') -> int:
        return x.v
    @staticmethod
    def from_bytes_le(n:bytes) -> 'uint32':
        return uint32(int.from_bytes(n,byteorder='little'))
    @staticmethod
    def to_bytes_le(x:'uint32') -> bytes:
        return x.v.to_bytes(4,byteorder='little')
    @staticmethod
    def from_u8array(x:'array[uint8]') -> 'uint32':
        return uint32(int(x[0].v) << 24 | int(x[1].v) << 16 | int(x[2].v) << 8 | int(x[3].v))

class uint64:
    def __init__(self,x:int) -> None:
        if x < 0:
            fail("cannot convert negative integer to uint64")
        else:
            self.v = x & 0xffffffffffffffff
    def __str__(self) -> str:
        return hex(self.v)
    def __repr__(self) -> str:
        return hex(self.v)
    def __add__(self,other:'uint64') -> 'uint64':
        return uint64(self.v + other.v)
    def __sub__(self,other:'uint64') -> 'uint64':
        return uint64(self.v - other.v)
    def __or__(self,other:'uint64') -> 'uint64':
        return uint64(self.v | other.v)
    def __and__(self,other:'uint64') -> 'uint64':
        return uint64(self.v & other.v)
    def __xor__(self,other:'uint64') -> 'uint64':
        return uint64(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'uint64':
        if other < 0 or other >= 64:
            fail("uint64 cannot be shifted by < 0 or >= 64")
        return uint64(self.v << other)
    def __rshift__(self,other:int) -> 'uint64':
        if other < 0 or other >= 64:
            fail("uint64 cannot be shifted by < 0 or >= 64")
        return uint64((self.v & 0xffffffff) >> other)
    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return self.v == other.v
    @staticmethod
    def rotate_left(x:'uint64',other:int) -> 'uint64':
        return (x << other | x >> (64 - other))
    @staticmethod
    def rotate_right(x:'uint64',other:int) -> 'uint64':
        return (x >> other | x << (64 - other))
    @staticmethod
    def int_value(x:'uint64') -> int:
        return x.v
    @staticmethod
    def from_bytes_le(n:bytes) -> 'uint64':
        return uint64(int.from_bytes(n,byteorder='little'))
    @staticmethod
    def to_bytes_le(x:'uint64') -> bytes:
        return x.v.to_bytes(8,byteorder='little')
    @staticmethod
    def to_bytes_be(x:'uint64') -> bytes:
        return x.v.to_bytes(8,byteorder='big')


class uint128:
    def __init__(self,x:int) -> None:
        if x < 0:
            fail("cannot convert negative integer to uint128")
        else:
            self.v = x & 0xffffffffffffffffffffffffffffffff
    def __str__(self) -> str:
        return hex(self.v)
    def __repr__(self) -> str:
        return hex(self.v)
    def __add__(self,other:'uint128') -> 'uint128':
        return uint128(self.v + other.v)
    def __sub__(self,other:'uint128') -> 'uint128':
        return uint128(self.v - other.v)
    def __or__(self,other:'uint128') -> 'uint128':
        return uint128(self.v | other.v)
    def __and__(self,other:'uint128') -> 'uint128':
        return uint128(self.v & other.v)
    def __xor__(self,other:'uint128') -> 'uint128':
        return uint128(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'uint128':
        if other < 0 or other >= 128:
            fail("uint128 cannot be shifted by < 0 or >= 128")
        return uint128(self.v << other)
    def __rshift__(self,other:int) -> 'uint128':
        if other < 0 or other >= 128:
            fail("uint128 cannot be shifted by < 0 or >= 128")
        return uint128((self.v & 0xffffffff) >> other)
    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return self.v == other.v

    @staticmethod
    def rotate_left(x:'uint128',other:int) -> 'uint128':
        return (x << other | x >> (128 - other))
    @staticmethod
    def rotate_right(x:'uint128',other:int) -> 'uint128':
        return (x >> other | x << (128 - other))
    @staticmethod
    def int_value(x:'uint128') -> int:
        return x.v
    @staticmethod
    def from_bytes_le(n:bytes) -> 'uint128':
        return uint128(int.from_bytes(n,byteorder='little'))
    @staticmethod
    def to_bytes_le(x:'uint128') -> bytes:
        return x.v.to_bytes(16,byteorder='little')


T = TypeVar('T')
U = TypeVar('U')

class array(Iterable[T]):
    def __init__(self,x:Sequence[T]) -> None:
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

    def __getitem__(self, key:Union[int, slice]):
        try:
            if isinstance(key, slice):
                return array(self.l[key.start:key.stop])
            return self.l[key]
        except:
            print('Array access error:')
            print('array content:',self.l)
            print('array index:',key)
            fail('array index error')

    def __getslice__(self, i:int, j:int) -> 'array[T]':
        return array(self.l[i:j])

    def __setitem__(self,key:Union[int,slice],v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v;
        else:
            self.l[key] = v

    def append(self, x:T) -> None:
        self.l = self.l[len(self.l):] = [x]
        return None

    def extend(self, x:'array[T]') -> None:
        self.l[len(self.l):] = x.l
        return None

    def split(self,blocksize:int) -> 'array[array[T]]':
        return array([array(self.l[x:x+blocksize]) for x in range(0,len(self.l),blocksize)])

    @staticmethod
    def to_int(x:'array[uint32]') -> int:
        result_int = 0
        for (i, b) in enumerate(x):
            result_int |= int(b.v) << (i*32)
        return result_int

    @staticmethod
    def create(default:T, len:int) -> 'array[T]':
        return array([default] * len)
    @staticmethod
    def create_type(x:Iterable[U], T) -> 'array[T]':
        return array(list([T(el) for el in x]))

    @staticmethod
    def len(a:'array[T]') -> int:
        return len(a.l)

    @staticmethod
    def copy(x:'array[T]') -> 'array[T]':
        return array(x.l[:])

    @staticmethod
    def zip(x:'array[T]',y:'array[U]') -> 'array[Tuple[T,U]]':
        return array(list(zip(x.l,y.l)))

    @staticmethod
    def enumerate(x:'array[T]') -> 'array[Tuple[int,T]]':
        return array(list(enumerate(x.l)))

    @staticmethod
    def split_blocks(a:'array[T]',blocksize:int) -> 'array[array[T]]':
        return array([a[x:x+blocksize] for x in range(0,len(a),blocksize)])

    @staticmethod
    def concat_blocks(blocks:'array[array[T]]') -> 'array[T]':
        return (array([b for block in blocks for b in block]))

    @staticmethod
    def split_bytes(a:bytes,blocksize:int) -> 'array[bytes]':
        return array([a[x:x+blocksize] for x in range(0,len(a),blocksize)])

    @staticmethod
    def concat_bytes(blocks:'array[bytes]') -> bytes:
        concat = [b for block in blocks for b in block]
        return bytes(array(concat))

    @staticmethod
    def uint32s_from_bytes_le(b:bytes) -> 'array[uint32]':
        blocks = array.split_bytes(b,4)
        ints = [uint32.from_bytes_le(b) for b in blocks]
        return array(ints)

    @staticmethod
    def uint32s_to_bytes_le(ints:'array[uint32]') -> bytes:
        blocks = array([uint32.to_bytes_le(i) for i in ints])
        return array.concat_bytes(blocks)

def precondition(*types):
    def precondition_decorator(func):
        assert(len(types) == func.__code__.co_argcount)
        def wrapper(*args, **kwds):
            for (a, t) in zip(args, types):
                if not isinstance(t, str):
                    # Check type.
                    assert isinstance(a, t), "arg %r does not match %s" % (a,t)
                else:
                    # Parse string as condition on variable
                    r = eval(str(a) + t)
                    if not r:
                        print("Precondition " + str(a) + t + " did not hold.")
                        assert False, "Precondition %r %s did not hold." % (a, t)
            return func(*args, **kwds)
        wrapper.func_name = func.__name__
        return wrapper
    return precondition_decorator




