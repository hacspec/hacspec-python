extern crate libc;

// Speclib implementation in Rust... because it's faster.
static MOD32: u64 = 1 << 32;

#[no_mangle]
pub extern fn ceil(x: libc::c_float) -> libc::c_int {
    x.ceil() as libc::c_int
}

// TODO: make operations check overflows?
#[no_mangle]
pub extern fn add32(x: libc::c_uint, y: libc::c_uint) -> libc::c_uint {
    x.wrapping_add(y)
}

#[no_mangle]
pub extern fn sub32(x: libc::c_uint, y: libc::c_uint) -> libc::c_uint {
    (MOD32 + x as u64 - y as u64) as libc::c_uint
}

#[no_mangle]
pub extern fn mul32(x: libc::c_uint, y: libc::c_uint) -> libc::c_uint {
    x * y
}

#[no_mangle]
pub extern fn pow32(x: libc::c_uint, y: libc::c_uint) -> libc::c_uint {
    x.pow(y)
}

#[no_mangle]
pub extern fn lshift32(x: libc::c_uint, y: libc::c_int) -> libc::c_uint {
    x << y
}

#[no_mangle]
pub extern fn rshift32(x: libc::c_uint, y: libc::c_int) -> libc::c_uint {
    x >> y
}

#[no_mangle]
pub extern fn rotate_left32(x: libc::c_uint, y: libc::c_int) -> libc::c_uint {
    (x << y) | (x >> (32 - y))
}

#[no_mangle]
pub extern fn rotate_right32(x: libc::c_uint, y: libc::c_int) -> libc::c_uint {
    (x >> y) | (x << (32 - y))
}
