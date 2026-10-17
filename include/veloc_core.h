#ifndef VELOC_CORE_H
#define VELOC_CORE_H

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <immintrin.h>

#ifdef _WIN32
#define VELOC_RESTRICT __restrict
#define VELOC_INLINE __forceinline
#else
#define VELOC_RESTRICT __restrict__
#define VELOC_INLINE inline __attribute__((always_inline))
#endif

#define noalias VELOC_RESTRICT
#define pub

// Fast fixed-size integer and floating point types
typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;

typedef int8_t   i8;
typedef int16_t  i16;
typedef int32_t  i32;
typedef int64_t  i64;

typedef float    f32;
typedef double   f64;
typedef size_t   usize;
typedef ptrdiff_t isize;

// AVX2 256-bit SIMD Vector Types
typedef __m256 f32x8;
typedef __m256i i32x8;

static VELOC_INLINE f32x8 f32x8_set1(f32 val) { return _mm256_set1_ps(val); }
static VELOC_INLINE f32x8 f32x8_load(const f32* ptr) { return _mm256_loadu_ps(ptr); }
static VELOC_INLINE f32x8 f32x8_load_aligned(const f32* ptr) { return _mm256_load_ps(ptr); }
static VELOC_INLINE void f32x8_store(f32* ptr, f32x8 vec) { _mm256_storeu_ps(ptr, vec); }
static VELOC_INLINE void f32x8_store_aligned(f32* ptr, f32x8 vec) { _mm256_store_ps(ptr, vec); }

// SIMD 3D Vector
struct alignas(16) Vec3 {
    f32 x, y, z, _pad;

    Vec3() : x(0), y(0), z(0), _pad(0) {}
    Vec3(f32 vx, f32 vy, f32 vz) : x(vx), y(vy), z(vz), _pad(0) {}

    VELOC_INLINE Vec3 operator+(const Vec3& o) const {
        __m128 a = _mm_load_ps(&x);
        __m128 b = _mm_load_ps(&o.x);
        Vec3 r;
        _mm_store_ps(&r.x, _mm_add_ps(a, b));
        return r;
    }

    VELOC_INLINE Vec3 operator-(const Vec3& o) const {
        __m128 a = _mm_load_ps(&x);
        __m128 b = _mm_load_ps(&o.x);
        Vec3 r;
        _mm_store_ps(&r.x, _mm_sub_ps(a, b));
        return r;
    }

    VELOC_INLINE Vec3 operator*(f32 s) const {
        __m128 a = _mm_load_ps(&x);
        __m128 b = _mm_set1_ps(s);
        Vec3 r;
        _mm_store_ps(&r.x, _mm_mul_ps(a, b));
        return r;
    }

    VELOC_INLINE f32 dot(const Vec3& o) const {
        return x * o.x + y * o.y + z * o.z;
    }
};

namespace veloc {
    static inline void println(const char* val) { printf("%s\n", val); }
    static inline void println(int val) { printf("%d\n", val); }
    static inline void println(unsigned int val) { printf("%u\n", val); }
    static inline void println(long long val) { printf("%lld\n", val); }
    static inline void println(unsigned long long val) { printf("%llu\n", val); }
    static inline void println(double val) { printf("%f\n", val); }
    static inline void println() { printf("\n"); }

    static inline void print(const char* val) { printf("%s", val); }
    static inline void print(int val) { printf("%d", val); }
}

using veloc::println;
using veloc::print;

#endif // VELOC_CORE_H
