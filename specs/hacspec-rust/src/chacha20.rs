
#[derive(Clone, Debug)]
pub struct State {
    pub v: [u32; 16],
}

fn rotate_left(x: u32, s: u32) -> u32 {
    x << s | x >> (32 - s)
}

fn line(a: u16, b: u16, d: u16, s: u32, m: State) -> State {
    let mut m = m.clone();
    m.v[a as usize] = ((m.v[a as usize] as u64 + m.v[b as usize] as u64) & 0xFFFFFFFF) as u32;
    m.v[d as usize] = rotate_left(m.v[d as usize] ^ m.v[a as usize], s);
    m
}

pub fn quarter_round(a: u16, b: u16, c: u16, d: u16, m: State) -> State {
    let mut m = m.clone();
    m = line(a, b, d, 16, m);
    m = line(c, d, b, 12, m);
    m = line(a, b, d,  8, m);
    m = line(c, d, b,  7, m);
    m
}

pub fn inner_block(m: State) -> State {
    let mut m = m.clone();
    m = quarter_round(0, 4,  8, 12, m);
    m = quarter_round(1, 5,  9, 13, m);
    m = quarter_round(2, 6, 10, 14, m);
    m = quarter_round(3, 7, 11, 15, m);

    m = quarter_round(0, 5, 10, 15, m);
    m = quarter_round(1, 6, 11, 12, m);
    m = quarter_round(2, 7,  8, 13, m);
    m = quarter_round(3, 4,  9, 14, m);
    m
}

fn from_bytes_le(x: &[u8]) -> u32 {
    x[0] as u32 | (x[1] as u32) << 8 | (x[2] as u32) << 16 | (x[3] as u32) << 24
}

pub fn chacha20(k: &[u8; 32], counter: u32, nonce: &[u8; 12]) -> State {
    let st = State{
        v: [ 0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
             from_bytes_le(&k[0..4]), from_bytes_le(&k[4..8]),
             from_bytes_le(&k[8..12]), from_bytes_le(&k[12..16]),
             from_bytes_le(&k[16..20]), from_bytes_le(&k[20..24]),
             from_bytes_le(&k[24..28]), from_bytes_le(&k[28..32]),
             counter,
             from_bytes_le(&nonce[0..4]), from_bytes_le(&nonce[4..8]),
             from_bytes_le(&nonce[8..12])]
    };
    let mut working_state = st.clone();
    for _ in 1..11 {
        working_state = inner_block(working_state);
    }
    let mut st_out = st;
    for i in 0..16 {
        st_out.v[i] = ((working_state.v[i] as u64 + st_out.v[i] as u64) & 0xFFFFFFFF) as u32;
    }
    st_out
}
