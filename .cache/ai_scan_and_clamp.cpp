#include "D:/VeloC/include/veloc.h"

// VeloC 8.0: SIMD Prefix Sum, In-place SIMD Clamp & Integer Match Expressions
auto test_simd_prefix_sum() -> void {
    printf("--- 1. Testing AVX2 SIMD Prefix Sum (Inclusive Scan) ---\n");
    const usize count = 1000000;
    const auto in_arr = (u32*)veloc_aligned_alloc(32, sizeof(u32) * count);
    const auto out_arr = (u32*)veloc_aligned_alloc(32, sizeof(u32) * count);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(in_arr); };
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(out_arr); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        in_arr[i] = 1;
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_prefix_sum_u32(out_arr, in_arr, count);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD Prefix Sum (1M u32)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("%s\n", (std::string("Sample out[0] = ") + ::veloc::to_str(out_arr[0]) + std::string(", out[99] = ") + ::veloc::to_str(out_arr[99]) + std::string(", out[999999] = ") + ::veloc::to_str(out_arr[999999])).c_str());
    assert_eq(out_arr[0], 1);
    assert_eq(out_arr[99], 100);
    assert_eq(out_arr[999999], 1000000);
}

auto test_simd_clamp_array() -> void {
    printf("--- 2. Testing AVX2 SIMD Clamp Array ---\n");
    const usize count = 1000000;
    const auto data = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    auto _veloc_defer_3 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(data); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        data[i] = (static_cast<f32>((i % 100))) - 50.0f; // range [-50.0, 49.0]
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_clamp_array(data, count, -10.0f, 10.0f);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD Clamp Array (1M floats, [-10.0, 10.0])", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    // Verify all clamped
    auto all_valid = true;
    for (const auto i : range(0, static_cast<i64>(count), 1000)) {
        if (data[i] < -10.0f || data[i] > 10.0f) all_valid = false;
    }
    printf("%s\n", (std::string("Clamped data[0] = ") + ::veloc::to_str(data[0]) + std::string(", data[99] = ") + ::veloc::to_str(data[99])).c_str());
    assert_true(all_valid);
}

auto test_integer_match() -> void {
    printf("--- 3. Testing Integer Match Pattern Matching ---\n");
    const i32 code = 200;
    auto status = "Unknown";

    switch (code) {
    case 200: status = "OK"; break;
    case 404: status = "Not Found"; break;
    case 500: status = "Internal Server Error"; break;
    default: status = "Other"; break;
}

    printf("%s\n", (std::string("HTTP ") + ::veloc::to_str(code) + std::string(" matched status: ") + ::veloc::to_str(status)).c_str());
    assert_true(strcmp(status, "OK") == 0);

    const i32 error_code = 404;
    switch (error_code) {
    case 200: status = "OK"; break;
    case 404: status = "Not Found"; break;
    default: status = "Other"; break;
}
    printf("%s\n", (std::string("HTTP ") + ::veloc::to_str(error_code) + std::string(" matched status: ") + ::veloc::to_str(status)).c_str());
    assert_true(strcmp(status, "Not Found") == 0);
}

int main() {
    test_simd_prefix_sum();
    test_simd_clamp_array();
    test_integer_match();
    printf("ALL VELOC 8.0 ADVANCED TESTS COMPLETED PERFECTLY!\n");
    return 0;
}