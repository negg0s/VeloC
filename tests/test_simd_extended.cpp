// Test 512-bit Extended SIMD Vector Subsystem
#include "veloc_simd512.h"
#include <cassert>
#include <cstdio>
#include <cmath>

int main() {
    using namespace veloc::simd;

    printf("[*] Testing VeloC 512-bit (16-wide f32) SIMD Vectors...\n");

    alignas(64) f32 a_data[16];
    alignas(64) f32 b_data[16];
    alignas(64) f32 c_data[16];
    alignas(64) f32 out_data[16];

    for (int i = 0; i < 16; i++) {
        a_data[i] = (f32)(i + 1);
        b_data[i] = 2.0f;
        c_data[i] = 10.0f;
    }

    f32x16 va = f32x16::load(a_data);
    f32x16 vb = f32x16::load(b_data);
    f32x16 vc = f32x16::load(c_data);

    // FMA: (a * b) + c
    f32x16 res = f32x16::fmadd(va, vb, vc);
    f32x16::store(out_data, res);

    for (int i = 0; i < 16; i++) {
        f32 expected = (a_data[i] * 2.0f) + 10.0f;
        assert(std::fabs(out_data[i] - expected) < 1e-5f);
    }
    printf("  [PASS] 16-wide FMA lanes computed accurately.\n");

    // Horizontal sum
    f32 sum = f32x16::hsum(va); // 1 + 2 + ... + 16 = 16 * 17 / 2 = 136.0
    assert(std::fabs(sum - 136.0f) < 1e-5f);
    printf("  [PASS] Horizontal sum of 16-wide vector: %.1f (Expected 136.0)\n", sum);

    printf("[SUCCESS] 512-bit extended SIMD subsystem operational!\n");
    return 0;
}
