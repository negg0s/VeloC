# RFC-0001: First-Class Hardware SIMD Intrinsics & Dispatch

- **Feature Name**: `simd_intrinsics`
- **Start Date**: 2026-10-15
- **Status**: Accepted & Implemented

---

## 1. Summary
Provides portable and high-performance native SIMD vector primitives (`Vec3`, `f32x8`, `i32x8`, `simd_add`, `simd_mul`, `simd_fma`) with automatic AVX2/AVX-512 hardware feature detection and dynamic runtime dispatch.

## 2. Motivation
VeloC is designed for systems performance. Requiring developers to write manual inline assembly or raw C intrinsics hinders readability and cross-platform portability. First-class SIMD types allow the compiler to auto-vectorize and dispatch optimal hardware instructions without overhead.

## 3. Guide-Level Explanation
```veloc
import veloc.simd;

fn vector_dot(a: &[f32], b: &[f32], n: usize) -> f32 {
    return simd_dot_product(a, b, n);
}
```

## 4. Implementation
Mapped to native Clang/LLVM vector extensions (`__vector_size__`) and Intel intrinsic headers (`<immintrin.h>`). In fast mode, bounds checking is eliminated and FMA instructions are emitted.
