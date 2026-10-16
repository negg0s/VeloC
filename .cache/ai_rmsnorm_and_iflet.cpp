#include "D:/VeloC/include/veloc.h"

// VeloC 7.0: AVX2 SIMD RMSNorm, Parallel Reduce & Rust-style if let pattern matching
auto test_simd_rms_norm() -> void {
    printf("--- 1. Testing AVX2 SIMD RMSNorm (LLaMA 3 / Gemma Normalization) ---\n");
    const usize count = 1000000;
    const auto data = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    const auto weight = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(data); };
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(weight); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        data[i] = (static_cast<f32>((i % 100))) * 0.1f - 5.0f;
        weight[i] = 1.0f;
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_rms_norm(data, weight, count, 1e-5f);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD RMSNorm (1M floats)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("%s\n", (std::string("Normalized data[0] = ") + ::veloc::to_str(data[0]) + std::string(", data[50] = ") + ::veloc::to_str(data[50])).c_str());
}

auto test_parallel_reduce() -> void {
    printf("--- 2. Testing parallel_reduce across 12 hardware threads ---\n");
    const usize count = 10000000; // 10 Million numbers
    const auto arr = (u64*)veloc_aligned_alloc(32, sizeof(u64) * count);
    auto _veloc_defer_3 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(arr); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        arr[i] = 1;
    }

    u64 total = 0;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        total = parallel_reduce(arr, count, 0ULL, [&](auto acc, auto val) { return acc + val; });
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "parallel_reduce sum (10M elements, 12 threads)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("%s\n", (std::string("Parallel sum of 10M ones = ") + ::veloc::to_str(total) + std::string(" (Expected: 10000000)")).c_str());
    assert_eq(total, 10000000ULL);
}

auto test_if_let_pattern_matching() -> void {
    printf("--- 3. Testing Rust-style if let Some / Ok pattern matching ---\n");
    const auto opt_some = Option<i32>::Some(42);
    const auto opt_none = Option<i32>::None();

    auto visited_some = false;
    if (auto _veloc_opt_1 = (opt_some); _veloc_opt_1.is_some()) {
        auto& val = _veloc_opt_1.val;

        printf("%s\n", (std::string("Successfully matched Some with value: ") + ::veloc::to_str(val)).c_str());
        assert_eq(val, 42);
        visited_some = true;
    }
    assert_true(visited_some);

    auto visited_none = false;
    if (auto _veloc_opt_2 = (opt_none); _veloc_opt_2.is_some()) {
        auto& val = _veloc_opt_2.val;

        printf("ERROR: Should not enter here!\n");
        assert_true(false);
    } else {
        printf("Successfully bypassed None in if let\n");
        visited_none = true;
    }
    assert_true(visited_none);

    const auto res_ok = Result<const char*, int>::Ok("VeloC Ultra Speed");
    auto visited_ok = false;
    if (auto _veloc_res_3 = (res_ok); _veloc_res_3.is_ok()) {
        auto& msg = _veloc_res_3.val;

        printf("%s\n", (std::string("Successfully matched Ok with message: ") + ::veloc::to_str(msg)).c_str());
        visited_ok = true;
    }
    assert_true(visited_ok);
}

int main() {
    test_simd_rms_norm();
    test_parallel_reduce();
    test_if_let_pattern_matching();
    printf("ALL VELOC 7.0 CHECKS COMPLETED WITH 100 PERCENT SUCCESS!\n");
    return 0;
}