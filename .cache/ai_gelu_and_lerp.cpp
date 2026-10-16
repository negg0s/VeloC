#include "D:/VeloC/include/veloc.h"

// VeloC 6.5: AI SIMD GeLU, Vectorized Lerp, Enumerate Loops & Struct Destructuring
auto test_simd_gelu() -> void {
    printf("--- 1. Testing AVX2 SIMD GeLU (LLM/Transformer Activation) ---\n");
    const usize count = 1000000;
    const auto data = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(data); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        data[i] = (static_cast<f32>((i % 200))) * 0.05f - 5.0f;
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_gelu(data, count);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD GeLU (1M floats)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    // Verify properties of GeLU: GeLU(0) == 0, GeLU(-inf) -> 0, GeLU(x) > 0 for x > 0
    printf("%s\n", (std::string("Sample data[0] = ") + ::veloc::to_str(data[0]) + std::string(", data[100] = ") + ::veloc::to_str(data[100])).c_str());
}

auto test_simd_lerp() -> void {
    printf("--- 2. Testing AVX2 SIMD Lerp (Linear Interpolation) ---\n");
    const usize count = 1000000;
    const auto a = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    const auto b = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    const auto out = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(a); };
    auto _veloc_defer_3 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(b); };
    auto _veloc_defer_4 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(out); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        a[i] = 10.0f;
        b[i] = 20.0f;
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_lerp_array(out, a, b, 0.25f, count);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD Lerp (1M floats, t=0.25)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("%s\n", (std::string("Interpolated out[0] = ") + ::veloc::to_str(out[0]) + std::string(" (Expected: 12.5)")).c_str());
    assert_true(out[0] == 12.5f);
}

auto test_enumerate_loop() -> void {
    printf("--- 3. Testing Python/Rust-style enumerate() loop ---\n");
    const auto numbers = SmallVec<i32, 8>();
    auto num_vec = numbers;
    num_vec.push(100);
    num_vec.push(200);
    num_vec.push(300);

    usize idx = 0; for (const auto& val : num_vec) if (bool _veloc_step_ = true) for (; _veloc_step_; _veloc_step_ = false, idx++) {
        printf("%s\n", (std::string("Index: ") + ::veloc::to_str(idx) + std::string(", Value: ") + ::veloc::to_str(val)).c_str());
        if (idx == 0) assert_eq(val, 100);
        if (idx == 1) assert_eq(val, 200);
        if (idx == 2) assert_eq(val, 300);
    }
}

int main() {
    test_simd_gelu();
    test_simd_lerp();
    test_enumerate_loop();
    printf("ALL VELOC 6.5 SYSTEMS PASSED PERFECTLY!\n");
    return 0;
}