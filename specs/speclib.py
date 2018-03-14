from typing import Any, NewType, List, TypeVar, Generic, Iterator, Iterable, Union, Generator, Sequence, Tuple, Callable, Type

class Error(Exception): pass

def fail(s):
    raise Error(s)

T = TypeVar('T')
U = TypeVar('U')

def refine(T:Type[T],f:Callable[[T],bool]):
    return T
nat = refine(int,lambda x : x >= 0)

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
    def __add__(self,other:'uintn') -> 'uintn':
        if (other.bits == self.bits): 
           return uintn(self.v + other.v,self.bits)
        else:
           fail("cannot add uintn of different lengths")
           return uintn(0,self.bits)
    def __sub__(self,other:'uintn') -> 'uintn':
        if (other.bits == self.bits): 
           return uintn(self.v - other.v,self.bits)
        else:
           fail("cannot sub uintn of different lengths")
           return uintn(0,self.bits)
    def __or__(self,other:'uintn') -> 'uintn':
        if (other.bits == self.bits): 
           return uintn(self.v | other.v,self.bits)
        else:
           fail("cannot or uintn of different lengths")
           return uintn(0,self.bits)
    def __and__(self,other:'uintn') -> 'uintn':
        if (other.bits == self.bits):
           return uintn(self.v & other.v,self.bits)
        else:
           fail("cannot and uintn of different lengths")
           return uintn(0,self.bits)
    def __xor__(self,other:'uintn') -> 'uintn':
        if (other.bits == self.bits):
           return uintn(self.v ^ other.v,self.bits)
        else:
           fail("cannot xor uintn of different lengths")
           return uintn(0,self.bits)
    def __lshift__(self,other:int) -> 'uintn':
        if other < 0 or other >= self.max:
           fail("uintn cannot be shifted by < 0 or >= max")
           return uintn(0,self.bits,)
        else:
           return uintn(self.v << other,self.bits)
    def __rshift__(self,other:int) -> 'uintn':
        if other < 0 or other >= self.max:
           fail("uintn cannot be shifted by < 0 or >= max")
           return uintn(0,self.bits)
        else:
           return uintn(self.v >> other,self.bits)
    # See https://github.com/python/mypy/issues/2783
    def __eq__(self,other:Any) -> Any:
        return (self.bits == other.bits and self.v == other.v)

    @staticmethod
    def num_bits(x:'uintn') -> int:
        return x.bits

    def __int__(self) -> int :
        return self.v
    
    @staticmethod
    def int_value(x:'uintn') -> int:
        return x.v
    @staticmethod
    def rotate_left(x:'uintn',other:int) -> 'uintn':
        return (x << other | x >> (x.bits - other))
    @staticmethod
    def rotate_right(x:'uintn',other:int) -> 'uintn':
        return (x >> other | x << (x.bits - other))

class bit(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,1)
        else:
            super().__init__(uintn.int_value(v),1)

class uint8(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,8)
        else:
            super().__init__(uintn.int_value(v),8)

class uint16(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,16)
        else:
            super().__init__(uintn.int_value(v),16)

class uint32(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,32)
        else:
            super().__init__(uintn.int_value(v),32)
            
class uint64(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,64)
        else:
            super().__init__(uintn.int_value(v),64)
            
class uint128(uintn):
    def __init__(self,v:Union[int,uintn]) -> None:
        if isinstance(v,int):
            super().__init__(v,128)
        else:
            super().__init__(uintn.int_value(v),128)


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
    def int_value(x:'pfelem') -> int:
        return x.v

    
    

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
    def concat(x:'array[T]',y:'array[T]') -> 'array[T]':
        return array(x.l[:]+y.l[:])
    
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
    def map(f:Callable[[T],U],a:'array[T]') -> 'array[U]':
        return array(list(map(f,a.l)))
    
    @staticmethod
    def reduce(f:Callable[[T,U],U],a:'array[T]',init:U) -> U:
        acc = init
        for i in range(len(a)):
            acc = f(a[i],acc)
        return acc
    

class bytes(array[uint8]):
    @staticmethod
    def from_ints(x:List[int]) -> array[uint8]:
        return array([uint8(i) for i in x])

    @staticmethod
    def concat_bytes(blocks:'array[array[uint8]]') -> 'array[uint8]':
        concat = [b for block in blocks for b in block]
        return array(concat)

    @staticmethod
    def from_hex(x:str) -> array[uint8]:
        return array([uint8(int(x[i:i+2],16)) for i in range(0,len(x),2)])
    
    @staticmethod
    def from_uint32_le(x:uint32) -> array[uint8]:
        xv = uint32.int_value(x)
        x0 = uint8(xv & 255)
        x1 = uint8((xv >> 8) & 255)
        x2 = uint8((xv >> 16) & 255)
        x3 = uint8((xv >> 24) & 255)
        return array([x0,x1,x2,x3])

    @staticmethod
    def to_uint32_le(x:array[uint8]) -> uint32:
        x0 = uint8.int_value(x[0])
        x1 = uint8.int_value(x[1]) << 8
        x2 = uint8.int_value(x[2]) << 16
        x3 = uint8.int_value(x[3]) << 24
        return uint32(x0 + x1 + x2 + x3)

    @staticmethod
    def from_uint64_le(x:uint64) -> array[uint8]:
        xv = uint64.int_value(x)
        x0 = uint32(xv & 0xffffffff)
        x1 = uint32((xv >> 32) & 0xffffffff)
        a:array[uint8] = array.create(uint8(0),8)
        a[0:4] = bytes.from_uint32_le(x0)
        a[4:8] = bytes.from_uint32_le(x1)
        return a

    @staticmethod
    def to_uint64_le(x:array[uint8]) -> uint64:
        x0 = bytes.to_uint32_le(x[0:4])
        x1 = bytes.to_uint32_le(x[4:8])
        return uint64(uint32.int_value(x0) +
                      (uint32.int_value(x1) << 32))

    @staticmethod
    def from_uint128_le(x:uint128) -> array[uint8]:
        xv = uint128.int_value(x)
        x0 = uint64(xv & 0xffffffffffffffff)
        x1 = uint64((xv >> 64) & 0xffffffffffffffff)
        a = array.create(uint8(0),16)
        a[0:8] = bytes.from_uint64_le(x0)
        a[8:16] = bytes.from_uint64_le(x1)
        return a

    @staticmethod
    def to_uint128_le(x:array[uint8]) -> uint128:
        x0 = bytes.to_uint64_le(x[0:8])
        x1 = bytes.to_uint64_le(x[8:16])
        return uint128(uint64.int_value(x0) +
                      (uint64.int_value(x1) << 64))

    @staticmethod
    def from_uint32s_le(x:array[uint32]) -> array[uint8]:
        by = array([bytes.from_uint32_le(i) for i in x])
        return(array.concat_blocks(by))
    @staticmethod
    def to_uint32s_le(x:array[uint8]) -> array[uint32]:
        return(array([bytes.to_uint32_le(i) for i in array.split_blocks(x,4)]))


class gfelem:
    def __init__(self,x:uintn,irred:uintn) -> None:
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
           return gfelem(uintn(0,self.bits),self.irred)
    def __sub__(self,other:'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred): 
           return gfelem(self.v ^ other.v,self.irred)
        else:
           fail("cannot sub gfelem of different fields")
           return gfelem(uintn(0,self.bits),self.irred)

    def __mul__(self,other:'gfelem') -> 'gfelem':
        if (other.bits == self.bits and other.irred == self.irred): 
           bits = self.bits
           irred = self.irred
           a = self.v
           b = other.v
           p = uintn(0,bits)
           for i in range(bits):
               if (uintn.int_value(b) & 1 == 1):
                   p = p ^ a
               b = b >> 1
               c = a >> (bits - 1)
               a = a << 1
               if (uintn.int_value(a) == 1):
                  a = a ^ irred
           return gfelem(p,irred)
        else:
           fail("cannot mul gfelem of different fields")
           return gfelem(uintn(0,self.bits),self.irred)
        
    def __pow__(self,other:int) -> 'gfelem':
        if (other < 0):
           fail("cannot exp with negative number")
           return gfelem(uintn(0,self.bits),self.irred)
        else:
           def exp(a,x):
               if (x == 0):
                  return gfelem(uintn(1,self.bits),self.irred)
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
        def degree(v:uintn,bits:int):
            if (v == 0 or bits == 0):
                return 0
            elif (uintn.int_value(v >> (bits - 1)) == 1):
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
        v = gfelem(uintn(0,bits),irred)
        u = gfelem(uintn(1,bits),irred)
        if (dr == 0):
            return u
        else:
            s_ =  s ^ (r << (ds - dr))
            v_ =  v ^ (r << (ds - dr))
            return gfelem(gfgcd(s_,r,v_,u),irred)

    def __int__(self) -> int :
        return uintn.int_value(self.v)

    @staticmethod
    def int_value(x:'gfelem') -> int:
        return uintn.int_value(x.v)




    
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

