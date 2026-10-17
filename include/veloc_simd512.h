// VeloC 512-bit Extended SIMD (AVX-512) and ARM NEON Vector Subsystem
// Provides f32x16, i32x16, and f64x8 registers with dual-AVX2 fallback
#pragma once

#include "veloc.h"
#include <immintrin.h>
#include <cstdio>
#include <cmath>

#if defined(__ARM_NEON) || defined(__aarch64__)
#include <arm_neon.h>
#endif

namespace veloc {
namespace simd {

// ============================================================================
// 1. 512-Bit Single Precision Float Vector (16x f32)
// ============================================================================
#if defined(__AVX512F__)
typedef __m512 f32x16_raw;
#else
// Dual-AVX2 fallback emulation
struct f32x16_raw {
    f32x8 lo;
    f32x8 hi;
};
#endif

struct f32x16 {
    f32x16_raw v;

    static VELOC_INLINE f32x16 set1(f32 val) {
        f32x16 r;
#if defined(__AVX512F__)
        r.v = _mm512_set1_ps(val);
#else
        r.v.lo = f32x8_set1(val);
        r.v.hi = f32x8_set1(val);
#endif
        return r;
    }

    static VELOC_INLINE f32x16 load(const f32* ptr) {
        f32x16 r;
#if defined(__AVX512F__)
        r.v = _mm512_loadu_ps(ptr);
#else
        r.v.lo = f32x8_load(ptr);
        r.v.hi = f32x8_load(ptr + 8);
#endif
        return r;
    }

    static VELOC_INLINE void store(f32* ptr, f32x16 vec) {
#if defined(__AVX512F__)
        _mm512_storeu_ps(ptr, vec.v);
#else
        f32x8_store(ptr, vec.v.lo);
        f32x8_store(ptr + 8, vec.v.hi);
#endif
    }

    static VELOC_INLINE f32x16 add(f32x16 a, f32x16 b) {
        f32x16 r;
#if defined(__AVX512F__)
        r.v = _mm512_add_ps(a.v, b.v);
#else
        r.v.lo = _mm256_add_ps(a.v.lo, b.v.lo);
        r.v.hi = _mm256_add_ps(a.v.hi, b.v.hi);
#endif
        return r;
    }

    static VELOC_INLINE f32x16 mul(f32x16 a, f32x16 b) {
        f32x16 r;
#if defined(__AVX512F__)
        r.v = _mm512_mul_ps(a.v, b.v);
#else
        r.v.lo = _mm256_mul_ps(a.v.lo, b.v.lo);
        r.v.hi = _mm256_mul_ps(a.v.hi, b.v.hi);
#endif
        return r;
    }

    static VELOC_INLINE f32x16 fmadd(f32x16 a, f32x16 b, f32x16 c) {
        f32x16 r;
#if defined(__AVX512F__)
        r.v = _mm512_fmadd_ps(a.v, b.v, c.v);
#else
        r.v.lo = f32x8_fmadd(a.v.lo, b.v.lo, c.v.lo);
        r.v.hi = f32x8_fmadd(a.v.hi, b.v.hi, c.v.hi);
#endif
        return r;
    }

    static VELOC_INLINE f32 hsum(f32x16 vec) {
#if defined(__AVX512F__)
        return _mm512_reduce_add_ps(vec.v);
#else
        return f32x8_hsum(vec.v.lo) + f32x8_hsum(vec.v.hi);
#endif
    }
};

// ============================================================================
// 2. ARM NEON 128-bit Vector Abstraction
// ============================================================================
#if defined(__ARM_NEON) || defined(__aarch64__)
struct neon_f32x4 {
    float32x4_t v;
    static VELOC_INLINE neon_f32x4 set1(f32 val) { neon_f32x4 r; r.v = vdupq_n_f32(val); return r; }
    static VELOC_INLINE neon_f32x4 load(const f32* ptr) { neon_f32x4 r; r.v = vld1q_f32(ptr); return r; }
    static VELOC_INLINE void store(f32* ptr, neon_f32x4 vec) { vst1q_f32(ptr, vec.v); }
    static VELOC_INLINE neon_f32x4 add(neon_f32x4 a, neon_f32x4 b) { neon_f32x4 r; r.v = vaddq_f32(a.v, b.v); return r; }
    static VELOC_INLINE neon_f32x4 mul(neon_f32x4 a, neon_f32x4 b) { neon_f32x4 r; r.v = vmulq_f32(a.v, b.v); return r; }
    static VELOC_INLINE f32 hsum(neon_f32x4 vec) { return vaddvq_f32(vec.v); }
};
#endif

} // namespace simd
} // namespace veloc
