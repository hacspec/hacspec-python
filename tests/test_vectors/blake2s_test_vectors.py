from mypy_extensions import TypedDict
from lib.speclib import *

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
     'output': '508c5e8c327c14e2e1a72ba34eeb452f37458b209ed63a294d999b4c86675982'},
    {'data': '00',
    'key': '000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f',
    'nn': 32,
     'output': '40d15fee7c328830166ac3f918650f807e7e01e177258cdc0a39b11f598066f1'},
    {'data': '000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfe',
    'key': '000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f',
    'nn': 32,
    'output': '3fb735061abc519dfe979e54c1ee5bfad0a9d858b3315bad34bde999efd724dd'}

])
