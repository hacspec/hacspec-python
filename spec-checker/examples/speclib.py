
nat = int

class uint32:
    def __init__(self,x:int) -> None:
        if x < 0:
            raise Exception("cannot convert negative integer to uint32")
        else:
            self.v = x & 0xffffffff
    def __str__(self) -> str:
        return str(self.v)
    def __repr__(self) -> str:
        return str(self.v)
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
    def rotate_left(self,other:int) -> 'uint32':
        return (self << other | self >> (32 - other))
    def rotate_right(self,other:int) -> 'uint32':
        return (self >> other | self << (32 - other))
    def to_int(self) -> int:
        return self.v
    @staticmethod
    def from_bytes_le(n:bytes) -> 'uint32':
        return uint32(int.from_bytes(n,byteorder='little'))
    def to_bytes_le(self) -> bytes:
        return self.v.to_bytes(4,byteorder='little')


class uint64:
    def __init__(self,x:int) -> None:
        if x < 0:
            raise Exception("cannot convert negative integer to uint64")
        else:
            self.v = x & 0xffffffffffffffff
    def __str__(self) -> str:
        return str(self.v)
    def __repr__(self) -> str:
        return str(self.v)
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
    def rotate_left(self,other:int) -> 'uint64':
        return (self << other | self >> (64 - other))
    def rotate_right(self,other:int) -> 'uint64':
        return (self >> other | self << (64 - other))
    def to_int(self) -> int:
        return self.v
    @staticmethod
    def from_bytes_le(n:bytes) -> 'uint64':
        return uint64(int.from_bytes(n,byteorder='little'))
    def to_bytes_le(self) -> bytes:
        return self.v.to_bytes(8,byteorder='little')


class uint128:
    def __init__(self,x:int) -> None:
        if x < 0:
            raise Exception("cannot convert negative integer to uint128")
        else:
            self.v = x & 0xffffffffffffffffffffffffffffffff
    def __str__(self) -> str:
        return str(self.v)
    def __repr__(self) -> str:
        return str(self.v)
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
    def rotate_left(self,other:int) -> 'uint128':
        return (self << other | self >> (128 - other))
    def rotate_right(self,other:int) -> 'uint128':
        return (self >> other | self << (128 - other))
    def to_int(self) -> int:
        return self.v
    @staticmethod
    def from_bytes_le(n:bytes) -> 'uint128':
        return uint128(int.from_bytes(n,byteorder='little'))
    def to_bytes_le(self) -> bytes:
        return self.v.to_bytes(16,byteorder='little')


    
