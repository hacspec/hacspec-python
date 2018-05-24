from mypy_extensions import TypedDict
from hacspec.speclib import *

gf128_test_item = TypedDict('gf128_test_item', {
    'input_len': int,
    'input': str,
    'key' :  str,
    'output' :  str})

gf128_test = vlarray_t(dict)

gf128_test_vectors = gf128_test([
{   'input_len': 92,
    'input': 'feedfacedeadbeeffeedfacedeadbeefabaddad20000000000000000000000005a8def2f0c9e53f1f75d7853659e2a20eeb2b22aafde6419a058ab4f6f746bf40fc0c3b780f244452da3ebf1c5d82cdea2418997200ef82e44ae7e3f',
    'key' :  'acbef20579b4b8ebce889bac8732dad7',
    'output' :  'cc9ae9175729a649936e890bd971a8bf'
}
])
