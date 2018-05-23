from mypy_extensions import TypedDict
from hacspec.speclib import *

blake2s_test_item = TypedDict('blake2s_test_item', {
    'data': str,
    'key': str,
    'nn': int,
    'output': str
    })

blake2s_test = vlarray_t(dict)

blake2s_test_vectors = blake2s_test([
    {'data': '616263',
    'key': '',
    'nn': 32,
    'output': '508c5e8c327c14e2e1a72ba34eeb452f37458b209ed63a294d999b4c86675982'}
])
