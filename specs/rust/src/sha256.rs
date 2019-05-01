// ==== SPECLIB START ====

// This is also part of the byteorder crate.
fn bytes_to_words(block: [u8; BLOCKSIZE]) -> [u32; 16] {
    let mut r: [u32; 16] = [0; 16];
    for i in 0..16 {
        let j = i * 4;
        r[i] = (block[j] as u32) << 24
            | (block[j + 1] as u32) << 16
            | (block[j + 2] as u32) << 8
            | (block[j + 3] as u32);
    }
    r
}

struct blocks_t(Vec<[u8; BLOCKSIZE]>, [u8; BLOCKSIZE]);
fn split_blocks(msg: &Vec<u8>) -> blocks_t {
    let nblocks = msg.len() / BLOCKSIZE;
    let rem = msg.len() % BLOCKSIZE;
    let mut blocks: Vec<[u8; BLOCKSIZE]> = Vec::new();
    for i in 0..nblocks {
        let mut tmp = [0 as u8; BLOCKSIZE];
        tmp.copy_from_slice(&msg[i * BLOCKSIZE..(i + 1) * BLOCKSIZE]);
        blocks.push(tmp);
    }
    let mut last = [0 as u8; BLOCKSIZE];
    for i in 0..msg.len()-rem {
        last[i] = msg[msg.len()-rem+i];
    }
    // last.copy_from_slice(&msg[msg.len() - rem..msg.len()]);
    return blocks_t(blocks, last);
}

fn len_to_bytes(l: u64) -> [u8; LENSIZE] {
    let mut result: [u8; LENSIZE] = [0; LENSIZE];
    let mut len = l;
    for i in 0..LENSIZE {
        result[LENSIZE - i - 1] = len as u8;
        len = len / 256;
    }
    return result;
}

fn words_to_bytes(w: [u32; LENSIZE]) -> [u8; HASHSIZE] {
    let mut result: [u8; HASHSIZE] = [0; HASHSIZE];
    for i in 0..LENSIZE {
        result[i * 4] = (w[i] >> 24) as u8;
        result[i * 4 + 1] = (w[i] >> 16) as u8;
        result[i * 4 + 2] = (w[i] >> 8) as u8;
        result[i * 4 + 3] = w[i] as u8;
    }
    return result;
}
// ==== SPECLIB END ====

// i_range_t = range_t(0, 4)
// op_range_t = range_t(0, 1)

// Initializing types and constants
const BLOCKSIZE: usize = 64;
// block_t = bytes_t(blockSize)
const LENSIZE: usize = 8;
// len_t = uint64_t
// to_len : FunctionType = uint64
// len_to_bytes : FunctionType = bytes.from_uint64_be
// word_t = uint32_t
// to_word : FunctionType = uint32
// bytes_to_words : FunctionType = bytes.to_uint32s_be
// words_to_bytes : FunctionType = bytes.from_uint32s_be
const KSIZE: usize = 64;
// k_t = array_t(word_t,kSize)
// opTableType_t = array_t(int,12)
const OPTABLE: [u8; 12] = [2, 13, 22, 6, 11, 25, 7, 18, 3, 17, 19, 10];
const KTABLE: [u32; KSIZE] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

const HASHSIZE: usize = 32;
// hash_t = array_t(word_t,8)
// digest_t = bytes_t(hashSize)
// h0_t = bytes_t(8)
const H0: [u32; LENSIZE] = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
];

fn ch(x: u32, y: u32, z: u32) -> u32 {
    (x & y) ^ ((!x) & z)
}

fn maj(x: u32, y: u32, z: u32) -> u32 {
    (x & y) ^ ((x & z) ^ (y & z))
}

fn sigma(x: u32, i: usize, op: u8) -> u32 {
    // NOTE: usize needed for i here for indexing a slice
    let tmp: u32;
    if op == 0 {
        tmp = x >> OPTABLE[3 * i + 2]
    } else {
        tmp = x.rotate_right(OPTABLE[3 * i + 2] as u32) // uintn.rotate_right
    }
    x.rotate_right(OPTABLE[3 * i] as u32) ^ x.rotate_right(OPTABLE[3 * i + 1] as u32) ^ tmp
}

fn schedule(block: [u8; BLOCKSIZE]) -> [u32; KSIZE] {
    let b: [u32; 16] = bytes_to_words(block);
    let mut s: [u32; KSIZE] = [0; KSIZE];
    for i in 0..KSIZE {
        if i < 16 {
            s[i] = b[i]
        } else {
            let t16: u32 = s[i - 16];
            let t15: u32 = s[i - 15];
            let t7: u32 = s[i - 7];
            let t2: u32 = s[i - 2];
            let s1: u32 = sigma(t2, 3, 0);
            let s0: u32 = sigma(t15, 2, 0);
            s[i] = s1.overflowing_add(t7).0;
            s[i] = s[i].overflowing_add(s0).0;
            s[i] = s[i].overflowing_add(t16).0;
        }
    }
    return s;
}

fn shuffle(ws: [u32; KSIZE], hashi: [u32; LENSIZE]) -> [u32; LENSIZE] {
    let mut h: [u32; LENSIZE] = hashi;
    for i in 0..KSIZE {
        let a0: u32 = h[0];
        let b0: u32 = h[1];
        let c0: u32 = h[2];
        let d0: u32 = h[3];
        let e0: u32 = h[4];
        let f0: u32 = h[5];
        let g0: u32 = h[6];
        let h0: u32 = h[7];

        let t1: u32 = h0.overflowing_add(sigma(e0, 1, 1)).0;
        let t1 = t1.overflowing_add(ch(e0, f0, g0)).0;
        let t1 = t1.overflowing_add(KTABLE[i]).0;
        let t1 = t1.overflowing_add(ws[i]).0;
        let t2: u32 = sigma(a0, 0, 1).overflowing_add(maj(a0, b0, c0)).0;

        h[0] = t1.overflowing_add(t2).0;
        h[1] = a0;
        h[2] = b0;
        h[3] = c0;
        h[4] = d0.overflowing_add(t1).0;
        h[5] = e0;
        h[6] = f0;
        h[7] = g0;
    }
    return h;
}

fn compress(block: [u8; BLOCKSIZE], hIn: [u32; LENSIZE]) -> [u32; LENSIZE] {
    let s: [u32; KSIZE] = schedule(block);
    let mut h: [u32; LENSIZE] = shuffle(s, hIn);
    for i in 0..8 {
        h[i] = h[i].overflowing_add(hIn[i]).0;
    }
    return h;
}

fn sha256(msg: Vec<u8>) -> [u8; HASHSIZE] {
    let splitted: blocks_t = split_blocks(&msg);
    let blocks: Vec<[u8; BLOCKSIZE]> = splitted.0;
    let last: [u8; BLOCKSIZE] = splitted.1;
    let nblocks: usize = blocks.len();
    let mut h: [u32; LENSIZE] = H0;
    for i in 0..nblocks {
        h = compress(blocks[i], h);
    }
    let last_len: usize = last.len();
    let len_bits: u64 = (msg.len() * 8) as u64;
    let mut pad: [u8; 2 * BLOCKSIZE] = [0; 2 * BLOCKSIZE];
    for i in 0..last_len {
        pad[i] = last[i];
    }
    pad[last_len] = 0x80;
    let len_bits_bytes = len_to_bytes(len_bits);
    if last_len < BLOCKSIZE - LENSIZE {
        for i in 0..LENSIZE {
            pad[BLOCKSIZE - (LENSIZE - i)] = len_bits_bytes[i];
        }
        let mut tmp = [0 as u8; 64];
        tmp.copy_from_slice(&pad[0..BLOCKSIZE]);
        h = compress(tmp, h);
    } else {
        for i in 0..LENSIZE {
            pad[(2 * BLOCKSIZE) - (LENSIZE - i)] = len_bits_bytes[i];
        }
        let mut tmp = [0 as u8; 64];
        tmp.copy_from_slice(&pad[0..BLOCKSIZE]);
        h = compress(tmp, h);
        let mut tmp = [0 as u8; 64];
        tmp.copy_from_slice(&pad[BLOCKSIZE..2 * BLOCKSIZE]);
        h = compress(tmp, h);
    }
    let result: [u8; HASHSIZE] = words_to_bytes(h);
    return result;
}

fn main() {
    let b = vec![
        0x68,0x61,0x63,0x73,0x70,0x65,0x63,0x20,0x72,0x75,0x6c,0x65,0x73
    ];
    let hash = sha256(b);
    println!("result:   {:?}", hash);
    println!("expected: 0xb37db5ed72c97da3b2579537afbc3261ed3d5a56f57b3d8e5c1019ae35929964");
}
