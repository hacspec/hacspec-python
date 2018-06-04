from lib.speclib import *
from specs.curve25519 import *
from specs.sha2 import *
from specs.ed25519 import *

n = 16

@typechecked
def normalise_point(s:extended_point_t) -> extended_point_t:
	(x,y,z,t) = s
	return extended_point(fmul(x, finv(z)), fmul(y, finv(z)), felem(nat(1)), fmul(t, finv (z)))


@typechecked
def OS2ECP(s:serialized_point_t) -> Union[extended_point_t, None]:
	return point_decompress(s)

@typechecked
def ECP2OS(p:extended_point_t) -> serialized_point_t :
	return point_compress(p)

@typechecked
def I2OSP(value: nat) -> bytes_t(32):
	return bytes.from_nat_le(nat(value))

@typechecked
def OS2IP(s: serialized_scalar_t) -> felem_t:
	return bytes.to_nat_le(s)

@typechecked
def hash (msg:vlbytes_t) -> serialized_point_t:
	return sha256(msg)

curveOrder = (7237005577332262213973186563042994240857116359379907606001950938285454250989)
cofactor = (8)


@typechecked
def ECVRF_hash_to_curve(ctr: nat, pub: serialized_point_t, input: bytes_t(uint32)) -> Union[extended_point_t, None]:
	tmp = array.create(array.length(input)+64,uint8(0))
	lenMessage = array.length(input)
	tmp[:lenMessage] = input
	tmp[lenMessage:lenMessage + 32] = pub
	tmp[lenMessage + 32:] = I2OSP(ctr)

	hashed = hash(tmp)
	possiblePoint = OS2ECP(hashed)

	if possiblePoint is None:
		if ctr == curveOrder:
			return None
		else:
			return ECVRF_hash_to_curve(ctr + 1, pub, input)
	else:
		p2 = point_mul(I2OSP(8), possiblePoint)
		return p2		


@typechecked
def ECVRF_decode_proof(pi: bytes_t(5*n)) -> Union[Tuple[extended_point_t, bytes_t(n), bytes_t(2*n)], None]:
	gamma = pi[:2*n]
	c = pi[2*n: 3*n]
	s = pi[3*n: 5*n]
	if OS2ECP(gamma) is None:
		return None
	else:	
		return (OS2ECP(gamma), c, s)

@typechecked
def ECVRF_hash_points (g: extended_point_t, h: extended_point_t, pub: extended_point_t, gamma: extended_point_t, gk: extended_point_t, hk: extended_point_t) -> felem_t:
	tmp = array.create(32*6, uint8(0))
	tmp[0:32] = ECP2OS(g)
	tmp[32:64] = ECP2OS(h)
	tmp[64:96] = ECP2OS(pub)
	tmp[96:128] = ECP2OS(gamma)
	tmp[128:160] = ECP2OS(gk)
	tmp[160:192] = ECP2OS(hk)
	hashed = bytes.to_nat_le(hash(tmp))
	result = to_felem(hashed)
	return result

@typechecked
def ECVRF_prove (input: bytes_t(uint32), pub: serialized_point_t, priv: serialized_scalar_t, k:felem_t) -> Union[(bytes_t(5*n)), None]:
	ap = point_decompress(pub)
	if ap is None:
		return False	

	h = ECVRF_hash_to_curve(0, pub, input)
	if h is None:
		return None
	gamma = point_mul(priv, h)
	kPrime = I2OSP(k)
	gk = point_mul(kPrime, g_ed25519)
	hk = point_mul(kPrime, h)


	c = ECVRF_hash_points(g_ed25519, h, ap, gamma, gk, hk)
	c  = OS2IP((I2OSP(c))[16:32])
	cPrime = c * OS2IP(priv)
	s = (k - cPrime + curveOrder) % curveOrder

	tmp = array.create(80, uint8(0))
	tmp[0:32] = ECP2OS(gamma)
	tmp[32:48] = I2OSP(c)
	tmp[48:80] = I2OSP(s)
	return tmp


@typechecked
def ECVRF_proof_to_hash (pi: bytes_t(5*n)) -> Union[(bytes_t(2*n)), None]:
	(gamma, c, s) = ECVRF_decode_proof(pi)
	h = hash(ECP2OS(gamma))
	return I2OSP(h)

@typechecked
def ECVRF_verify (pub: serialized_point_t, pi: bytes_t(5*n), input: bytes_t(uint32)) -> bool:
	ap = point_decompress(pub)
	if ap is None:
		return False
	(gamma, c, s) = ECVRF_decode_proof(pi)
	if gamma is None:
		return false
	yc = point_mul(c, ap)
	gs = point_mul(s, g_ed25519)
	u = point_add(yc, gs)
	h = ECVRF_hash_to_curve(0, pub, input)
	if h is None:
		false

	gammac = point_mul(c, gamma)
	hs = point_mul(s, h)
	v = point_add(gammac, hs)


	c_prime = ECVRF_hash_points(g_ed25519, h, ap, gamma, u, v)
	halfC  = OS2IP((I2OSP(c_prime))[16:32])
	return halfC == OS2IP(c)		
