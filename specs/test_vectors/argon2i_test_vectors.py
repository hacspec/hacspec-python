from mypy_extensions import TypedDict
from hacspec.speclib import *

argon2i_test_item = TypedDict('blake2b_test_item', {
    'p': str,
    's': str,
    'lanes': int,
    't_len': int,
    'm': int,
    'iterations': int,
    'x' : str,
    'k' : str,
    'output': str
    })

argon2i_test = vlarray_t(dict)

argon2i_test_vectors = argon2i_test([{
    'p': '0101010101010101010101010101010101010101010101010101010101010101',
    's': '02020202020202020202020202020202',
    'lanes': 4,
    't_len': 32,
    'm': 32,
    'iterations': 3,
    'x': '040404040404040404040404',
    'k': '0303030303030303',
    'output': 'c814d9d1dc7f37aa13f0d77f2494bda1c8de6b016dd388d29952a4c4672b6ce8'
}])
