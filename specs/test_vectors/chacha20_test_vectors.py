from mypy_extensions import TypedDict
from speclib import array

chacha20_test = TypedDict('chacha20_test', {
    'input_len': str,
    'input': str,
    'key' :  str,
    'nonce' :  str,
    'counter' :  str,
    'output' :  str}
)

chacha20_test_vectors : array[chacha20_test] = [
]
