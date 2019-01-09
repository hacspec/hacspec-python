from lib.speclib import *

state_t = array_t(uint64_t, 25)
index_t = range_t(0, 5)
max_size_t : int = op_Subtraction(pow2(130), 1)
max_size_nat: int = op_Subtraction(pow2(32), 1)
size_nat_t = range_t(0, 4294967295)
size_nat_24_t = range_t(0, 23)
size_nat_25_t = range_t(0, 24)
size_nat_200_t = range_t(0, 200)
size_nat_0_200_t = range_t(1, 201)

rotval_u64_t = range_t(1, 64)
piln_t = range_t(1, 25)
lseq_rotc_t_24_t = array_t(rotval_u64_t, 24)
lseq_pilns_t_24_t = array_t(piln_t, 24)
lseq_rndc_t_24_t = array_t(uint64_t, 24)
lseq_uint64_5_t = array_t(uint64_t, 5)

lbytes_200_t = array_t(uint8_t, 200)

keccak_rotc: lseq_rotc_t_24_t = lseq_rotc_t_24_t[1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 2, 14, 27, 41, 56, 8, 25, 43, 62, 18, 39, 61, 20, 44]
keccak_piln: lseq_pilns_t_24_t = lseq_pilns_t_24_t[10, 7, 11, 17, 18, 3, 5, 16, 8, 21, 24, 4, 15, 23, 19, 13, 12, 2, 20, 14, 22, 9, 6, 1]
keccak_rndc: lseq_rndc_t_24_t = lseq_rndc_t_24_t[uint64(0x0000000000000001), uint64(0x0000000000008082), uint64(0x800000000000808a), 
uint64(0x8000000080008000), uint64(0x000000000000808b), uint64(0x0000000080000001), uint64(0x8000000080008081), 
uint64(0x8000000000008009), uint64(0x000000000000008a), uint64(0x0000000000000088), uint64(0x0000000080008009), 
uint64(0x000000008000000a), uint64(0x000000008000808b), uint64(0x800000000000008b), uint64(0x8000000000008089), 
uint64(0x8000000000008003), uint64(0x8000000000008002), uint64(0x8000000000000080), uint64(0x000000000000800a), 
uint64(0x800000008000000a), uint64(0x8000000080008081), uint64(0x8000000000008080), uint64(0x0000000080000001), 
uint64(0x8000000080008008)]



@typechecked
def readLane(s: state_t, x: index_t, y: index_t) -> uint64_t:
    return s[x + 5 * y]


@typechecked
def writeLane(s: state_t, x: index_t, y: index_t, v: uint64_t) -> state_t:
    s[x + 5 * y] = v
    return s

@typechecked
def rotl(a: uint64_t, b: rotval_u64_t) -> uint64_t:
    return uintn.rotate_left(a, b)


@typechecked
def state_theta_inner_C(s: state_t, i: nat_t, _C: lseq_uint64_5_t) -> lseq_uint64_5_t:
    _C[i] = readLane(s, i, 0) ^ readLane(s, i, 1) ^ readLane(s, i, 2) ^ readLane(s, i, 3) ^ readLane(s, i, 4)
    return _C

@typechecked
def state_theta0(s: state_t, _C: lseq_uint64_5_t) -> lseq_uint64_5_t:
    for x in range(5):
        _C: lseq_uint64_5_t = state_theta_inner_C(s, x, _C)
    return _C    

@typechecked
def state_theta_inner_s_inner(x: index_t, _D: uint64_t, y: index_t, s: state_t)-> state_t:
    return writeLane(s, x, y, readLane(s, x, y) ^ _D)

@typechecked
def state_theta_inner_s (_C : lseq_uint64_5_t, x: index_t, s: state_t) -> state_t:
    _D: uint64_t = _C[(x + 4) % 5] ^ rotl(_C[(x + 1) % 5], 1)
    for y in range(5):
        s:state_t = state_theta_inner_s_inner(x, _D, y, s)
    return s

@typechecked
def state_theta1(s: state_t, _C: lseq_uint64_5_t) -> state_t:
    for x in range(5):
        s:state_t = state_theta_inner_s(_C, x, s)
    return s    

@typechecked
def state_theta(s: state_t) -> state_t:
    _C: vlarray_t(uint64_t) = array.create(5, uint64(0)) 
    _C = state_theta0(s, _C)
    return state_theta1(s, _C)


@typechecked
def state_pi_rho_inner(t: size_nat_24_t, current: uint64_t, s_pi_rho: state_t) -> tuple_t(uint64_t, state_t):
    r : int = keccak_rotc[t]
    _Y : index_t = keccak_piln[t]
    temp : uint64_t = s_pi_rho[_Y]
    s_pi_rho[_Y] = rotl(current, r)
    current : uint64_t = temp
    return (current, s_pi_rho)

@typechecked
def state_pi_rho(s_theta: state_t) -> state_t:
    current : uint64_t = readLane(s_theta, 1, 0)
    s_pi_rho : state_t = array.copy(s_theta)
    for t in range(24):
        (current, s_pi_rho) = state_pi_rho_inner(t, current, s_pi_rho)
    return s_pi_rho    


@typechecked
def state_chi_inner(s_pi_rho: state_t, y: index_t, x: index_t, s: state_t)-> state_t : 
    s_chi:state_t = writeLane(s, x, y, (readLane(s_pi_rho, x, y)) ^ 
        ((~(readLane(s_pi_rho, (x + 1) % 5, y)) & (readLane(s_pi_rho, (x + 2) % 5, y)))))
    return s_chi

@typechecked
def state_chi_inner1(s_pi_rho: state_t, y: index_t, s: state_t) -> state_t:
    s_chi: state_t = array.copy(s_pi_rho)
    for x in range (5):
        s_chi:state_t =state_chi_inner(s_pi_rho, y, x, s)
    return s_chi

@typechecked
def state_chi(s_pi_rho: state_t) -> state_t:
    saved: state_t = array.copy(s_pi_rho)
    s_chi: state_t = array.copy(s_pi_rho)
    for y in range(5):
        s_chi:state_t = state_chi_inner1(s_pi_rho, y, saved)
    return s_chi    

@typechecked
def state_iota(s: state_t, r: size_nat_24_t) -> state_t:
    return writeLane(s, 0, 0, readLane(s, 0, 0) ^ keccak_rndc[r])


@typechecked
def state_permute1(s: state_t, round: size_nat_24_t) -> state_t:
    s_theta: state_t = state_theta(s)
    s_pi_rho:state_t = state_pi_rho(s_theta)
    s_chi:state_t = state_chi(s_pi_rho)
    s_iota:state_t = state_iota(s_chi, round)
    return s_iota


@typechecked
def state_permute(s: state_t) -> state_t:
    s: state_t 
    for i in range(24):
        s = state_permute1(s, i)
    return s

# @contract3(lambda rateInBytes, input_b, s:
#             array.length(input_b) == rateInBytes,
#            lambda rateInBytes, input_b, s, res:
#             True)


@typechecked
def loadState_inner(block: lbytes_200_t, j: size_nat_25_t, s: state_t) -> state_t:
    nj : uint64_t = bytes.to_uint64_le(block[(j * 8):(j * 8 + 8)])
    s[j] = s[j] ^ nj
    return s

@typechecked
def loadState(rateInBytes: size_nat_200_t, input_b: vlbytes_t, s: state_t) -> state_t:
    block: lbytes_200_t = array.create(200, uint8(0))
    block[0:rateInBytes] = input_b
    for j in range(25):
        s:state_t = loadState_inner(block, j, s)
    return s

# @contract3(lambda rateInBytes, s:
#             True,
#            lambda rateInBytes, s, res:
#             array.length(res) == rateInBytes)

@typechecked
def storeState_inner(s: state_t, j: size_nat_25_t, block: lbytes_200_t) -> lbytes_200_t:
    block[(j * 8):(j * 8 + 8)] = bytes.from_uint64_le(s[j])
    return block

@typechecked
def storeState(rateInBytes: size_nat_200_t, s: state_t) -> lbytes_200_t:
    block: vlbytes_t = bytes(array.create(200, uint8(0)))
    for j in range(25):
        block = storeState_inner(s, j, block)
    return block[0:rateInBytes]

# @contract3(lambda s, rateInBytes, inputByteLen, input_b, delimitedSuffix:
#             0 < rateInBytes and rateInBytes <= 200 and array.length(input_b) == inputByteLen,
#            lambda s, rateInBytes, inputByteLen, input_b, delimitedSuffix, res:
#             True)


@typechecked 
def absorb_next(s: state_t, rateInBytes : size_nat_0_200_t)-> state_t : 
    nextBlock: vlbytes_t = array.create(rateInBytes, uint8(0))
    nextBlock[rateInBytes - 1] = uint8(0x80)
    s:state_t = loadState(rateInBytes, nextBlock, s)
    s:state_t = state_permute(s)
    return s

@typechecked
def absorb_last(delimitedSuffix: uint8_t, rateInBytes: size_nat_0_200_t, rem: nat_t, input_b: lbytes_200_t, inputByteLen: size_nat_t, s: state_t)-> state_t:
    last : array_t(uint8_t, 200) = input_b[(inputByteLen - rem):inputByteLen]
    lastBlock: vlbytes_t = array.create(rateInBytes, uint8(0))
    lastBlock[0:rem] = last
    lastBlock[rem] = delimitedSuffix
    s:state_t = loadState(rateInBytes, lastBlock, s) 

    if not(delimitedSuffix & uint8(0x80) == uint8(0)) and (rem == rateInBytes - 1):
        s = state_permute(s)

    s = absorb_next(s, rateInBytes)   
    return s


@typechecked
def absorb_inner(rateInBytes: size_nat_0_200_t, block: lbytes_200_t, s: state_t, i: nat_t) -> state_t:
    s:state_t = loadState(rateInBytes, block[(i*rateInBytes):(i*rateInBytes + rateInBytes)], s)
    s = state_permute(s)
    return s

@typechecked
def absorb(s: state_t,
           rateInBytes: size_nat_0_200_t,
           inputByteLen: size_nat_t,
           input_b: vlbytes_t,
           delimitedSuffix: uint8_t) -> state_t:
    n : int = inputByteLen // rateInBytes
    rem : int = inputByteLen % rateInBytes
    for i in range(n):
        s  : state_t = absorb_inner(rateInBytes, input_b, s, i)  
    s : state_t = absorb_last(delimitedSuffix, rateInBytes, rem, input_b, inputByteLen, s)
    return s


# # @contract3(lambda s, rateInBytes, outputByteLen:
# #             0 < rateInBytes and rateInBytes <= 200,
# #            lambda s, rateInBytes, outputByteLen, res:
# #             array.length(res) == outputByteLen)


@typechecked
def squeeze_inner(rateInBytes: size_nat_0_200_t, outputByteLen: size_nat_t, i: nat_t, s: state_t)-> tuple_t(lbytes_200_t, state_t):
    block : vlbytes_t = storeState(rateInBytes, s)
    s : state_t = state_permute(s)
    return (block, s)


@typechecked
def squeeze(s: state_t,
            rateInBytes: size_nat_0_200_t,
            outputByteLen: size_nat_t) -> vlbytes_t:
    output: vlbytes_t = array.create(outputByteLen, uint8(0))
    outBlocks : int = outputByteLen // rateInBytes
    block: vlbytes_t = array.create(200, uint8(0))
    s: state_t
    
    for i in range(outBlocks):
        (block, s) = squeeze_inner(rateInBytes, outputByteLen, i, s)
        output[(i*rateInBytes):(i*rateInBytes + rateInBytes)] = block

    remOut : size_nat_t = outputByteLen % rateInBytes
    outBlock : vlbytes_t = storeState(remOut, s)
    output[(outputByteLen - remOut):outputByteLen] = outBlock
    return output


@typechecked
def keccak(rate: size_nat_t, capacity: size_nat_t, inputByteLen: size_nat_t,
           input_b: vlbytes_t, delimitedSuffix: uint8_t, outputByteLen: size_nat_t) -> vlbytes_t:
    rateInBytes : nat_t = rate // 8
    s: state_t  = array.create(25, uint64(0))
    s: state_t= absorb(s, rateInBytes, inputByteLen, input_b, delimitedSuffix)
    output : vlbytes_t = squeeze(s, rateInBytes, outputByteLen)
    return output


# @contract3(lambda inputByteLen, input_b, outputByteLen:
#             array.length(input_b) == inputByteLen,
#            lambda inputByteLen, input_b, outputByteLen, res:
#             array.length(res) == outputByteLen)
@typechecked
def shake128(inputByteLen: size_nat_t,
             input_b: vlbytes_t,
             outputByteLen: size_nat_t) -> vlbytes_t:
    return keccak(1344, 256, inputByteLen, input_b, uint8(0x1F), outputByteLen)


# @contract3(lambda inputByteLen, inpuvlbytes_tt_b, outputByteLen:
#             array.length(input_b) == inputByteLen,
#            lambda inputByteLen, input_b, outputByteLen, res:
#             array.length(res) == outputByteLen)
@typechecked
def shake256(inputByteLen: size_nat_t,
             input_b: vlbytes_t,
             outputByteLen: size_nat_t) -> vlbytes_t:
    return keccak(1088, 512, inputByteLen, input_b, uint8(0x1F), outputByteLen)


# @contract3(lambda inputByteLen, input_b:
#             array.length(input_b) == inputByteLen,
#            lambda inputByteLen, input_b, res:
#             array.length(res) == 28)
@typechecked
def sha3_224(inputByteLen: size_nat_t,
             input_b: vlbytes_t) -> vlbytes_t:
    return keccak(1152, 448, inputByteLen, input_b, uint8(0x06), 28)


# @contract3(lambda inputByteLen, input_b:
#             array.length(input_b) == inputByteLen,
#            lambda inputByteLen, input_b, res:
#             array.length(res) == 32)
@typechecked
def sha3_256(inputByteLen: size_nat_t,
             input_b: vlbytes_t) -> vlbytes_t:
    return keccak(1088, 512, inputByteLen, input_b, uint8(0x06), 32)


# @contract3(lambda inputByteLen, input_b:
#             array.length(input_b) == inputByteLen,
#            lambda inputByteLen, input_b, res:
#             array.length(res) == 48)
@typechecked
def sha3_384(inputByteLen: size_nat_t,
             input_b: vlbytes_t) -> vlbytes_t:
    return keccak(832, 768, inputByteLen, input_b, uint8(0x06), 48)


# @contract3(lambda inputByteLen, input_b:
#             array.length(input_b) == inputByteLen,
#            lambda inputByteLen, input_b, res:
#             array.length(res) == 64)
@typechecked
def sha3_512(inputByteLen: size_nat_t,
             input_b: vlbytes_t) -> vlbytes_t:
    return keccak(576, 1024, inputByteLen, input_b, uint8(0x06), 64)
