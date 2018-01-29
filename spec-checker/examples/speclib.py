
nat = int

class uint32:
    def __init__(self,x:int) -> None:
        if x < 0:
            raise Exception("cannot convert negative integer to uint32")
        else:
            self.v = x
    def __str__(self) -> str:
        return str(self.v)
    def __repr__(self) -> str:
        return str(self.v)
    def __add__(self,other:'uint32') -> 'uint32':
        return uint32(self.v + other.v)
    def __xor__(self,other:'uint32') -> 'uint32':
        return uint32(self.v ^ other.v)
    def __lshift__(self,other:'uint32') -> 'uint32':
        return uint32(self.v << other.v)
    def __rshift__(self,other:'uint32') -> 'uint32':
        return uint32(self.v >> other.v)
    def to_int(self) -> int:
        return self.v
    @staticmethod
    def from_bytes_le(n:bytes) -> 'uint32':
        return uint32(int.from_bytes(n,byteorder='little'))
    def to_bytes_le(self) -> bytes:
        return self.v.to_bytes(4,byteorder='little')
