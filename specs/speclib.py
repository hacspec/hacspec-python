from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple, Callable, Type, GenericMeta
from random import SystemRandom as rand
import builtins

class Error(Exception): pass
def fail(s):
    raise Error(s)

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
W = TypeVar('W')
X = TypeVar('X')

def tuple2(T,U):
    return Tuple[T,U]

def tuple3(T,U,V):
    return Tuple[T,U,V]

def tuple4(T,U,V,W):
    return Tuple[T,U,V,W]

def tuple5(T,U,V,W,X):
    return Tuple[T,U,V,W,X]

def refine(T:Type[T],f:Callable[[T],bool]):
    return T

nat = refine(int,lambda x : x >= 0)

def range_t(min,max):
    return refine(int,lambda x : x >= min and x < max)

class _uintn:
    def __init__(self,x:int,bits:int) -> None:
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

    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return (self.bits == other.bits and self.v == other.v)

    @staticmethod
    def num_bits(x:'_uintn') -> int:
        return x.bits

    def __int__(self) -> int :
        return self.v

    @staticmethod
    def to_int(x:'_uintn') -> int:
        return x.v
    
class _bit(_uintn):
    def __init__(self,v:Union[int,_uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,1)
        else:
            super().__init__(_uintn.to_int(v),1)
    def __add__(self,other:'_bit') -> '_bit':
        return _bit(self.v + other.v)
    def __sub__(self,other:'_bit') -> '_bit':
        return _bit(self.v - other.v)
    def __mul__(self,other:'_bit') -> '_bit':
        return _bit(self.v * other.v)
    def __inv__(self) -> '_bit':
        return _bit(~ self.v)
    def __or__(self,other:'_bit') -> '_bit':
        return _bit(self.v | other.v)
    def __and__(self,other:'_bit') -> '_bit':
        return _bit(self.v & other.v)
    def __xor__(self,other:'_bit') -> '_bit':
        return _bit(self.v ^ other.v)
    def __lshift__(self,other:int) -> '_bit':
        return _bit(self.v << other)
    def __rshift__(self,other:int) -> '_bit':
        return _bit(self.v >> other)
    @staticmethod
    def rotate_left(x:'_bit',other:int) -> '_bit':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'_bit',other:int) -> '_bit':
        return (x >> other | x << (x.bits - other))

class _uint8(_uintn):
    def __init__(self,v:Union[int,_uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,8)
        else:
            super().__init__(_uintn.to_int(v),8)
    def __add__(self,other:'_uint8') -> '_uint8':
        return _uint8(self.v + other.v)
    def __sub__(self,other:'_uint8') -> '_uint8':
        return _uint8(self.v - other.v)
    def __mul__(self,other:'_uint8') -> '_uint8':
        return _uint8(self.v * other.v)
    def __inv__(self) -> '_uint8':
        return _uint8(~ self.v)
    def __or__(self,other:'_uint8') -> '_uint8':
        return _uint8(self.v | other.v)
    def __and__(self,other:'_uint8') -> '_uint8':
        return _uint8(self.v & other.v)
    def __xor__(self,other:'_uint8') -> '_uint8':
        return _uint8(self.v ^ other.v)
    def __lshift__(self,other:int) -> '_uint8':
        return _uint8(self.v << other)
    def __rshift__(self,other:int) -> '_uint8':
        return _uint8(self.v >> other)
    @staticmethod
    def rotate_left(x:'_uint8',other:int) -> '_uint8':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'_uint8',other:int) -> '_uint8':
        return (x >> other | x << (x.bits - other))

class _uint16(_uintn):
    def __init__(self,v:Union[int,_uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,16)
        else:
            super().__init__(_uintn.to_int(v),16)
    def __add__(self,other:'_uint16') -> '_uint16':
        return _uint16(self.v + other.v)
    def __sub__(self,other:'_uint16') -> '_uint16':
        return _uint16(self.v - other.v)
    def __mul__(self,other:'_uint16') -> '_uint16':
        return _uint16(self.v * other.v)
    def __inv__(self) -> '_uint16':
        return _uint16(~ self.v)
    def __or__(self,other:'_uint16') -> '_uint16':
        return _uint16(self.v | other.v)
    def __and__(self,other:'_uint16') -> '_uint16':
        return _uint16(self.v & other.v)
    def __xor__(self,other:'_uint16') -> '_uint16':
        return _uint16(self.v ^ other.v)
    def __lshift__(self,other:int) -> '_uint16':
        return _uint16(self.v << other)
    def __rshift__(self,other:int) -> '_uint16':
        return _uint16(self.v >> other)
    @staticmethod
    def rotate_left(x:'_uint16',other:int) -> '_uint16':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'_uint16',other:int) -> '_uint16':
        return (x >> other | x << (x.bits - other))


class _uint32(_uintn):
    def __init__(self,v:Union[int,_uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,32)
        else:
            super().__init__(_uintn.to_int(v),32)
    def __add__(self,other:'_uint32') -> '_uint32':
        return _uint32(self.v + other.v)
    def __sub__(self,other:'_uint32') -> '_uint32':
        return _uint32(self.v - other.v)
    def __mul__(self,other:'_uint32') -> '_uint32':
        return _uint32(self.v * other.v)
    def __inv__(self) -> '_uint32':
        return _uint32(~ self.v)
    def __invert__(self) -> '_uint32':
        return _uint32(~ self.v & self.max)
    def __or__(self,other:'_uint32') -> '_uint32':
        return _uint32(self.v | other.v)
    def __and__(self,other:'_uint32') -> '_uint32':
        return _uint32(self.v & other.v)
    def __xor__(self,other:'_uint32') -> '_uint32':
        return _uint32(self.v ^ other.v)
    def __lshift__(self,other:int) -> '_uint32':
        return _uint32(self.v << other)
    def __rshift__(self,other:int) -> '_uint32':
        return _uint32(self.v >> other)
    @staticmethod
    def rotate_left(x:'_uint32',other:int) -> '_uint32':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'_uint32',other:int) -> '_uint32':
        return (x >> other | x << (x.bits - other))



class _uint64(_uintn):
    def __init__(self,v:Union[int,_uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,64)
        else:
            super().__init__(_uintn.to_int(v),64)
    def __add__(self,other:'_uint64') -> '_uint64':
        return _uint64(self.v + other.v)
    def __sub__(self,other:'_uint64') -> '_uint64':
        return _uint64(self.v - other.v)
    def __mul__(self,other:'_uint64') -> '_uint64':
        return _uint64(self.v * other.v)
    def __inv__(self) -> '_uint64':
        return _uint64(~ self.v)
    def __invert__(self) -> '_uint64':
        return _uint64(~ self.v & self.max)
    def __or__(self,other:'_uint64') -> '_uint64':
        return _uint64(self.v | other.v)
    def __and__(self,other:'_uint64') -> '_uint64':
        return _uint64(self.v & other.v)
    def __xor__(self,other:'_uint64') -> '_uint64':
        return _uint64(self.v ^ other.v)
    def __lshift__(self,other:int) -> '_uint64':
        return _uint64(self.v << other)
    def __rshift__(self,other:int) -> '_uint64':
        return _uint64(self.v >> other)
    @staticmethod
    def rotate_left(x:'_uint64',other:int) -> '_uint64':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'_uint64',other:int) -> '_uint64':
        return (x >> other | x << (x.bits - other))


class _uint128(_uintn):
    def __init__(self,v:Union[int,_uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,128)
        else:
            super().__init__(_uintn.to_int(v),128)
    def __add__(self,other:'_uint128') -> '_uint128':
        return _uint128(self.v + other.v)
    def __sub__(self,other:'_uint128') -> '_uint128':
        return _uint128(self.v - other.v)
    def __mul__(self,other:'_uint128') -> '_uint128':
        return _uint128(self.v * other.v)
    def __inv__(self) -> '_uint128':
        return _uint128(~ self.v)
    def __or__(self,other:'_uint128') -> '_uint128':
        return _uint128(self.v | other.v)
    def __and__(self,other:'_uint128') -> '_uint128':
        return _uint128(self.v & other.v)
    def __xor__(self,other:'_uint128') -> '_uint128':
        return _uint128(self.v ^ other.v)
    def __lshift__(self,other:int) -> '_uint128':
        return _uint128(self.v << other)
    def __rshift__(self,other:int) -> '_uint128':
        return _uint128(self.v >> other)
    @staticmethod
    def rotate_left(x:'_uint128',other:int) -> '_uint128':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'_uint128',other:int) -> '_uint128':
        return (x >> other | x << (x.bits - other))


bit_t = _bit
bit = _bit
uint8_t = _uint8
uint8 = _uint8
uint16_t = _uint16
uint16 = _uint16
uint32_t = _uint32
uint32 = _uint32
uint64_t = _uint64
uint64 = _uint64
uint128_t = _uint128
uint128 = _uint128

class _bitvector(_uintn):
    def __init__(self,v:Union[int,_uintn],bits:int) -> None:
        if isinstance(v,int):
            super().__init__(v,bits)
        else:
            super().__init__(_uintn.to_int(v),bits)
    def __add__(self,other:'_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
           return _bitvector(self.v + other.v,self.bits)
        else:
           fail("cannot add _bitvector of different lengths")
           return _bitvector(0,self.bits)
    def __sub__(self,other:'_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
           return _bitvector(self.v - other.v,self.bits)
        else:
           fail("cannot sub _bitvector of different lengths")
           return _bitvector(0,self.bits)
    def __inv__(self) -> '_bitvector':
        return _bitvector(~self.v,self.bits)
    def __or__(self,other:'_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
           return _bitvector(self.v | other.v,self.bits)
        else:
           fail("cannot or _bitvector of different lengths")
           return _bitvector(0,self.bits)
    def __and__(self,other:'_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
           return _bitvector(self.v & other.v,self.bits)
        else:
           fail("cannot and _bitvector of different lengths")
           return _bitvector(0,self.bits)
    def __xor__(self,other:'_bitvector') -> '_bitvector':
        if (other.bits == self.bits):
           return _bitvector(self.v ^ other.v,self.bits)
        else:
           fail("cannot xor _bitvector of different lengths")
           return _bitvector(0,self.bits)
    def __lshift__(self,other:int) -> '_bitvector':
        if other < 0 or other >= self.bits:
           fail("_bitvector cannot be shifted by < 0 or >= bits")
           return _bitvector(0,self.bits,)
        else:
           return _bitvector(self.v << other,self.bits)
    def __rshift__(self,other:int) -> '_bitvector':
        if other < 0 or other >= self.bits:
           fail("_bitvector cannot be shifted by < 0 or >= bits")
           return _bitvector(0,self.bits)
        else:
           return _bitvector(self.v >> other,self.bits)
    @staticmethod
    def rotate_left(x:'_bitvector',other:int) -> '_bitvector':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'_bitvector',other:int) -> '_bitvector':
        return (x >> other | x << (x.bits - other))

    def __getitem__(self, key:Union[int, slice]):
        try:
            if isinstance(key, slice):
                return _bitvector(self.v >> key.start,
                                 key.stop - key.start)
            else:
                return bit(self.v >> key)
        except:
            print('_bitvector content:',self.v)
            print('_bitvector index:',key)
            fail('_bitvector access error')

    def __getslice__(self, i:int, j:int) -> '_bitvector':
        return _bitvector(self.v >> i, j - i)


def bitvector_t(len:nat):
    return _bitvector
bitvector = _bitvector

class _vlarray(Iterable[T]):
    def __init__(self,x:Sequence[T],t:Type=T) -> None:
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

    def __getitem__(self, key:Union[int, slice]):
        try:
            if isinstance(key, slice):
                return _vlarray(self.l[key.start:key.stop])
            return self.l[key]
        except:
            print('_Vlarray access error:')
            print('_vlarray content:',self.l)
            print('_vlarray index:',key)
            fail('_vlarray index error')

    def __getslice__(self, i:int, j:int) -> '_vlarray[T]':
        return _vlarray(self.l[i:j])

    def __setitem__(self,key:Union[int,slice],v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v;
        else:
            self.l[key] = v

    @staticmethod
    def create(len:int,default) -> '_vlarray[T]':
        return _vlarray([default] * len)
    @staticmethod
    def create_type(x:Iterable[U], t: Type) -> '_vlarray[t]':
        return _vlarray(list([t(el) for el in x]), t)

    @staticmethod
    def len(a:'_vlarray[T]') -> int:
        return len(a.l)
    @staticmethod
    def length(a:'_vlarray[T]') -> int:
        return len(a.l)
    @staticmethod
    def copy(x:'_vlarray[T]') -> '_vlarray[T]':
        return _vlarray(x.l[:])

    @staticmethod
    def concat(x:'_vlarray[T]',y:'_vlarray[U]') -> '_vlarray[T]':
        if str(x.t) == "speclib.vlbytes" or str(x.t) == "speclib.vlarray":
            tmp = x.l[:]
            tmp.append(vlarray(y.l[:], type(y)))
            return _vlarray(tmp, x.t)
        return _vlarray(x.l[:]+y.l[:])

    @staticmethod
    def zip(x:'_vlarray[T]',y:'_vlarray[U]') -> '_vlarray[Tuple[T,U]]':
        return _vlarray(list(zip(x.l,y.l)))

    @staticmethod
    def enumerate(x:'_vlarray[T]') -> '_vlarray[Tuple[int,T]]':
        return _vlarray(list(enumerate(x.l)))

    @staticmethod
    def split_blocks(a:'_vlarray[T]',blocksize:int) -> 'Typle[_vlarray[_vlarray[T]],_vlarray[T]]':
        nblocks = len(a) // blocksize
        blocks = _vlarray([a[x*blocksize:(x+1)*blocksize] for x in range(nblocks)])
        last = _vlarray(a[len(a) - (len(a) % blocksize):len(a)])
        return (blocks,last)

    @staticmethod
    def concat_blocks(blocks:'_vlarray[_vlarray[T]]',last:'_vlarray[T]') -> '_vlarray[T]':
        return (_vlarray.concat(_vlarray([b for block in blocks for b in block]),last))

    @staticmethod
    def map(f:Callable[[T],U],a:'_vlarray[T]') -> '_vlarray[U]':
        return _vlarray(list(map(f,a.l)))

    @staticmethod
    def reduce(f:Callable[[T,U],U],a:'_vlarray[T]',init:U) -> U:
        acc = init
        for i in range(len(a)):
            acc = f(a[i],acc)
        return acc

    @staticmethod
    def create_random(len:nat, t:_uintn) -> '_vlarray[t]':
        r = rand()
        x = t(0)
        return array(list([t(r.randint(0, x.max)) for _ in range(0, len)]))


def vlarray_t(T):
    return _vlarray[T]
vlarray = _vlarray

def array_t(T,len):
    return _vlarray[T]
array = _vlarray

class _vlbytes(vlarray[uint8]):
    def __init__(self,x:Sequence[T]) -> None:
        super(_vlbytes, self).__init__(x, uint8_t)
    @staticmethod
    def from_ints(x:List[int]) -> '_vlbytes':
        return vlarray([uint8(i) for i in x])
    
    @staticmethod
    def concat_bytes(blocks:'vlarray[_vlbytes]') -> '_vlbytes':
        concat = [b for block in blocks for b in block]
        return vlarray(concat)

    @staticmethod
    def from_hex(x:str) -> vlarray[uint8]:
        return vlarray([uint8(int(x[i:i+2],16)) for i in range(0,len(x),2)])

    @staticmethod
    def to_hex(a:vlarray[uint8]) -> str:
        return "".join(['{:02x}'.format(uint8.to_int(x)) for x in a])

    @staticmethod
    def from_nat_le(x:nat) -> '_vlbytes':
        b = x.to_bytes((x.bit_length() + 7) // 8, 'little') or b'\0'
        return vlarray([uint8(i) for i in b])

    @staticmethod
    def to_nat_le(x:vlarray[uint8]) -> nat:
        b = builtins.bytes([uint8.to_int(u) for u in x])
        return int.from_bytes(b,'little')

    @staticmethod
    def from_nat_be(x:nat,l:nat=0) -> '_vlbytes':
        b = x.to_bytes((x.bit_length() + 7) // 8, 'big') or b'\0'
        pad = vlarray([uint8(0) for i in range(0,max(0,l-len(b)))])
        result = vlarray([uint8(i) for i in b])
        return array.concat(pad, result)

    @staticmethod
    def to_nat_be(x:vlarray[uint8]) -> nat:
        b = builtins.bytes([uint8.to_int(u) for u in x])
        return int.from_bytes(b,'big')
    
    @staticmethod
    def from_uint32_le(x:uint32) -> vlarray[uint8]:
        xv = uint32.to_int(x)
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
        return vlarray([x0,x1,x2,x3])

    @staticmethod
    def to_uint32_le(x:vlarray[uint8]) -> uint32:
        x0 = uint8.to_int(x[0])
        x1 = uint8.to_int(x[1]) << 8
        x2 = uint8.to_int(x[2]) << 16
        x3 = uint8.to_int(x[3]) << 24
        return uint32(x0 + x1 + x2 + x3)

    @staticmethod
    def from_uint64_le(x:uint64) -> vlarray[uint8]:
        xv = uint64.to_int(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a:vlarray[uint8] = vlarray.create(8,uint8(0))
        a[0:4] = vlbytes.from_uint32_le(x0)
        a[4:8] = vlbytes.from_uint32_le(x1)
        return a

    @staticmethod
    def to_uint64_le(x:vlarray[uint8]) -> uint64:
        x0 = vlbytes.to_uint32_le(x[0:4])
        x1 = vlbytes.to_uint32_le(x[4:8])
        return uint64(uint32.to_int(x0) +
                      (uint32.to_int(x1) << 32))

    @staticmethod
    def from_uint128_le(x:uint128) -> vlarray[uint8]:
        xv = uint128.to_int(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = vlarray.create(16,uint8(0))
        a[0:8] = vlbytes.from_uint64_le(x0)
        a[8:16] = vlbytes.from_uint64_le(x1)
        return a

    @staticmethod
    def to_uint128_le(x:vlarray[uint8]) -> uint128:
        x0 = vlbytes.to_uint64_le(x[0:8])
        x1 = vlbytes.to_uint64_le(x[8:16])
        return uint128(uint64.to_int(x0) +
                      (uint64.to_int(x1) << 64))
    @staticmethod
    def from_uint32_be(x:uint32) -> vlarray[uint8]:
        xv = uint32.to_int(x)
        x0 = uint8((xv >> 24) & 255)
        x1 = uint8((xv >> 16) & 255)
        x2 = uint8((xv >> 8) & 255)
        x3 = uint8(xv & 255)
        return vlarray([x3,x2,x1,x0])

    @staticmethod
    def to_uint32_be(x:vlarray[uint8]) -> uint32:
        x0 = uint8.to_int(x[0]) << 24
        x1 = uint8.to_int(x[1]) << 16
        x2 = uint8.to_int(x[2]) << 8
        x3 = uint8.to_int(x[3])
        return uint32(x3 + x2 + x1 + x0)

    @staticmethod
    def from_uint64_be(x:uint64) -> vlarray[uint8]:
        xv = uint64.to_int(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a:vlarray[uint8] = vlarray.create(8,uint8(0))
        a[0:4] = vlbytes.from_uint32_be(x1)
        a[4:8] = vlbytes.from_uint32_be(x0)
        return a

    @staticmethod
    def to_uint64_be(x:vlarray[uint8]) -> uint64:
        x0 = vlbytes.to_uint32_be(x[0:4])
        x1 = vlbytes.to_uint32_be(x[4:8])
        return uint64(uint32.to_int(x1) +
                      (uint32.to_int(x0) << 32))

    @staticmethod
    def from_uint128_be(x:uint128) -> vlarray[uint8]:
        xv = uint128.to_int(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = vlarray.create(16,uint8(0))
        a[0:8] = vlbytes.from_uint64_be(x1)
        a[8:16] = vlbytes.from_uint64_be(x0)
        return a

    @staticmethod
    def to_uint128_be(x:vlarray[uint8]) -> uint128:
        x0 = vlbytes.to_uint64_be(x[0:8])
        x1 = vlbytes.to_uint64_be(x[8:16])
        return uint128(uint64.to_int(x1) +
                      (uint64.to_int(x0) << 64))

    @staticmethod
    def from_uint32s_le(x:vlarray[uint32]) -> vlarray[uint8]:
        by = vlarray([vlbytes.from_uint32_le(i) for i in x])
        return(vlarray.concat_blocks(by,vlarray([])))
    @staticmethod
    def to_uint32s_le(x:vlarray[uint8]) -> vlarray[uint32]:
        nums,x = vlarray.split_blocks(x,4)
        if len(x) > 0:
            fail("array length not a multiple of 4")
        else:
            return(vlarray([vlbytes.to_uint32_le(i) for i in nums]))

    @staticmethod
    def from_uint32s_be(x:vlarray[uint32]) -> vlarray[uint8]:
        by = vlarray([vlbytes.from_uint32_be(i) for i in x])
        return(vlarray.concat_blocks(by,vlarray([])))
    @staticmethod
    def to_uint32s_be(x:vlarray[uint8]) -> vlarray[uint32]:
        nums,x = vlarray.split_blocks(x,4)
        if len(x) > 0:
            fail("array length not a multiple of 4")
        else:
            return(vlarray([vlbytes.to_uint32_be(i) for i in nums]))

    @staticmethod
    def from_uint64s_be(x:vlarray[uint64]) -> vlarray[uint8]:
        by = vlarray([vlbytes.from_uint64_be(i) for i in x])
        return(vlarray.concat_blocks(by,vlarray([])))
    @staticmethod
    def to_uint64s_be(x:vlarray[uint8]) -> vlarray[uint64]:
        nums,x = vlarray.split_blocks(x,8)
        if len(x) > 0:
            fail("array length not a multple of 8")
        else:
            return(vlarray([vlbytes.to_uint64_be(i) for i in nums]))

    @staticmethod
    def create_random_bytes(len:nat) -> '_vlarray[uint8]':
        r = rand()
        return array(list([uint8(r.randint(0, 0xFF)) for _ in range(0, len)]))


def vlbytes_t(T):
    return _vlbytes
def bytes_t(len):
    return _vlbytes
vlbytes = _vlbytes
bytes = vlbytes


# The libraries below are experimental and need more thought

class pfelem:
    def __init__(self,x:int,p:int) -> None:
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
    def __add__(self,other:'pfelem') -> 'pfelem':
        if (other.p == self.p):
           return pfelem(self.v + other.v,self.p)
        else:
           fail("cannot add pfelem of different fields")
           return pfelem(0,self.p)
    def __sub__(self,other:'pfelem') -> 'pfelem':
        if (other.p == self.p):
           return pfelem(self.v - other.v,self.p)
        else:
           fail("cannot sub pfelem of different fields")
           return pfelem(0,self.p)
    def __mul__(self,other:'pfelem') -> 'pfelem':
        if (other.p == self.p):
           return pfelem(self.v * other.v,self.p)
        else:
           fail("cannot sub pfelem of different fields")
           return pfelem(0,self.p)
    def __pow__(self,other:int) -> 'pfelem':
        if (other >= 0):
           return pfelem(pow(self.v,other,self.p),self.p)
        else:
           fail("cannot exp with negative number")
           return pfelem(0,self.p)


    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return (self.p == other.p and self.v == other.v)

    @staticmethod
    def pfadd(x:'pfelem',y:'pfelem') -> 'pfelem':
        return (x+y)


    @staticmethod
    def pfmul(x:'pfelem',y:'pfelem') -> 'pfelem':
        return (x*y)

    @staticmethod
    def pfsub(x:'pfelem',y:'pfelem') -> 'pfelem':
        return (x-y)


    @staticmethod
    def pfinv(x:'pfelem') -> 'pfelem':
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

        return pfelem(modinv(x.v,x.p),x.p)

    @staticmethod
    def prime(x:'pfelem') -> int:
        return x.p

    def __int__(self) -> int :
        return self.v

    @staticmethod
    def to_int(x:'pfelem') -> int:
        return x.v

pfelem_t = pfelem
def prime_field(prime:nat):
    return pfelem_t, (lambda x: pfelem(x,prime)), pfelem.to_int

class gfelem:
    def __init__(self,x:bitvector,irred:bitvector) -> None:
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
    def __add__(self,other:'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred):
           return gfelem(self.v ^ other.v,self.irred)
        else:
           fail("cannot add gfelem of different fields")
           return gfelem(bitvector(0,self.bits),self.irred)
    def __sub__(self,other:'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred):
           return gfelem(self.v ^ other.v,self.irred)
        else:
           fail("cannot sub gfelem of different fields")
           return gfelem(bitvector(0,self.bits),self.irred)

    def __mul__(self,other:'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred):
           bits = self.bits
           irred = self.irred
           a = self.v
           b = other.v
           p = bitvector(0,bits)
           for i in range(bits):
               if (bitvector.to_int(b) & 1 == 1):
                   p = p ^ a
               b = b >> 1
               c = a >> (bits - 1)
               a = a << 1
               if (bitvector.to_int(a) == 1):
                  a = a ^ irred
           return gfelem(p,irred)
        else:
           fail("cannot mul gfelem of different fields")
           return gfelem(bitvector(0,self.bits),self.irred)

    def __pow__(self,other:int) -> 'gfelem':
        if (other < 0):
           fail("cannot exp with negative number")
           return gfelem(bitvector(0,self.bits),self.irred)
        else:
           def exp(a,x):
               if (x == 0):
                  return gfelem(bitvector(1,self.bits),self.irred)
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
           return exp(self,other)

    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return (self.bits == other.bits and self.v == other.v)

    @staticmethod
    def gfadd(x:'gfelem',y:'gfelem') -> 'gfelem':
        return (x + y)

    @staticmethod
    def gfsub(x:'gfelem',y:'gfelem') -> 'gfelem':
        return (x - y)

    @staticmethod
    def gfmul(x:'gfelem',y:'gfelem') -> 'gfelem':
        return (x * y)

    @staticmethod
    def gfexp(x:'gfelem',y:int) -> 'gfelem':
        return (x ** y)

    @staticmethod
    def gfinv(x:'gfelem') -> 'gfelem':
        bits = x.bits
        irred = x.irred
        def degree(v:bitvector,bits:int):
            if (v == 0 or bits == 0):
                return 0
            elif (bitvector.to_int(v >> (bits - 1)) == 1):
                return (bits - 1)
            else:
                return degree(v >> 1, bits - 1)
        def gfgcd(s,r,v,u):
            dr = degree(r,bits)
            ds = degree(s,bits)
            if (dr == 0):
                return u
            elif (ds >= dr):
                s_ = s ^ (r << (ds - dr))
                v_ = v ^ (u << (ds - dr))
                return gfgcd(s_,r,v_,u)
            else:
                r_ = s
                s_ = r
                v_ = u
                u_ = v
                s_ = s_ ^ (r_ << (dr - ds))
                v_ = v_ ^ (u_ << (dr - ds))
                return gfgcd(s_,r_,v_,u_)
        r = x.v
        s = irred
        dr = degree(r,bits)
        ds = degree(s,bits)
        v = gfelem(bitvector(0,bits),irred)
        u = gfelem(bitvector(1,bits),irred)
        if (dr == 0):
            return u
        else:
            s_ =  s ^ (r << (ds - dr))
            v_ =  v ^ (r << (ds - dr))
            return gfelem(gfgcd(s_,r,v_,u),irred)

    def __int__(self) -> int :
        return bitvector.to_int(self.v)

    @staticmethod
    def to_int(x:'gfelem') -> int:
        return bitvector.to_int(x.v)

    @staticmethod
    def uint32s_to_uint8s_be(ints:'array[uint32]') -> 'array[uint8]':
        blocks = [uint32.to_bytes_le(i) for i in ints]
        return array([uint8(b) for block in blocks for b in reversed(block)])

    @staticmethod
    def uint32s_to_uint8s_le(ints:'array[uint32]') -> 'array[uint8]':
        blocks = [uint32.to_bytes_le(i) for i in ints]
        return array([uint8(b) for block in blocks for b in block])

