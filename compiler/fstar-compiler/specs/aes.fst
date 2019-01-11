(* Generated from hacspec module ../specs/aes.py *)
module aes
open Speclib
#reset-options "--z3rlimit 60"
let blocksize : int = 16

let block_t : Type0 = array_t uint8_t 16

let subblock_t : Type0 = (x:vlbytes_t{(array_length x) <=. blocksize})

let rowindex_t : Type0 = range_t 0 4

let expindex_t : Type0 = range_t 0 44

let word_t : Type0 = array_t uint8_t 4

let key_t : Type0 = array_t uint8_t 16

let nonce_t : Type0 = array_t uint8_t 12

let bytes_144_t : Type0 = array_t uint8_t 144

let bytes_176_t : Type0 = array_t uint8_t 176

let index_t : Type0 = range_t 0 16

let rotval_t : Type0 = range_t 1 32

let sbox_t : Type0 = array_t uint8_t 256

let indexes_t : Type0 = range_t 0 176

let state_t : Type0 = (bytes_176_t * block_t)

let size_nat_t : Type0 = range_t 0 4294967295

let sbox : sbox_t = array (array_createL [uint8 99; uint8 124; uint8 119; uint8 123; uint8 242; uint8 107; uint8 111; uint8 197; uint8 48; uint8 1; uint8 103; uint8 43; uint8 254; uint8 215; uint8 171; uint8 118; uint8 202; uint8 130; uint8 201; uint8 125; uint8 250; uint8 89; uint8 71; uint8 240; uint8 173; uint8 212; uint8 162; uint8 175; uint8 156; uint8 164; uint8 114; uint8 192; uint8 183; uint8 253; uint8 147; uint8 38; uint8 54; uint8 63; uint8 247; uint8 204; uint8 52; uint8 165; uint8 229; uint8 241; uint8 113; uint8 216; uint8 49; uint8 21; uint8 4; uint8 199; uint8 35; uint8 195; uint8 24; uint8 150; uint8 5; uint8 154; uint8 7; uint8 18; uint8 128; uint8 226; uint8 235; uint8 39; uint8 178; uint8 117; uint8 9; uint8 131; uint8 44; uint8 26; uint8 27; uint8 110; uint8 90; uint8 160; uint8 82; uint8 59; uint8 214; uint8 179; uint8 41; uint8 227; uint8 47; uint8 132; uint8 83; uint8 209; uint8 0; uint8 237; uint8 32; uint8 252; uint8 177; uint8 91; uint8 106; uint8 203; uint8 190; uint8 57; uint8 74; uint8 76; uint8 88; uint8 207; uint8 208; uint8 239; uint8 170; uint8 251; uint8 67; uint8 77; uint8 51; uint8 133; uint8 69; uint8 249; uint8 2; uint8 127; uint8 80; uint8 60; uint8 159; uint8 168; uint8 81; uint8 163; uint8 64; uint8 143; uint8 146; uint8 157; uint8 56; uint8 245; uint8 188; uint8 182; uint8 218; uint8 33; uint8 16; uint8 255; uint8 243; uint8 210; uint8 205; uint8 12; uint8 19; uint8 236; uint8 95; uint8 151; uint8 68; uint8 23; uint8 196; uint8 167; uint8 126; uint8 61; uint8 100; uint8 93; uint8 25; uint8 115; uint8 96; uint8 129; uint8 79; uint8 220; uint8 34; uint8 42; uint8 144; uint8 136; uint8 70; uint8 238; uint8 184; uint8 20; uint8 222; uint8 94; uint8 11; uint8 219; uint8 224; uint8 50; uint8 58; uint8 10; uint8 73; uint8 6; uint8 36; uint8 92; uint8 194; uint8 211; uint8 172; uint8 98; uint8 145; uint8 149; uint8 228; uint8 121; uint8 231; uint8 200; uint8 55; uint8 109; uint8 141; uint8 213; uint8 78; uint8 169; uint8 108; uint8 86; uint8 244; uint8 234; uint8 101; uint8 122; uint8 174; uint8 8; uint8 186; uint8 120; uint8 37; uint8 46; uint8 28; uint8 166; uint8 180; uint8 198; uint8 232; uint8 221; uint8 116; uint8 31; uint8 75; uint8 189; uint8 139; uint8 138; uint8 112; uint8 62; uint8 181; uint8 102; uint8 72; uint8 3; uint8 246; uint8 14; uint8 97; uint8 53; uint8 87; uint8 185; uint8 134; uint8 193; uint8 29; uint8 158; uint8 225; uint8 248; uint8 152; uint8 17; uint8 105; uint8 217; uint8 142; uint8 148; uint8 155; uint8 30; uint8 135; uint8 233; uint8 206; uint8 85; uint8 40; uint8 223; uint8 140; uint8 161; uint8 137; uint8 13; uint8 191; uint8 230; uint8 66; uint8 104; uint8 65; uint8 153; uint8 45; uint8 15; uint8 176; uint8 84; uint8 187; uint8 22])

let sub_byte (input : uint8_t) : uint8_t = 
sbox.[uintn_to_int input]

let subBytes (state : block_t) : block_t = 
let st = bytes (array_copy state) in 
let st = repeati 16 (fun i st -> st.[i] <- sub_byte state.[i]) st in 
st

let shiftRow (i : rowindex_t) (shift : rowindex_t) (state : block_t) : block_t = 
let temp0 = state.[i +. (4 *. (shift % 4))] in 
let temp1 = state.[i +. (4 *. ((shift +. 1) % 4))] in 
let temp2 = state.[i +. (4 *. ((shift +. 2) % 4))] in 
let temp3 = state.[i +. (4 *. ((shift +. 3) % 4))] in 
let out = bytes (array_copy state) in 
let out = out.[i] <- temp0 in 
let out = out.[i +. 4] <- temp1 in 
let out = out.[i +. 8] <- temp2 in 
let out = out.[i +. 12] <- temp3 in 
out

let shiftRows (state : block_t) : block_t = 
let state = shiftRow 1 1 state in 
let state = shiftRow 2 2 state in 
let state = shiftRow 3 3 state in 
state

let xtime (x : uint8_t) : uint8_t = 
let x1 = x <<. 1 in 
let x7 = x >>. 7 in 
let x71 = x7 &. (uint8 1) in 
let x711b = x71 *. (uint8 27) in 
x1 ^. x711b

let mixColumn (c : rowindex_t) (state : block_t) : block_t = 
let i0 = 4 *. c in 
let s0 = state.[i0] in 
let s1 = state.[i0 +. 1] in 
let s2 = state.[i0 +. 2] in 
let s3 = state.[i0 +. 3] in 
let st = bytes (array_copy state) in 
let tmp = ((s0 ^. s1) ^. s2) ^. s3 in 
let st = st.[i0] <- (s0 ^. tmp) ^. (xtime (s0 ^. s1)) in 
let st = st.[i0 +. 1] <- (s1 ^. tmp) ^. (xtime (s1 ^. s2)) in 
let st = st.[i0 +. 2] <- (s2 ^. tmp) ^. (xtime (s2 ^. s3)) in 
let st = st.[i0 +. 3] <- (s3 ^. tmp) ^. (xtime (s3 ^. s0)) in 
st

let mixColumns (state : block_t) : block_t = 
let state = mixColumn 0 state in 
let state = mixColumn 1 state in 
let state = mixColumn 2 state in 
let state = mixColumn 3 state in 
state

let xor_block (b : block_t) (b1 : block_t) : block_t = 
let out = bytes (array_copy b) in 
let out = repeati 16 (fun i out -> out.[i] <- b.[i] ^. b1.[i]) out in 
out

let addRoundKey (state : block_t) (key : block_t) : block_t = 
xor_block state key

let aes_enc (state : block_t) (round_key : block_t) : block_t = 
let state = subBytes state in 
let state = shiftRows state in 
let state = mixColumns state in 
let state = addRoundKey state round_key in 
state

let aes_enc_last (state : block_t) (round_key : block_t) : block_t = 
let state = subBytes state in 
let state = shiftRows state in 
let state = addRoundKey state round_key in 
state

let rounds_inside (key : bytes_144_t) (i : indexes_t) : block_t = 
array_slice key (i *. 16) ((i *. 16) +. 16)

let rounds (state : block_t) (key : bytes_144_t) : block_t = 
let out = bytes (array_copy state) in 
let out = repeati 9 (fun i out -> aes_enc out (rounds_inside key i)) out in 
out

let block_cipher (input : block_t) (key : bytes_176_t) : block_t = 
let state = bytes (array_copy input) in 
let k0 = array_slice key 0 16 in 
let k = array_slice key 16 (op_Multiply 10 16) in 
let kn = array_slice key (op_Multiply 10 16) (op_Multiply 11 16) in 
let state = addRoundKey state k0 in 
let state = rounds state k in 
let state = aes_enc_last state kn in 
state

let rcon_l_t : Type0 = array_t uint8_t 11

let rcon_l : rcon_l_t = array (array_createL [uint8 141; uint8 1; uint8 2; uint8 4; uint8 8; uint8 16; uint8 32; uint8 64; uint8 128; uint8 27; uint8 54])

let aes_keygen_assist_ (rcon : uint8_t) (s : block_t) : block_t = 
let st = array_create blocksize (uint8 0) in 
let st = st.[0] <- sub_byte s.[4] in 
let st = st.[1] <- sub_byte s.[5] in 
let st = st.[2] <- sub_byte s.[6] in 
let st = st.[3] <- sub_byte s.[7] in 
let st = st.[4] <- rcon ^. (sub_byte s.[5]) in 
let st = st.[5] <- sub_byte s.[6] in 
let st = st.[6] <- sub_byte s.[7] in 
let st = st.[7] <- sub_byte s.[4] in 
let st = st.[8] <- sub_byte s.[12] in 
let st = st.[9] <- sub_byte s.[13] in 
let st = st.[10] <- sub_byte s.[14] in 
let st = st.[11] <- sub_byte s.[15] in 
let st = st.[12] <- rcon ^. (sub_byte s.[13]) in 
let st = st.[13] <- sub_byte s.[14] in 
let st = st.[14] <- sub_byte s.[15] in 
let st = st.[15] <- sub_byte s.[12] in 
st

let aes128_keygen_assist (rcon : uint8_t) (s : block_t) : block_t = 
let st = aes_keygen_assist_ rcon s in 
let st = array_update_slice st 8 12 (array_slice st 12 16) in 
let st = array_update_slice st 0 8 (array_slice st 8 16) in 
st

let key_expansion_step (p : block_t) (assist : block_t) : block_t = 
let p0 = array_create 16 (uint8 0) in 
let pTemp = array_copy p0 in 
let k = array_copy p in 
let pTemp = array_update_slice pTemp 4 12 (array_slice k 0 12) in 
let k = xor_block k pTemp in 
let pTemp = array_update_slice pTemp 4 12 (array_slice k 0 12) in 
let k = xor_block k pTemp in 
let pTemp = array_update_slice pTemp 4 12 (array_slice k 0 12) in 
let k = xor_block k pTemp in 
xor_block k assist

let get_block (f : bytes_176_t) (a : index_t) (b : index_t) : block_t = 
array_slice f a b

let get_rcon (rcon_l : rcon_l_t) (index : index_t) : uint8_t = 
rcon_l.[index]

let aes128_key_expansion_step (kex : bytes_176_t) (i : nat_t) : bytes_176_t = 
let p = get_block kex (i *. 16) ((i *. 16) +. 16) in 
let a = aes128_keygen_assist (get_rcon rcon_l (i +. 1)) p in 
let n = key_expansion_step p a in 
let kex = array_update_slice kex (op_Multiply (op_Addition i 1) 16) (op_Multiply (op_Addition (op_Addition i 1) 16) 16) (n) in 
kex

let aes128_key_expansion (key : block_t) : bytes_176_t = 
let key_ex = array_create 176 (uint8 0) in 
let key_ex = repeati 16 (fun i key_ex -> key_ex.[i] <- key.[i]) key_ex in 
let key_ex = repeati 10 (fun i key_ex -> aes128_key_expansion_step key_ex i) key_ex in 
key_ex

let aes128_encrypt_block_ (k : block_t) (m : block_t) : block_t = 
let key_ex = aes128_key_expansion k in 
block_cipher m key_ex

let aes_init (k : block_t) (n_len : size_nat_t) (n : block_t) : state_t = 
let inp = array_create 16 (uint8 0) in 
let inp = repeati n_len (fun i inp -> inp.[i] <- n.[i]) inp in 
let key_ex = aes128_key_expansion k in 
(key_ex,inp)

let aes_set_counter (st : state_t) (c : size_nat_t) : state_t = 
let cby = bytes_from_nat_be c 4 in 
let (kex,bl) = st in 
let bl = array_update_slice bl 12 16 (cby) in 
(kex,bl)

let aes_key_block (st : state_t) : block_t = 
let (kex,bl) = st in 
block_cipher bl kex

let aes_key_block0 (k : block_t) (n_len : size_nat_t) (n : subblock_t) : block_t = 
aes_key_block (aes_init k n_len n)

let aes_key_block1 (k : block_t) (n_len : size_nat_t) (n : subblock_t) : block_t = 
let st = aes_init k n_len n in 
let st = aes_set_counter st 1 in 
aes_key_block st

let aes_encrypt_block (st0 : state_t) (ctr0 : size_nat_t) (b : block_t) : block_t = 
let st = aes_set_counter st0 ctr0 in 
let kb = aes_key_block st in 
let kb = repeati 16 (fun i kb -> kb.[i] <- kb.[i] ^. b.[i]) kb in 
kb

let aes_encrypt_last (st0 : state_t) (ctr0 : size_nat_t) (last : block_t) : block_t = 
let cip = aes_encrypt_block st0 ctr0 last in 
cip

let incr_counter (c : size_nat_t) (incr : size_nat_t) : size_nat_t = 
c +. incr

let aes128_encrypt_bytes (key : block_t) (nonce : nonce_t) (c : size_nat_t) (msg : vlbytes_t) : vlbytes_t = 
let (blocks,last) = array_split_blocks msg blocksize in 
let keyblock = array_create blocksize (uint8 0) in 
let last_block = array_create blocksize (uint8 0) in 
let st0 = aes_init key (array_length nonce) nonce in 
let (blocks,c) = repeati (array_length blocks) (fun i (blocks,c) -> let blocks = blocks.[i] <- aes_encrypt_block st0 c blocks.[i] in 
let c = incr_counter c 1 in 
(blocks,c)) (blocks,c) in 
let last_block = array_update_slice last_block 0 (array_length last) (last) in 
let last_block = aes_encrypt_last st0 c last_block in 
let last = array_slice last_block 0 (array_length last) in 
array_concat_blocks blocks last
