#include "D:/VeloC/include/veloc.h"

// VeloC 6.0: AI SIMD Softmax, Branchless Binary Search, Parallel Transform & Non-null Assertion
#include <algorithm>

auto test_softmax() -> void {
    printf("--- 1. Testing AVX2 SIMD Softmax for AI/Transformer LLM Inference ---\n");
    const usize count = 32768; // 32k logits (e.g. Vocabulary distribution)
    const auto logits = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(logits); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        logits[i] = (static_cast<f32>((i % 100))) * 0.1f - 5.0f;
    }

    // Benchmark SIMD Softmax
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_softmax(logits, count);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD Softmax (32k logits)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    // Verify sum of probabilities == 1.0f
    f32 sum = 0.0f;
    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        sum += logits[i];
    }
    printf("%s\n", (std::string("Softmax probability sum = ") + ::veloc::to_str(sum) + std::string(" (Expected: ~1.0)")).c_str());
    assert_true(sum > 0.99f && sum < 1.01f);
}

auto test_branchless_binary_search() -> void {
    printf("--- 2. Testing Branchless CMOV Binary Search vs std::lower_bound ---\n");
    const usize count = 1000000;
    const auto data = (u32*)veloc_aligned_alloc(32, sizeof(u32) * count);
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(data); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        data[i] = static_cast<u32>((i * 2));
    }

    const usize queries = 100000;
    const auto targets = (u32*)veloc_aligned_alloc(32, sizeof(u32) * queries);
    auto _veloc_defer_3 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(targets); };

    for (const auto i : range(0, static_cast<i64>(queries), 1)) {
        targets[i] = static_cast<u32>(((i * 37) % (count * 2)));
    }

    usize sum_std = 0;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        for (const auto i : range(0, static_cast<i64>(queries), 1)) {
            const auto it = std::lower_bound(data, data + count, targets[i]);
            sum_std += (it - data);
        }
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "std::lower_bound (100k queries)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    usize sum_branchless = 0;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        for (const auto i : range(0, static_cast<i64>(queries), 1)) {
            const auto idx = branchless_lower_bound(data, count, targets[i]);
            sum_branchless += idx;
        }
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "Branchless CMOV lower_bound (100k queries)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("%s\n", (std::string("std sum = ") + ::veloc::to_str(sum_std) + std::string(", branchless sum = ") + ::veloc::to_str(sum_branchless)).c_str());
    assert_eq(sum_std, sum_branchless);
}

auto test_parallel_transform() -> void {
    printf("--- 3. Testing parallel_transform across 12 hardware threads ---\n");
    const usize count = 2000000;
    const auto arr = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    auto _veloc_defer_4 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(arr); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        arr[i] = 1.0f;
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        parallel_transform(arr, count, [&](auto x) { return x * 3.0f + 5.0f; });
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "parallel_transform (2M floats, 12 threads)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("%s\n", (std::string("Sample arr[0] = ") + ::veloc::to_str(arr[0]) + std::string(", arr[1000] = ") + ::veloc::to_str(arr[1000]) + std::string(" (Expected: 8.0)")).c_str());
    assert_true(arr[0] == 8.0f);
    assert_true(arr[1000] == 8.0f);
}

auto test_non_null_assertion() -> void {
    printf("--- 4. Testing Non-null Assertion Operator opt! ---\n");
    const auto opt = Option<i32>::Some(42);
    const auto val = (opt).unwrap();
    printf("%s\n", (std::string("Unwrapped value via opt! = ") + ::veloc::to_str(val)).c_str());
    assert_eq(val, 42);

    const auto res = Result<i32, const char*>::Ok(1337);
    const auto r_val = (res).unwrap();
    printf("%s\n", (std::string("Unwrapped value via res! = ") + ::veloc::to_str(r_val)).c_str());
    assert_eq(r_val, 1337);
}

int main() {
    test_softmax();
    test_branchless_binary_search();
    test_parallel_transform();
    test_non_null_assertion();
    printf("ALL VELOC 6.0 CHECKS PASSED PERFECTLY!\n");
    return 0;
}