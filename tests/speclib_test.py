from lib.speclib import *
from random import SystemRandom
import unittest

class ruint32_test(unittest.TestCase):
    modulus = 1 << 32
    rand = SystemRandom()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def compare(self, x:ruint32_t, y:uint32):
        x_val = ruintn_t.to_int(x)
        y_val = natmod.to_int(y)
        if x_val != y_val:
            print(str(x_val)+" != "+str(y_val))
        self.assertEqual(x_val, y_val)

    def test_init(self):
        x = ruint32_t(0)
        y = uint32(0)
        self.compare(x, y)
        try:
            x = ruint32_t(-1)
            self.assertTrue(False)
        except Exception as e:
            pass
        max32 = (1<<32)-1
        x = ruint32_t(max32)
        y = uint32(max32)
        self.compare(x, y)
        val = (1<<32)+5
        x = ruint32_t(val)
        y = uint32(val)
        self.compare(x, y)

    def test_shift(self):
        val = self.rand.randrange(1, 1<<32)
        x = ruint32_t(val)
        y = uint32(val)
        self.compare(x << 5, y << 5)
        self.compare(x << 32, y << 32)
        self.compare(x >> 5, y >> 5)
        self.compare(x >> 32, y >> 32)
        try:
            x << 33
            x << -1
            x >> 33
            x >> -1
            self.assertTrue(False)
        except Exception as e:
            pass

    def test_rotate(self):
        val = self.rand.randrange(1, 1<<32)
        x = ruint32_t(val)
        y = uint32(val)
        self.compare(ruint32.rotate_right(x, 5), uint32.rotate_right(y, 5))
        self.compare(ruint32.rotate_right(x, 31), uint32.rotate_right(y, 31))
        self.compare(ruint32.rotate_left(x, 5), uint32.rotate_left(y, 5))
        self.compare(ruint32.rotate_left(x, 31), uint32.rotate_left(y, 31))
        try:
            ruint32.rotate_right(x, 32)
            ruint32.rotate_right(x, -1)
            ruint32.rotate_left(x, 32)
            ruint32.rotate_left(x, -1)
            self.assertTrue(False)
        except Exception as e:
            pass

    def test_arithmetic(self):
        val1 = self.rand.randrange(1, 1<<32)
        val2 = self.rand.randrange(1, 1<<32)
        x1 = ruint32_t(val1)
        x2 = ruint32_t(val2)
        y1 = uint32(val1)
        y2 = uint32(val2)
        self.compare(x1+x2, y1+y2)
        self.compare(x1*x2, y1*y2)
        self.compare(x1-x2, y1-y2)
        self.compare(x1^x2, y1^y2)
        self.compare(x1&x2, y1&y2)
        self.compare(x1|x2, y1|y2)

class bytes_test(unittest.TestCase):
    rand = SystemRandom()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_from_uint64_be(self):
        val = self.rand.randrange(1, 1<<64)
        x = ruint64_t(val)
        b = bytes.from_uint64_be(x)
        self.assertEqual(str(x), str(b))


if __name__ == '__main__':
    unittest.main()
