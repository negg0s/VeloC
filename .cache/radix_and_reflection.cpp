#include "D:/VeloC/include/veloc.h"

// ============================================================================
// VeloC 4.0: Radix Sort, Enum Reflection, SIMD Min/Max, and Fast Trig
// ============================================================================
#include <algorithm>
#include <math.h>

veloc_enum(PlayerState, Idle, Running, Jumping, Attacking, Dead);

int main() {
    printf("===============================================================\n");
    printf("      VeloC 4.0: Advanced Systems & Extreme Algorithms         \n");
    printf("===============================================================\n");

    // 1. Zero-Cost Enum Reflection (Reddit #1 Wishlist Item for 30 years)
    printf("1. Zero-Cost Enum Reflection:\n");
    const auto state = PlayerState::Attacking;
    printf("%s\n", (std::string("   Player state: ") + ::veloc::to_str(state)).c_str());
    const auto next_state = PlayerState::Running;
    printf("%s\n", (std::string("   Next state:   ") + ::veloc::to_str(next_state)).c_str());

    // 2. Python/Rust-like Range Loop: for (const auto i : range(...))
    printf("\n2. Range-based Iteration (Zero Boilerplate):\n");
    printf("%s", "   Evens up to 10: ");
    for (const auto i : range(0, 10, 2)) {
        printf("%lld ", (long long)i);
    }
    printf("\n");

    // 3. Fast Trigonometric Polynomial Approximation (fast_sin vs sinf)
    printf("\n3. Ultra-Fast Trigonometric Approximations:\n");
    f32 angle = 0.785398f; // ~PI/4
    f32 approx_val = fast_sin(angle);
    f32 exact_val  = sinf(angle);
    printf("%s\n", (std::string("   Angle PI/4: fast_sin = ") + ::veloc::to_str(approx_val) + std::string(", std::sin = ") + ::veloc::to_str(exact_val) + std::string(" (diff = ") + ::veloc::to_str(approx_val - exact_val) + std::string(")")).c_str());

    const usize TRIG_COUNT = 1000000;
    f32 trig_sum_fast = 0;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        for (usize i = 0; i < TRIG_COUNT; i++) {
            trig_sum_fast += fast_sin((f32)i * 0.001f);
        }
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "fast_sin (1,000,000 calls)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    f32 trig_sum_std = 0;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        for (usize i = 0; i < TRIG_COUNT; i++) {
            trig_sum_std += sinf((f32)i * 0.001f);
        }
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "std::sinf (1,000,000 calls)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    // 4. AVX2 SIMD Min/Max on 1,000,000 Floats
    printf("\n4. AVX2 SIMD Min/Max Reduction (1,000,000 Floats):\n");
    const usize FLOAT_COUNT = 1000000;
    f32* float_arr = (f32*)veloc_aligned_alloc(32, sizeof(f32) * FLOAT_COUNT);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(float_arr); };

    veloc::FastRng rng(12345);
    for (usize i = 0; i < FLOAT_COUNT; i++) {
        float_arr[i] = rng.next_f32() * 1000.0f;
    }
    float_arr[42] = -999.0f;
    float_arr[1337] = 9999.0f;

    f32 min_val = 0, max_val = 0;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_min_max_f32(float_arr, FLOAT_COUNT, &min_val, &max_val);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD Min/Max (1M floats)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    printf("%s\n", (std::string("   Calculated Min: ") + ::veloc::to_str(min_val) + std::string(", Max: ") + ::veloc::to_str(max_val)).c_str());

    // 5. Branchless 8-bit LSD Radix Sort vs std::sort (1,000,000 Integers)
    printf("\n5. Extreme Sorting Benchmark (1,000,000 32-bit Integers):\n");
    const usize INT_COUNT = 1000000;
    u32* radix_arr = (u32*)veloc_aligned_alloc(32, sizeof(u32) * INT_COUNT);
    u32* std_arr   = (u32*)veloc_aligned_alloc(32, sizeof(u32) * INT_COUNT);
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(radix_arr); };
    auto _veloc_defer_3 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(std_arr); };

    for (usize i = 0; i < INT_COUNT; i++) {
        u32 r = (u32)rng.next_u64();
        radix_arr[i] = r;
        std_arr[i] = r;
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        radix_sort_u32(radix_arr, INT_COUNT);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "veloc::radix_sort_u32 (1M ints)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        std::sort(std_arr, std_arr + INT_COUNT);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "std::sort (1M ints)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    // Verify sort correctness
    bool sorted_correct = true;
    for (usize i = 1; i < INT_COUNT; i++) {
        if (radix_arr[i] < radix_arr[i - 1]) {
            sorted_correct = false;
            break;
        }
    }
    const char* sort_status = sorted_correct ? "YES" : "NO";
    printf("%s\n", (std::string("   Radix sort verified: ") + ::veloc::to_str(sort_status)).c_str());
    printf("%s\n", (std::string("   First 3: [") + ::veloc::to_str(radix_arr[0]) + std::string(", ") + ::veloc::to_str(radix_arr[1]) + std::string(", ") + ::veloc::to_str(radix_arr[2]) + std::string("], Last: ") + ::veloc::to_str(radix_arr[INT_COUNT - 1])).c_str());

    printf("===============================================================\n");
    printf("      All VeloC 4.0 Systems & Benchmarks Completed!            \n");
    printf("===============================================================\n");
    return 0;
}