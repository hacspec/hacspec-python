from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union

nat = int

class uint32:
    def __init__(self,x:int) -> None:
        if x < 0:
            raise Exception("cannot convert negative integer to uint32")
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
            raise Exception("uint32 cannot be shifted by < 0 or >= 32")
        return uint32(self.v << other)
    def __rshift__(self,other:int) -> 'uint32':
        if other < 0 or other >= 32:
            raise Exception("uint32 cannot be shifted by < 0 or >= 32")
        return uint32((self.v & 0xffffffff) >> other)
    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return self.v == other.v
    
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
    
class uint64:
    def __init__(self,x:int) -> None:
        if x < 0:
            raise Exception("cannot convert negative integer to uint64")
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
            raise Exception("uint64 cannot be shifted by < 0 or >= 64")
        return uint64(self.v << other)
    def __rshift__(self,other:int) -> 'uint64':
        if other < 0 or other >= 64:
            raise Exception("uint64 cannot be shifted by < 0 or >= 64")
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


class uint128:
    def __init__(self,x:int) -> None:
        if x < 0:
            raise Exception("cannot convert negative integer to uint128")
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
            raise Exception("uint128 cannot be shifted by < 0 or >= 128")
        return uint128(self.v << other)
    def __rshift__(self,other:int) -> 'uint128':
        if other < 0 or other >= 128:
            raise Exception("uint128 cannot be shifted by < 0 or >= 128")
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

class array(Iterable[T]):
    def __init__(self,x:List[T]) -> None:
        self.l = x

    def __len__(self) -> int:
        return len(self.l)

    def __iter__(self) -> Iterator[T]:
        return iter(self.l)

    def __getitem__(self, key:Union[int, slice]):
        if isinstance(key, slice):
            return array(self.l[key.start:key.stop])
        return self.l[key]

    def __getslice__(self, i:int, j:int) -> 'array[T]':
        return array(self.l[i:j])

    def __setitem__(self,key,v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v;
        else:
            self.l[key] = v
            
    @staticmethod
    def create(default:T, len:int) -> 'array[T]':
        return array([default] * len)

    @staticmethod
    def len(a:'array[T]') -> int:
        return len(a.l)

    @staticmethod
    def copy(x:'array[T]') -> 'array[T]':
        return array(x.l[:])

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
