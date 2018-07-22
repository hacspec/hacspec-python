from specs.p256 import *
import json
from sys import exit

def main (x: int) -> None :
    # Safe Curve test vectors


	sk0 = to_scalar(0x14)
	point_computed0 = point_mul(sk0)
	point_expected0 = (to_felem(0x83A01A9378395BAB9BCD6A0AD03CC56D56E6B19250465A94A234DC4C6B28DA9A), to_felem(0x76E49B6DE2F73234AE6A5EB9D612B75C9F2202BB6923F54FF8240AAA86F640B8))
	        
	if point_computed0 == point_expected0:
		print("P256 Test 0 succeded")
	else:
		print("P256 Test 0 failed")
		(x_e, y_e) = point_expected0
		print("expected   x: " + str(x_e) + "   y: " + str(y_e))
		(x_c, y_c) = point_computed0
		print("computed   x: " + str(x_c) + "   y: " + str(y_c))
		exit(1)	

	sk1 = to_scalar(0x018ebbb95eed0e13)
	point_computed1 = point_mul(sk1)
	point_expected1 = (to_felem(0x339150844EC15234807FE862A86BE77977DBFB3AE3D96F4C22795513AEAAB82F), to_felem(0xB1C14DDFDC8EC1B2583F51E85A5EB3A155840F2034730E9B5ADA38B674336A21))

	if point_computed1 == point_expected1:
		print("P256 Test 1 succeded")
	else:
		print("P256 Test 1 failed")
		(x_e, y_e) = point_expected1
		print("expected   x: " + str(x_e) + "   y: " + str(y_e))
		(x_c, y_c) = point_computed1
		print("computed   x: " + str(x_c) + "   y: " + str(y_c))	
		exit(1)

	sk2 = to_scalar(0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632550)
	point_computed2 = point_mul(sk2)
	point_expected2 = (to_felem(0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296), to_felem(0xB01CBD1C01E58065711814B583F061E9D431CCA994CEA1313449BF97C840AE0A))

	if point_computed2 == point_expected2:
		print("P256 Test 2 succeded")
	else:
		print("P256 Test 2 failed")
		(x_e, y_e) = point_expected2
		print("expected   x: " + str (x_e) + "   y: " + str(y_e))
		(x_c, y_c) = point_computed2
		print("computed   x: " + str (x_c) + "   y: " + str(y_c))
		exit(1)

main(0)



