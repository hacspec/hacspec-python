from mypy_extensions import TypedDict
from lib.speclib import *

curve25519_test_item = TypedDict('curve25519_test_item', {
    'private':  str,
    'public' :  str,
    'result' :  str,
    'valid'  :  bool}
)

curve25519_test = vlarray_t(dict)

curve25519_test_vectors = curve25519_test([
	{
		'private' :  '77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a',
		'public' : 'de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f',
		'result' :'4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742',
		'valid' : True
	},
	{
		'private' :  '5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb',
		'public' : '8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a',
		'result' :'4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742',
		'valid' : True
	},
	{
		'private' :  '01'+('00'*31),
		'public' : '2500000000000000000000000000000000000000000000000000000000000000',
		'result' :'3c7777caf997b264416077665b4e229d0b9548dc0cd81998ddcdc5c8533c797f',
		'valid' : True
	},
	{
		'private' :  '01'+('00'*31),
		'public' : 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
		'result' :'b32d1362c248d62fe62619cff04dd43db73ffc1b6308ede30b78d87380f1e834',
		'valid' : True
	},
	{
		'private' :  'a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4',
		'public' : 'e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c',
		'result' :'c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552',
		'valid' : True
	},
	# {
	# 	'private' :  '01020304'+('00'*28),
 #        'public' : '00'*32,
	# 	'result' : '00'*32,
	# 	'valid' : False
	# },
	# {
	# 	'private' :  '02040608'+('00'*28),
	# 	'public' : 'e0eb7a7c3b41b8ae1656e3faf19fc46ada098deb9c32b1fd866205165f49b8',
	#     'result' : '00'*32,
	# 	'valid' : False
	# }
])
