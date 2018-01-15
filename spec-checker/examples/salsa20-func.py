def rotate(x, n):
    x &= 0xffffffff
    return ((x << n) | (x >> (32 - n))) & 0xffffffff

def step(s0, i, j, k, r):
    s1 = s0
    s1[i] ^= rotate(s[j] + s[k],r)
    return s1

def quarterround(s0, i0, i1, i2, i3):
    s1 = step(s0, i1, i0, i3, 7)
    s2 = step(s1, i2, i1, i0, 9)
    s3 = step(s2, i3, i2, i1, 13)
    s4 = step(s3, i0, i3, i2, 18)
    return s4

def rowround(s0):
    s1 = quarterround(s0, 0, 1, 2, 3)
    s2 = quarterround(s1, 5, 6, 7, 4)
    s3 = quarterround(s2, 10, 11, 8, 9)
    s4 = quarterround(s3, 15, 12, 13, 14)

def columnround(s0):
    s1 = quarterround(s0, 0, 4, 8, 12)
    s2 = quarterround(s1, 5, 9, 13, 1)
    s3 = quarterround(s2, 10, 14, 2, 6)
    s4 = quarterround(s3, 15, 3, 7, 11)
    return s4

def doubleround(s0):
    s1 = columnround(s0)
    s2 = rowround(s1)
    return s2

# def hsalsa20(n,k):
#     n=''.join([chr(n[i]) for i in range(16)])
#     n = struct.unpack('<4I', n)
#     k=''.join([chr(k[i]) for i in range(32)])
#     k = struct.unpack('<8I', k)
#     s = [0] * 16
#     s[::5] = struct.unpack('<4I', 'expand 32-byte k')
#     s[1:5] = k[:4]
#     s[6:10] = n
#     s[11:15] = k[4:]
#     for i in range(10): s = doubleround(s)
#     s = [s[i] for i in [0,5,10,15,6,7,8,9]]
#     return struct.pack('<8I',*s)