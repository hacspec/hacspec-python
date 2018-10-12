from lib.speclib import *
import time

performance_test = None

testing: ruint32_t = ruint32_t(0x20)
print(testing + ruint32_t(0x5))
print(testing - ruint32_t(0x5))
print(ruintn_t.to_int(testing - ruint32_t(0x5)))
print(ruint32_t.rotate_right(testing, 7))



if performance_test:
    start = time.time()
    x: ruint32_t = ruint32_t(0x20)
    for _ in range(1,100000):
        x = ruint32_t.rotate_right(x, 1)
    end = time.time()

    print("done with ruint32_t "+str(end-start))

    start = time.time()
    y: uint32_t = uint32(0x20)
    for _ in range(1,100000):
        y = uint32_t.rotate_right(y, 1)
    end = time.time()

    print("done with uint32_t  "+str(end-start))
