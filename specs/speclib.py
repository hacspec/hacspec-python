from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple, Callable, Type

class Error(Exception): pass

def fail(s):
    raise Error(s)

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

def tuple2(T,U):
    return Tuple[T,U]

def tuple3(T,U,V):
    return Tuple[T,U,V]

def refine(T:Type[T],f:Callable[[T],bool]):
    return T

nat = refine(int,lambda x : x >= 0)
def range_t(min,max):
    return refine(int,lambda x : x >= min and x < max)

class uintn:
    def __init__(self,x:int,bits:int) -> None:
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

    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return (self.bits == other.bits and self.v == other.v)

    @staticmethod
    def num_bits(x:'uintn') -> int:
        return x.bits

    def __int__(self) -> int :
        return self.v

    @staticmethod
    def to_int(x:'uintn') -> int:
        return x.v

class bit(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,1)
        else:
            super().__init__(uintn.to_int(v),1)
    def __add__(self,other:'bit') -> 'bit':
        return bit(self.v + other.v)
    def __sub__(self,other:'bit') -> 'bit':
        return bit(self.v - other.v)
    def __mul__(self,other:'bit') -> 'bit':
        return bit(self.v * other.v)
    def __inv__(self) -> 'bit':
        return bit(~ self.v)
    def __or__(self,other:'bit') -> 'bit':
        return bit(self.v | other.v)
    def __and__(self,other:'bit') -> 'bit':
        return bit(self.v & other.v)
    def __xor__(self,other:'bit') -> 'bit':
        return bit(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'bit':
        return bit(self.v << other)
    def __rshift__(self,other:int) -> 'bit':
        return bit(self.v >> other)
    @staticmethod
    def rotate_left(x:'bit',other:int) -> 'bit':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'bit',other:int) -> 'bit':
        return (x >> other | x << (x.bits - other))

class uint8(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,8)
        else:
            super().__init__(uintn.to_int(v),8)
    def __add__(self,other:'uint8') -> 'uint8':
        return uint8(self.v + other.v)
    def __sub__(self,other:'uint8') -> 'uint8':
        return uint8(self.v - other.v)
    def __mul__(self,other:'uint8') -> 'uint8':
        return uint8(self.v * other.v)
    def __inv__(self) -> 'uint8':
        return uint8(~ self.v)
    def __or__(self,other:'uint8') -> 'uint8':
        return uint8(self.v | other.v)
    def __and__(self,other:'uint8') -> 'uint8':
        return uint8(self.v & other.v)
    def __xor__(self,other:'uint8') -> 'uint8':
        return uint8(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'uint8':
        return uint8(self.v << other)
    def __rshift__(self,other:int) -> 'uint8':
        return uint8(self.v >> other)
    @staticmethod
    def rotate_left(x:'uint8',other:int) -> 'uint8':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'uint8',other:int) -> 'uint8':
        return (x >> other | x << (x.bits - other))

class uint16(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,16)
        else:
            super().__init__(uintn.to_int(v),16)
    def __add__(self,other:'uint16') -> 'uint16':
        return uint16(self.v + other.v)
    def __sub__(self,other:'uint16') -> 'uint16':
        return uint16(self.v - other.v)
    def __mul__(self,other:'uint16') -> 'uint16':
        return uint16(self.v * other.v)
    def __inv__(self) -> 'uint16':
        return uint16(~ self.v)
    def __or__(self,other:'uint16') -> 'uint16':
        return uint16(self.v | other.v)
    def __and__(self,other:'uint16') -> 'uint16':
        return uint16(self.v & other.v)
    def __xor__(self,other:'uint16') -> 'uint16':
        return uint16(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'uint16':
        return uint16(self.v << other)
    def __rshift__(self,other:int) -> 'uint16':
        return uint16(self.v >> other)
    @staticmethod
    def rotate_left(x:'uint16',other:int) -> 'uint16':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'uint16',other:int) -> 'uint16':
        return (x >> other | x << (x.bits - other))



class uint32(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,32)
        else:
            super().__init__(uintn.to_int(v),32)
    def __add__(self,other:'uint32') -> 'uint32':
        return uint32(self.v + other.v)
    def __sub__(self,other:'uint32') -> 'uint32':
        return uint32(self.v - other.v)
    def __mul__(self,other:'uint32') -> 'uint32':
        return uint32(self.v * other.v)
    def __inv__(self) -> 'uint32':
        return uint32(~ self.v)
    def __invert__(self) -> 'uint32':
        return uint32(~ self.v & self.max)
    def __or__(self,other:'uint32') -> 'uint32':
        return uint32(self.v | other.v)
    def __and__(self,other:'uint32') -> 'uint32':
        return uint32(self.v & other.v)
    def __xor__(self,other:'uint32') -> 'uint32':
        return uint32(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'uint32':
        return uint32(self.v << other)
    def __rshift__(self,other:int) -> 'uint32':
        return uint32(self.v >> other)
    @staticmethod
    def rotate_left(x:'uint32',other:int) -> 'uint32':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'uint32',other:int) -> 'uint32':
        return (x >> other | x << (x.bits - other))



class uint64(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,64)
        else:
            super().__init__(uintn.to_int(v),64)
    def __add__(self,other:'uint64') -> 'uint64':
        return uint64(self.v + other.v)
    def __sub__(self,other:'uint64') -> 'uint64':
        return uint64(self.v - other.v)
    def __mul__(self,other:'uint64') -> 'uint64':
        return uint64(self.v * other.v)
    def __inv__(self) -> 'uint64':
        return uint64(~ self.v)
    def __invert__(self) -> 'uint64':
        return uint64(~ self.v & self.max)
    def __or__(self,other:'uint64') -> 'uint64':
        return uint64(self.v | other.v)
    def __and__(self,other:'uint64') -> 'uint64':
        return uint64(self.v & other.v)
    def __xor__(self,other:'uint64') -> 'uint64':
        return uint64(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'uint64':
        return uint64(self.v << other)
    def __rshift__(self,other:int) -> 'uint64':
        return uint64(self.v >> other)
    @staticmethod
    def rotate_left(x:'uint64',other:int) -> 'uint64':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'uint64',other:int) -> 'uint64':
        return (x >> other | x << (x.bits - other))


class uint128(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,128)
        else:
            super().__init__(uintn.to_int(v),128)
    def __add__(self,other:'uint128') -> 'uint128':
        return uint128(self.v + other.v)
    def __sub__(self,other:'uint128') -> 'uint128':
        return uint128(self.v - other.v)
    def __mul__(self,other:'uint128') -> 'uint128':
        return uint128(self.v * other.v)
    def __inv__(self) -> 'uint128':
        return uint128(~ self.v)
    def __or__(self,other:'uint128') -> 'uint128':
        return uint128(self.v | other.v)
    def __and__(self,other:'uint128') -> 'uint128':
        return uint128(self.v & other.v)
    def __xor__(self,other:'uint128') -> 'uint128':
        return uint128(self.v ^ other.v)
    def __lshift__(self,other:int) -> 'uint128':
        return uint128(self.v << other)
    def __rshift__(self,other:int) -> 'uint128':
        return uint128(self.v >> other)
    @staticmethod
    def rotate_left(x:'uint128',other:int) -> 'uint128':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'uint128',other:int) -> 'uint128':
        return (x >> other | x << (x.bits - other))


class bitvector(uintn):
    def __init__(self,v:Union[int,uintn],bits:int) -> None:
        if isinstance(v,int):
            super().__init__(v,bits)
        else:
            super().__init__(uintn.to_int(v),bits)
    def __add__(self,other:'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
           return bitvector(self.v + other.v,self.bits)
        else:
           fail("cannot add bitvector of different lengths")
           return bitvector(0,self.bits)
    def __sub__(self,other:'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
           return bitvector(self.v - other.v,self.bits)
        else:
           fail("cannot sub bitvector of different lengths")
           return bitvector(0,self.bits)
    def __inv__(self) -> 'bitvector':
        return bitvector(~self.v,self.bits)
    def __or__(self,other:'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
           return bitvector(self.v | other.v,self.bits)
        else:
           fail("cannot or bitvector of different lengths")
           return bitvector(0,self.bits)
    def __and__(self,other:'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
           return bitvector(self.v & other.v,self.bits)
        else:
           fail("cannot and bitvector of different lengths")
           return bitvector(0,self.bits)
    def __xor__(self,other:'bitvector') -> 'bitvector':
        if (other.bits == self.bits):
           return bitvector(self.v ^ other.v,self.bits)
        else:
           fail("cannot xor bitvector of different lengths")
           return bitvector(0,self.bits)
    def __lshift__(self,other:int) -> 'bitvector':
        if other < 0 or other >= self.bits:
           fail("bitvector cannot be shifted by < 0 or >= bits")
           return bitvector(0,self.bits,)
        else:
           return bitvector(self.v << other,self.bits)
    def __rshift__(self,other:int) -> 'bitvector':
        if other < 0 or other >= self.bits:
           fail("bitvector cannot be shifted by < 0 or >= bits")
           return bitvector(0,self.bits)
        else:
           return bitvector(self.v >> other,self.bits)
    @staticmethod
    def rotate_left(x:'bitvector',other:int) -> 'bitvector':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'bitvector',other:int) -> 'bitvector':
        return (x >> other | x << (x.bits - other))

    def __getitem__(self, key:Union[int, slice]):
        try:
            if isinstance(key, slice):
                return bitvector(self.v >> key.start,
                                 key.stop - key.start)
            return bit(self.v)
        except:
            print('bitvector content:',self.v)
            print('bitvector index:',key)
            fail('bitvector access error')

    def __getslice__(self, i:int, j:int) -> 'bitvector':
        return bitvector(self.v >> i, j - i)

    def __setitem__(self,key:Union[int,slice],v) -> 'bitvector':
        if isinstance(key, slice):
            mask = ((1 << (key.stop - key.start)) - 1) << key.start
            return bitvector((self.v & (not mask)) |
                             (v.v << key.start),self.bits)
        else:
            return bitvector((self.v & (not (1 << key))) | (v << key), self.bits)


uint8_t = uint8
uint16_t = uint16
uint32_t = uint32
uint64_t = uint64
uint128_t = uint128
bitvector_t = bitvector



class vlarray(Iterable[T]):
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
                return vlarray(self.l[key.start:key.stop])
            return self.l[key]
        except:
            print('Vlarray access error:')
            print('vlarray content:',self.l)
            print('vlarray index:',key)
            fail('vlarray index error')

    def __getslice__(self, i:int, j:int) -> 'vlarray[T]':
        return vlarray(self.l[i:j])

    def __setitem__(self,key:Union[int,slice],v) -> None:
        if isinstance(key, slice):
            self.l[key.start:key.stop] = v;
        else:
            self.l[key] = v

    @staticmethod
    def create(len:int,default) -> 'vlarray[T]':
        return vlarray([default] * len)
    @staticmethod
    def create_type(x:Iterable[U], T) -> 'vlarray[T]':
        return vlarray(list([T(el) for el in x]))

    @staticmethod
    def len(a:'vlarray[T]') -> int:
        return len(a.l)
    @staticmethod
    def length(a:'vlarray[T]') -> int:
        return len(a.l)
    @staticmethod
    def copy(x:'vlarray[T]') -> 'vlarray[T]':
        return vlarray(x.l[:])

    @staticmethod
    def concat(x:'vlarray[T]',y:'vlarray[T]') -> 'vlarray[T]':
        return vlarray(x.l[:]+y.l[:])

    @staticmethod
    def zip(x:'vlarray[T]',y:'vlarray[U]') -> 'vlarray[Tuple[T,U]]':
        return vlarray(list(zip(x.l,y.l)))

    @staticmethod
    def enumerate(x:'vlarray[T]') -> 'vlarray[Tuple[int,T]]':
        return vlarray(list(enumerate(x.l)))

    @staticmethod
    def split_blocks(a:'vlarray[T]',blocksize:int) -> 'Typle[vlarray[vlarray[T]],vlarray[T]]':
        nblocks = len(a) // blocksize
        blocks = vlarray([a[x*blocksize:(x+1)*blocksize] for x in range(nblocks)])
        last = vlarray(a[len(a) - (len(a) % blocksize):len(a)])
        return (blocks,last)

    @staticmethod
    def concat_blocks(blocks:'vlarray[vlarray[T]]',last:'vlarray[T]') -> 'vlarray[T]':
        return (vlarray.concat(vlarray([b for block in blocks for b in block]),last))

    @staticmethod
    def map(f:Callable[[T],U],a:'vlarray[T]') -> 'vlarray[U]':
        return vlarray(list(map(f,a.l)))

    @staticmethod
    def reduce(f:Callable[[T,U],U],a:'vlarray[T]',init:U) -> U:
        acc = init
        for i in range(len(a)):
            acc = f(a[i],acc)
        return acc


class vlbytes(vlarray[uint8]):
    @staticmethod
    def from_ints(x:List[int]) -> vlarray[uint8]:
        return vlarray([uint8(i) for i in x])

    @staticmethod
    def concat_bytes(blocks:'vlarray[vlarray[uint8]]') -> 'vlarray[uint8]':
        concat = [b for block in blocks for b in block]
        return vlarray(concat)

    @staticmethod
    def from_hex(x:str) -> vlarray[uint8]:
        return vlarray([uint8(int(x[i:i+2],16)) for i in range(0,len(x),2)])

    @staticmethod
    def to_hex(a:vlarray[uint8]) -> str:
        return "".join(['{:02x}'.format(uint8.to_int(x)) for x in a])

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
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
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

def vlarray_t(T):
    return vlarray[T]
def array_t(T,len):
    return vlarray[T]
def vlbytes_t(T):
    return vlbytes
def bytes_t(len):
    return vlbytes
array = vlarray
bytes = vlbytes

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
