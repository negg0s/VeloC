# Rust Interop (C-ABI) Guide for VeloC

VeloC is designed from first principles with zero-overhead C-ABI compatibility (`extern "C"`). This allows seamless, bidirectional interoperation between Rust and VeloC without wrapper overhead or runtime garbage collection friction.

---

## 1. Calling VeloC from Rust

### 1.1 VeloC Shared Library (`libveloc_math.vc`)

```veloc
#[no_mangle]
pub extern "C" fn veloc_vector_dot(a: *const f32, b: *const f32, len: usize) -> f32 {
    let mut sum: f32 = 0.0;
    // VeloC AVX2/SIMD auto-vectorizer applies here
    for i in 0..len {
        sum += a[i] * b[i];
    }
    return sum;
}
```

Compile with:
```bash
veloc build --lib --emit-header -o libveloc_math.dll libveloc_math.vc
```

### 1.2 Rust FFI Bindings (`src/lib.rs` / `build.rs`)

**Cargo.toml**:
```toml
[package]
name = "veloc-rust-demo"
version = "0.1.0"
edition = "2021"

[build-dependencies]
# Optional: bindgen if generating bindings automatically
```

**build.rs**:
```rust
fn main() {
    println!("cargo:rustc-link-search=native=.");
    println!("cargo:rustc-link-lib=dylib=veloc_math");
}
```

**src/main.rs**:
```rust
use std::os::raw::c_float;

extern "C" {
    fn veloc_vector_dot(a: *const c_float, b: *const c_float, len: usize) -> c_float;
}

fn main() {
    let a: Vec<f32> = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0];
    let b: Vec<f32> = vec![0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5];

    let result = unsafe {
        veloc_vector_dot(a.as_ptr(), b.as_ptr(), a.len())
    };

    println!("Dot product computed by VeloC: {}", result);
}
```

---

## 2. Calling Rust from VeloC

### 2.1 Rust Shared Library (`Cargo.toml`)

```toml
[package]
name = "rust_hasher"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]
```

**src/lib.rs**:
```rust
#[no_mangle]
pub extern "C" fn rust_fast_hash(data: *const u8, len: usize) -> u64 {
    let slice = unsafe { std::slice::from_raw_parts(data, len) };
    let mut h: u64 = 0xcbf29ce484222325;
    for &b in slice {
        h ^= b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}
```

Build the Rust cdylib:
```bash
cargo build --release
```

### 2.2 VeloC Consumer (`main.vc`)

```veloc-ffi
extern "C" {
    fn rust_fast_hash(data: *const u8, len: usize) -> u64;
}

fn main() {
    let text = "Hello from VeloC to Rust!";
    let hash = unsafe { rust_fast_hash(text.ptr, text.len) };
    println("Rust FNV-1a hash: 0x{:016x}", hash);
}
```

---

## 3. ABI Data Types & Conventions

| VeloC Type | Rust Equivalent | C Equivalent | Notes |
|---|---|---|---|
| `i8`, `i16`, `i32`, `i64` | `i8`, `i16`, `i32`, `i64` | `int8_t`, `int16_t`, `int32_t`, `int64_t` | Exact match |
| `u8`, `u16`, `u32`, `u64` | `u8`, `u16`, `u32`, `u64` | `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t` | Exact match |
| `f32`, `f64` | `f32`, `f64` | `float`, `double` | IEEE-754 binary32/binary64 |
| `bool` | `bool` | `bool` / `uint8_t` | Guaranteed 1 byte |
| `*const T`, `*mut T` | `*const T`, `*mut T` | `const T*`, `T*` | Raw pointers |
| `[T; N]` | `[T; N]` | `T[N]` | Contiguous array |
| `#[repr(C)] struct S` | `#[repr(C)] struct S` | `struct S` | Identical padding/alignment |

### Zero-Copy Memory Sharing
- VeloC `Arena` allocators can hand memory buffers directly to Rust slices using `std::slice::from_raw_parts` without cloning.
- Rust `Vec::into_raw_parts` pointers can be consumed and freed in VeloC when using standard `malloc`/`free`.
