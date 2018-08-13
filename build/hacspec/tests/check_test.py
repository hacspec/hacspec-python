# Testing spec checker

from hacspec.speclib import *

@typechecked
def test_lists() -> None:
    my_vlarray_t = vlarray_t(uint32_t)
    x : my_vlarray_t = my_vlarray_t([uint32(0), uint32(1)])

    my_array_t = array_t(uint32_t, 2)
    x = my_array_t([uint32(0), uint32(1)])

    x = vlbytes_t([uint8(0), uint8(1)])

    my_bytes_t = bytes_t(3)
    x = my_bytes_t([uint8(0), uint8(1), uint8(255)])

    print("hacspec arrays are working.")
