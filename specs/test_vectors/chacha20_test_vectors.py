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
{'input_len': '34',
 'input'    : '43727970746f6772617068696320466f72756d2052657365617263682047726f7570',
 'key'    : '85d6be7857556d337f4452fe42d506a80103808afb0db2fd4abff6af4149f51b',
 'tag'    : 'a8061dc1305136c6c22b8baf0c0127a9'}
]
