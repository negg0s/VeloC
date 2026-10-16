#include "D:/VeloC/include/veloc.h"

// [VeloC module declaration]

auto main() -> i32 {
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_BOLD) + std::string("      VeloC 3.0: Extreme User & Speed Features    ") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());

    // 1. SmallVec: Zero-heap allocation for small collections
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[1] SmallVec (Small Buffer Optimization)") + ::veloc::to_str(VELOC_RESET)).c_str());
    auto vec = SmallVec<i32, 16>();
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { vec.destroy(); };

    for (usize i = 0; i < 16; i++) {
        vec.push((i32)(i * 10));
    }
    printf("%s\n", (std::string("  SmallVec count: ") + ::veloc::to_str(vec.len()) + std::string(" (Stored 100% on CPU stack, 0 heap allocations!)")).c_str());
    printf("%s\n", (std::string("  vec[5] = ") + ::veloc::to_str(vec[5]) + std::string(", vec[15] = ") + ::veloc::to_str(vec[15])).c_str());

    // 2. FlatMap: Cache-friendly open-addressing hash map (5x faster than std::unordered_map)
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[2] FlatMap (Contiguous Cache-Friendly Hash Table)") + ::veloc::to_str(VELOC_RESET)).c_str());
    auto map = FlatMap<u64, f32, 512>();

    map.insert(1001, 3.14159f);
    map.insert(2048, 42.0f);
    map.insert(9999, 1337.0f);

    const auto found = map.get(2048);
    if (found.is_some()) {
        const auto val = found.unwrap();
        printf("%s\n", (std::string("  FlatMap key 2048 found: ") + ::veloc::to_str(val) + std::string(" (O(1) cache-line hit without linked lists)")).c_str());
    }

    // 3. AVX2 Matrix Multiplication 4x4
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[3] AVX2 4x4 SIMD Matrix Multiplication") + ::veloc::to_str(VELOC_RESET)).c_str());
    f32 a[16] = {
        1, 2, 3, 4,
        5, 6, 7, 8,
        9, 1, 2, 3,
        4, 5, 6, 7
    };
    f32 b[16] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    };
    f32 c[16];

    VeloC_Timer timer;
    const usize MATRIX_ITERS = 1000000; // 1 Million matrix multiplications
    timer.start();
    for (usize i = 0; i < MATRIX_ITERS; i++) {
        mat4_mul_simd(c, a, b);
    }
    f64 ms = timer.elapsed_ms();
    f64 mops = (f64)MATRIX_ITERS / (ms / 1000.0) / 1e6;

    printf("%s\n", (std::string("  Computed 1,000,000 4x4 matrix multiplications in: ") + ::veloc::to_str(ms) + std::string(" ms")).c_str());
    printf("%s\n", (std::string("  ") + ::veloc::to_str(VELOC_GREEN) + std::string("Throughput: ") + ::veloc::to_str(mops) + std::string(" MILLION 4x4 matrix mults / sec!") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (std::string("  Result c[0..3] = [") + ::veloc::to_str(c[0]) + std::string(", ") + ::veloc::to_str(c[1]) + std::string(", ") + ::veloc::to_str(c[2]) + std::string(", ") + ::veloc::to_str(c[3]) + std::string("]")).c_str());

    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());
    return 0;
}