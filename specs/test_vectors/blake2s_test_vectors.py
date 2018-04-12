from mypy_extensions import TypedDict
from speclib import array

blake2s_test = TypedDict('blake2s_test', {
    'data': str,
    'key': str,
    'nn': int,
    'output': str
    })

blake2s_test_vectors = array([
    {'data': '616263',
    'key': '',
    'nn': 32,
    'output': '508c5e8c327c14e2e1a72ba34eeb452f37458b209ed63a294d999b4c86675982'}
])
