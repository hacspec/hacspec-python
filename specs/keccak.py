from speclib import *

def lfsr86540(lfsr:uint8) -> tuple2(uint8_t, bool):
    lfsr1 = lfsr & uint8(1)
    result = not (lfsr1 == uint8(0))
    lfsr2 = lfsr << 1
    if (lfsr & uint8(0x80)) != uint8(0):
        return (lfsr2 ^ uint8(0x71), result)
    else:
        return (lfsr2, result)

state_t = array_t(uint64_t, 25)
index_t = range_t(0, 5)

def readLane (s:state_t, x:index_t, y:index_t) -> uint64_t:
    return s[x + 5 * y]

def writeLane (s:state_t, x:index_t, y:index_t, v:uint64) -> state_t:
    s[x + 5 * y] = v
    return s

def state_permute1 (s:state_t, lfsr:uint8_t) -> tuple2(state_t, uint8_t):
    _C = array.create(5, uint64(0))
    for x in range(5):
        _C[x] = readLane(s, x, 0) ^ readLane(s, x, 1) ^ readLane(s, x, 2) ^ readLane(s, x, 3) ^ readLane(s, x, 4)

    s_theta = array.copy(s)
    for x in range(5):
        _D = _C[(x + 4) % 5] ^ uint64.rotate_left(_C[(x + 1) % 5], 1)
        for y in range(5):
            s_theta = writeLane(s_theta, x, y, readLane(s_theta, x, y) ^ _D)

    x = 1
    y = 0
    current = readLane(s_theta, x, y)
    s_pi_rho = array.copy(s_theta)

    for t in range(24):
        r = ((t + 1) * (t + 2)//2) % 64
        _Y = (2 * x + 3 * y) % 5
        x = y
        y = _Y
        temp = readLane(s_pi_rho, x, y)
        s_pi_rho = writeLane(s_pi_rho, x, y, uint64_t.rotate_left(current, r))
        current = temp

    temp = array.copy(s_pi_rho)
    s_chi = array.copy(s_pi_rho)

    for y in range(5):
        for x in range(5):
            s_chi = writeLane(s_chi, x, y, readLane(temp, x, y) ^ ((~(readLane(temp, (x + 1) % 5, y)) & readLane(temp, (x + 2) % 5, y ))))

    s_iota = array.copy(s_chi)

    for j in range(7):
        bitPosition = 2 ** j - 1
        lfsr,result = lfsr86540(lfsr)
        if result == True:
            s_iota = writeLane(s_iota, 0, 0, readLane(s_iota, 0, 0) ^ (uint64(1) << bitPosition))

    return (s_iota, lfsr)

def state_permute (s:state_t) -> state_t:
    lfsr = uint8(0x01)
    for i in range(24):
        s,lfsr = state_permute1(s,lfsr)
    return s

bytes_len_t = refine(vlbytes_t, lambda x: array.length(x) <= 200)
max_size_t = 2**64 - 1
size_nat = refine(nat, lambda x: x <= max_size_t)
size_nat_200 = refine(nat, lambda x: x <= 200)
size_nat_1600 = refine(nat, lambda x: x <= 1600 and x % 8 == 0 and x // 8 > 0)

def loadState (rateInBytes:size_nat_200, input_b:bytes_len_t, s:state_t) -> state_t:
    block = array.create(200, uint8(0))
    block[0:rateInBytes] = input_b
    for j in range(25):
        nj = vlbytes.to_uint64_le(block[(j * 8):(j * 8 + 8)])
        s[j] = s[j] ^ nj
    return s

def storeState (rateInBytes:size_nat_200, s:state_t) -> bytes_len_t:
    block = array.create(200, uint8(0))
    for j in range(25):
        block[(j * 8):(j * 8 + 8)] = vlbytes.from_uint64_le(s[j])
    return block[0:rateInBytes]

def absorb (rateInBytes:size_nat_200, inputByteLen:size_nat, input_b:vlbytes_t, delimitedSuffix:uint8_t) -> state_t:
    s = array.create(25, uint64(0))
    n = inputByteLen // rateInBytes
    for i in range(n):
        s = loadState(rateInBytes, input_b[(i*rateInBytes):(i*rateInBytes + rateInBytes)], s)
        s = state_permute(s)

    rem = inputByteLen % rateInBytes
    last = input_b[(inputByteLen - rem):inputByteLen]
    lastBlock = array.create(rateInBytes, uint8(0))
    lastBlock[0:rem] = last
    lastBlock[rem] = delimitedSuffix
    s = loadState(rateInBytes, lastBlock, s)

    if not(delimitedSuffix & uint8(0x80) == uint8(0)) and (rem == rateInBytes - 1):
        s = state_permute(s)

    nextBlock = array.create(rateInBytes, uint8(0))
    nextBlock[rateInBytes - 1] = uint8(0x80)
    s = loadState(rateInBytes, nextBlock, s)
    s = state_permute(s)
    return s

def squeeze (s:state_t, rateInBytes:size_nat_200, outputByteLen:size_nat) -> vlbytes_t:
    output = array.create(outputByteLen, uint8(0))
    outBlocks = outputByteLen // rateInBytes
    for i in range(outBlocks):
        block = storeState(rateInBytes, s)
        output[(i*rateInBytes):(i*rateInBytes + rateInBytes)] = block
        s = state_permute(s)

    remOut = outputByteLen % rateInBytes
    outBlock = storeState(remOut, s)
    output[(outputByteLen - remOut):outputByteLen] = outBlock
    return output

def keccak (rate:size_nat_1600, capacity:size_nat, inputByteLen:size_nat,
            input_b:vlbytes_t, delimitedSuffix:uint8_t, outputByteLen:size_nat) -> vlbytes_t:
    rateInBytes = rate // 8
    s = absorb(rateInBytes, inputByteLen, input_b, delimitedSuffix)
    output = squeeze(s, rateInBytes, outputByteLen)
    return output

def shake128 (inputByteLen:size_nat, input_b:vlbytes_t, outputByteLen:size_nat) -> vlbytes_t:
    return keccak(1344, 256, inputByteLen, input_b, uint8(0x1F), outputByteLen)

def shake256 (inputByteLen:size_nat, input_b:vlbytes_t, outputByteLen:size_nat) -> vlbytes_t:
    return keccak(1088, 512, inputByteLen, input_b, uint8(0x1F), outputByteLen)

def sha3_224 (inputByteLen:size_nat, input_b:vlbytes_t) -> vlbytes_t:
    return keccak(1152, 448, inputByteLen, input_b, uint8(0x06), 28)

def sha3_256 (inputByteLen:size_nat, input_b:vlbytes_t) -> vlbytes_t:
    return keccak(1088, 512, inputByteLen, input_b, uint8(0x06), 32)

def sha3_384 (inputByteLen:size_nat, input_b:vlbytes_t) -> vlbytes_t:
    return keccak(832, 768, inputByteLen, input_b, uint8(0x06), 48)

def sha3_512 (inputByteLen:size_nat, input_b:vlbytes_t) -> vlbytes_t:
    return keccak(576, 1024, inputByteLen, input_b, uint8(0x06), 64)
