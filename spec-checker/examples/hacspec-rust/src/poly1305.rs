extern crate num;
use poly1305::num::bigint::BigUint;
use poly1305::num::bigint::ToBigUint;
use poly1305::num::pow;
use poly1305::num::zero;
use poly1305::num::traits::Num;

macro_rules! p1305 {
    () => (pow(2.to_biguint().unwrap(), 130) - 5.to_biguint().unwrap());
}

fn fadd(a: &BigUint, b: &BigUint) -> BigUint {
    (a + b) % p1305!()
}

fn fmul(a: &BigUint, b: &BigUint) -> BigUint {
    (a * b) % p1305!()
}

fn encode(block: &[u8]) -> BigUint {
    let welem = BigUint::from_bytes_le(block);
    let lelem = pow(2.to_biguint().unwrap(), 8 * block.len());
    fadd(&lelem, &welem)
}

fn encode_r(r: &[u8]) -> BigUint {
    let ruint = BigUint::from_bytes_le(r);
    let mask: BigUint = BigUint::from_str_radix("0ffffffc0ffffffc0ffffffc0fffffff", 16).unwrap();
    ruint & mask
}

const BLOCKSIZE: usize = 16;

pub fn poly1305(msg: &[u8], key: &[u8; 32]) -> Vec<u8> {
    let mut acc: BigUint = zero();
    let num_blocks = (msg.len() as f32 / 16 as f32).ceil() as usize;
    let relem = encode_r(&key[0..BLOCKSIZE]);
    for i in 0..num_blocks {
        let j = 16*i;
        let k = msg.len().min(j + 16);
        acc = fmul(&fadd(&acc, &encode(&msg[j..k])), &relem);
    }
    let selem = BigUint::from_bytes_le(&key[BLOCKSIZE..2*BLOCKSIZE]);
    let n = acc + selem;
    let mut mac = n.to_bytes_le();
    while mac.len() > 16 {
        mac.pop();
    }
    mac
}
