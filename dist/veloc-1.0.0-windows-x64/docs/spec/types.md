# VeloC Type System Specification

## 1. Type Taxonomy

### RULE-TYPE-001: Integer Types
VeloC defines fixed-width two's complement integer types with explicit signedness and bit-widths:
- Signed integers: `i8`, `i16`, `i32`, `i64`
- Unsigned integers: `u8`, `u16`, `u32`, `u64`, `usize` (pointer-sized unsigned integer, 32-bit on x86, 64-bit on x86-64)
- Size guarantee: `sizeof(T)` is exactly `bits/8` bytes.

### RULE-TYPE-002: Floating-Point Types
IEEE-754 standard floating-point types:
- `f32`: 32-bit single precision (binary32)
- `f64`: 64-bit double precision (binary64)

### RULE-TYPE-003: Boolean and Character Types
- `bool`: 1-byte logical value (`true` = 1, `false` = 0).
- `char`: 1-byte ASCII / UTF-8 code unit.
- `void`: 0-sized unit / return type.

### RULE-TYPE-004: Pointers and Slices
- Raw pointers: `T*` represents an unmanaged memory address.
- Restricted pointers: `T* noalias` guarantees non-aliasing for SIMD vectorizer.
- Slices: `Slice<T>` represents a non-owning `(T* ptr, usize len)` pair with mandatory O(1) bounds-checking in safe mode.

### RULE-TYPE-005: Algebraic Data Types (Option & Result)
- `Option<T>`: Represents either `Some(val)` or `None`.
- `Result<T, E>`: Represents either `Ok(val)` or `Err(err)`.
- Operations:
  - `opt!`: postfix non-null / non-empty unwrap. Panics on `None`.
  - `res?`: postfix try error propagation operator. Unwraps `Ok(val)` or returns early with `Err(e)`.

### RULE-TYPE-006: Struct-of-Arrays (SoA)
- Declared via `soa struct Name { type field; ... }`.
- Automatically lowered into aligned parallel arrays with 32-byte memory boundaries for AVX2 streaming.

### RULE-TYPE-007: Explicit Type Coercion (`as`)
- No implicit lossy conversions exist between distinct numeric types in pure VeloC expressions.
- Conversions must be stated explicitly via `expr as TargetType`.
- Integer-to-float, float-to-integer (truncating), and integer widening/narrowing are defined operations.
