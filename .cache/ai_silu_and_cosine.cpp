#include "D:/VeloC/include/veloc.h"

// VeloC 7.5: AVX2 SIMD SiLU, SIMD Cosine Similarity & while let pattern matching
auto test_simd_silu() -> void {
    printf("--- 1. Testing AVX2 SIMD SiLU / Swish Activation (LLaMA 2/3) ---\n");
    const usize count = 1000000;
    const auto data = (f32*)veloc_aligned_alloc(32, sizeof(f32) * count);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(data); };

    for (const auto i : range(0, static_cast<i64>(count), 1)) {
        data[i] = (static_cast<f32>((i % 100))) * 0.1f - 5.0f;
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_silu(data, count);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD SiLU (1M floats)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("%s\n", (std::string("Sample data[0] = ") + ::veloc::to_str(data[0]) + std::string(", data[50] = ") + ::veloc::to_str(data[50])).c_str());
}

auto test_simd_cosine_similarity() -> void {
    printf("--- 2. Testing AVX2 SIMD Cosine Similarity (Vector Databases & AI Search) ---\n");
    const usize dim = 4096; // 4k embedding dimension (LLaMA 3 embedding size)
    const auto vec_a = (f32*)veloc_aligned_alloc(32, sizeof(f32) * dim);
    const auto vec_b = (f32*)veloc_aligned_alloc(32, sizeof(f32) * dim);
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(vec_a); };
    auto _veloc_defer_3 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(vec_b); };

    for (const auto i : range(0, static_cast<i64>(dim), 1)) {
        vec_a[i] = 1.0f;
        vec_b[i] = 1.0f;
    }

    const usize iterations = 100000;
    f32 last_sim = 0.0f;

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        for (const auto i : range(0, static_cast<i64>(iterations), 1)) {
            last_sim = simd_cosine_similarity(vec_a, vec_b, dim);
        }
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD Cosine Similarity (100k queries, dim=4096)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("%s\n", (std::string("Identical vectors similarity = ") + ::veloc::to_str(last_sim) + std::string(" (Expected: 1.0)")).c_str());
    assert_true(last_sim > 0.999f && last_sim < 1.001f);
}

auto test_while_let_pattern_matching() -> void {
    printf("--- 3. Testing Rust-style while let Some(...) loop ---\n");
    const auto queue = FixedQueue<i32, 8>();
    auto q = queue;
    q.push(10);
    q.push(20);
    q.push(30);

    i32 sum = 0;
    usize count = 0;

    for (auto _veloc_wopt_1 = (q.pop()); _veloc_wopt_1.is_some(); _veloc_wopt_1 = (q.pop())) {
        auto& item = _veloc_wopt_1.val;

        printf("%s\n", (std::string("Popped item from queue: ") + ::veloc::to_str(item)).c_str());
        sum += item;
        count++;
    }

    printf("%s\n", (std::string("Total sum = ") + ::veloc::to_str(sum) + std::string(", count = ") + ::veloc::to_str(count)).c_str());
    assert_eq(sum, 60);
    assert_eq(count, 3);
    assert_true(q.is_empty());
}

int main() {
    test_simd_silu();
    test_simd_cosine_similarity();
    test_while_let_pattern_matching();
    printf("ALL VELOC 7.5 CHECKS PASSED WITH FLYING COLORS!\n");
    return 0;
}