from lib.speclib import *

state_t = array_t(uint64_t, 25)
index_t = range_t(0, 5)
max_size_t = 2**64 - 1
size_nat_t, size_nat = refine(int, lambda x: x <= max_size_t and x >= 0)
size_nat_200_t, size_nat_200 = refine(int, lambda x: x <= 200 and x >= 0)
size_nat_1600_t, size_nat_1600 = refine(int, lambda x: x <= 1600 and x %
                                        8 == 0 and x // 8 > 0 and x >= 0)


@typechecked
def lfsr86540(lfsr: uint8_t) -> tuple2(uint8_t, bool):
    lfsr1 : uint8_t = lfsr & uint8(1)
    result : bool = not (lfsr1 == uint8(0))
    lfsr2 : uint8_t = lfsr << 1
    if (lfsr & uint8(0x80)) != uint8(0):
        return (lfsr2 ^ uint8(0x71), result)
    else:
        return (lfsr2, result)


@typechecked
def readLane(s: state_t, x: index_t, y: index_t) -> uint64_t:
    return s[x + 5 * y]


@typechecked
def writeLane(s: state_t, x: index_t, y: index_t, v: uint64_t) -> state_t:
    s[x + 5 * y] = v
    return s


@typechecked
def state_permute1(s: state_t, lfsr: uint8_t) -> tuple2(state_t, uint8_t):
    _C = array.create(5, uint64(0))
    for x in range(5):
        _C[x] = readLane(s, x, 0) ^ readLane(s, x, 1) ^ readLane(
            s, x, 2) ^ readLane(s, x, 3) ^ readLane(s, x, 4)

    s_theta = array.copy(s)
    _D : uint64_t
    for x in range(5):
        _D = _C[(x + 4) % 5] ^ uintn.rotate_left(_C[(x + 1) % 5], 1)
        for y in range(5):
            s_theta = writeLane(s_theta, x, y, readLane(s_theta, x, y) ^ _D)

    x : int = 1
    y : int = 0
    current : uint64_t = readLane(s_theta, x, y)
    s_pi_rho = array.copy(s_theta)

    for t in range(24):
        r : int = ((t + 1) * (t + 2)//2) % 64
        _Y : index_t = (2 * x + 3 * y) % 5
        x : index_t = y
        y : index_t = _Y
        temp : uint64_t = readLane(s_pi_rho, x, y)
        s_pi_rho : state_t = writeLane(s_pi_rho, x, y, uintn.rotate_left(current, r))
        current : uint64_t = temp

    temp = array.copy(s_pi_rho)
    s_chi = array.copy(s_pi_rho)

    for y in range(5):
        for x in range(5):
            s_chi = writeLane(s_chi, x, y, readLane(temp, x, y) ^ (
                (~(readLane(temp, (x + 1) % 5, y)) & readLane(temp, (x + 2) % 5, y))))

    s_iota = array.copy(s_chi)

    for j in range(7):
        bitPosition : int = 2 ** j - 1
        lfsr : uint8_t
        result : bool
        lfsr, result = lfsr86540(lfsr)
        if result == True:
            s_iota = writeLane(s_iota, 0, 0, readLane(
                s_iota, 0, 0) ^ (uint64(1) << bitPosition))

    return (s_iota, lfsr)


@typechecked
def state_permute(s: state_t) -> state_t:
    lfsr : uint8_t = uint8(0x01)
    for i in range(24):
        s : state_t
        lfsr : uint8_t
        s, lfsr = state_permute1(s, lfsr)
    return s

@contract3(lambda rateInBytes, input_b, s:
            array.length(input_b) == rateInBytes,
           lambda rateInBytes, input_b, s, res:
            True)
@typechecked
def loadState(rateInBytes: size_nat_200_t, input_b: vlbytes_t, s: state_t) -> state_t:
    block = array.create(200, uint8(0))
    block[0:rateInBytes] = input_b
    for j in range(25):
        nj : uint64_t = bytes.to_uint64_le(block[(j * 8):(j * 8 + 8)])
        s[j] = s[j] ^ nj
    return s

@contract3(lambda rateInBytes, s:
            True,
           lambda rateInBytes, s, res:
            array.length(res) == rateInBytes)
@typechecked
def storeState(rateInBytes: size_nat_200_t, s: state_t) -> vlbytes_t:
    block = bytes(array.create(200, uint8(0)))
    for j in range(25):
        block[(j * 8):(j * 8 + 8)] = bytes.from_uint64_le(s[j])
    return block[0:rateInBytes]

@contract3(lambda s, rateInBytes, inputByteLen, input_b, delimitedSuffix:
            0 < rateInBytes and rateInBytes <= 200 and array.length(input_b) == inputByteLen,
           lambda s, rateInBytes, inputByteLen, input_b, delimitedSuffix, res:
            True)
@typechecked
def absorb(s: state_t,
           rateInBytes: nat_t,
           inputByteLen: size_nat_t,
           input_b: vlbytes_t,
           delimitedSuffix: uint8_t) -> state_t:
    n : int = inputByteLen // rateInBytes
    s : state_t
    for i in range(n):
        s = loadState(rateInBytes, input_b[(
            i*rateInBytes):(i*rateInBytes + rateInBytes)], s)
        s = state_permute(s)

    rem : int = inputByteLen % rateInBytes
    last : uint8_t = input_b[(inputByteLen - rem):inputByteLen]
    lastBlock = bytes(array.create(rateInBytes, uint8(0)))
    lastBlock[0:rem] = last
    lastBlock[rem] = delimitedSuffix
    s = loadState(rateInBytes, lastBlock, s)

    if not(delimitedSuffix & uint8(0x80) == uint8(0)) and (rem == rateInBytes - 1):
        s = state_permute(s)

    nextBlock = bytes(array.create(rateInBytes, uint8(0)))
    nextBlock[rateInBytes - 1] = uint8(0x80)
    s = loadState(rateInBytes, nextBlock, s)
    s = state_permute(s)
    return s


@contract3(lambda s, rateInBytes, outputByteLen:
            0 < rateInBytes and rateInBytes <= 200,
           lambda s, rateInBytes, outputByteLen, res:
            array.length(res) == outputByteLen)
@typechecked
def squeeze(s: state_t,
            rateInBytes: nat_t,
            outputByteLen: size_nat_t) -> vlbytes_t:
    output = bytes(array.create(outputByteLen, uint8(0)))
    outBlocks : int = outputByteLen // rateInBytes
    for i in range(outBlocks):
        block : vlbytes_t = storeState(rateInBytes, s)
        output[(i*rateInBytes):(i*rateInBytes + rateInBytes)] = block
        s : state_t = state_permute(s)

    remOut : int = outputByteLen % rateInBytes
    outBlock : state_t = storeState(remOut, s)
    output[(outputByteLen - remOut):outputByteLen] = outBlock
    return output


@typechecked
def keccak(rate: size_nat_1600_t, capacity: size_nat_t, inputByteLen: size_nat_t,
           input_b: vlbytes_t, delimitedSuffix: uint8_t, outputByteLen: size_nat_t) -> vlbytes_t:
    rateInBytes : nat_t = nat(rate // 8)
    s = array.create(25, uint64(0))
    s = absorb(s, rateInBytes, inputByteLen, input_b, delimitedSuffix)
    output : vlbytes_t = squeeze(s, rateInBytes, outputByteLen)
    return output


@contract3(lambda inputByteLen, input_b, outputByteLen:
            array.length(input_b) == inputByteLen,
           lambda inputByteLen, input_b, outputByteLen, res:
            array.length(res) == outputByteLen)
@typechecked
def shake128(inputByteLen: size_nat_t,
             input_b: vlbytes_t,
             outputByteLen: size_nat_t) -> vlbytes_t:
    return keccak(1344, 256, inputByteLen, input_b, uint8(0x1F), outputByteLen)


@contract3(lambda inputByteLen, input_b, outputByteLen:
            array.length(input_b) == inputByteLen,
           lambda inputByteLen, input_b, outputByteLen, res:
            array.length(res) == outputByteLen)
@typechecked
def shake256(inputByteLen: size_nat_t,
             input_b: vlbytes_t,
             outputByteLen: size_nat_t) -> vlbytes_t:
    return keccak(1088, 512, inputByteLen, input_b, uint8(0x1F), outputByteLen)


@contract3(lambda inputByteLen, input_b:
            array.length(input_b) == inputByteLen,
           lambda inputByteLen, input_b, res:
            array.length(res) == 28)
@typechecked
def sha3_224(inputByteLen: size_nat_t,
             input_b: vlbytes_t) -> vlbytes_t:
    return keccak(1152, 448, inputByteLen, input_b, uint8(0x06), 28)


@contract3(lambda inputByteLen, input_b:
            array.length(input_b) == inputByteLen,
           lambda inputByteLen, input_b, res:
            array.length(res) == 32)
@typechecked
def sha3_256(inputByteLen: size_nat_t,
             input_b: vlbytes_t) -> vlbytes_t:
    return keccak(1088, 512, inputByteLen, input_b, uint8(0x06), 32)


@contract3(lambda inputByteLen, input_b:
            array.length(input_b) == inputByteLen,
           lambda inputByteLen, input_b, res:
            array.length(res) == 48)
@typechecked
def sha3_384(inputByteLen: size_nat_t,
             input_b: vlbytes_t) -> vlbytes_t:
    return keccak(832, 768, inputByteLen, input_b, uint8(0x06), 48)


@contract3(lambda inputByteLen, input_b:
            array.length(input_b) == inputByteLen,
           lambda inputByteLen, input_b, res:
            array.length(res) == 64)
@typechecked
def sha3_512(inputByteLen: size_nat_t,
             input_b: vlbytes_t) -> vlbytes_t:
    return keccak(576, 1024, inputByteLen, input_b, uint8(0x06), 64)
