def rotate(x, n):
    x &= 0xffffffff
    return ((x << n) | (x >> (32 - n))) & 0xffffffff

def step(s, i, j, k, r):
    s[i] ^= rotate(s[j] + s[k],r)

def quarterround(s, i0, i1, i2, i3):
    step(s, i1, i0, i3, 7)
    step(s, i2, i1, i0, 9)
    step(s, i3, i2, i1, 13)
    step(s, i0, i3, i2, 18)

def rowround(s):
    quarterround(s, 0, 1, 2, 3)
    quarterround(s, 5, 6, 7, 4)
    quarterround(s, 10, 11, 8, 9)
    quarterround(s, 15, 12, 13, 14)

def columnround(s):
    quarterround(s, 0, 4, 8, 12)
    quarterround(s, 5, 9, 13, 1)
    quarterround(s, 10, 14, 2, 6)
    quarterround(s, 15, 3, 7, 11)

def doubleround(s):
    columnround(s)
    rowround(s)

def hsalsa20(n,k):
    n=''.join([chr(n[i]) for i in range(16)])
    n = struct.unpack('<4I', n)
    k=''.join([chr(k[i]) for i in range(32)])
    k = struct.unpack('<8I', k)
    s = [0] * 16
    s[::5] = struct.unpack('<4I', 'expand 32-byte k')
    s[1:5] = k[:4]
    s[6:10] = n
    s[11:15] = k[4:]
    for i in range(10): doubleround(s)
    s = [s[i] for i in [0,5,10,15,6,7,8,9]]
    return struct.pack('<8I',*s)