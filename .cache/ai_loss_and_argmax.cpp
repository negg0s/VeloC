#include "D:/VeloC/include/veloc.h"

// VeloC 8.5: AVX2 SIMD Cross-Entropy Loss, ArgMax & defer blocks
auto test_simd_loss_and_argmax() -> void {
    printf("--- 1. Testing AVX2 SIMD Cross-Entropy Loss & ArgMax (LLM Inference/Training) ---\n");
    const usize vocab_size = 32768; // 32k vocabulary
    const auto logits = (f32*)veloc_aligned_alloc(32, sizeof(f32) * vocab_size);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(logits);
        printf("Multi-statement defer block executed successfully!\n"); };

    for (const auto i : range(0, static_cast<i64>(vocab_size), 1)) {
        logits[i] = (static_cast<f32>((i % 100))) * 0.1f - 5.0f;
    }
    // Set a clear maximum peak
    logits[1337] = 25.0f;

    const usize target_token = 1337;
    f32 loss = 0.0f;

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        loss = simd_cross_entropy_loss(logits, vocab_size, target_token);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD Cross-Entropy Loss (32k vocab)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    usize best_token = 0;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        best_token = simd_argmax(logits, vocab_size);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD ArgMax (32k vocab)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("%s\n", (std::string("Calculated Loss for target token ") + ::veloc::to_str(target_token) + std::string(": ") + ::veloc::to_str(loss) + std::string(" (Expected small loss due to high logit)")).c_str());
    printf("%s\n", (std::string("ArgMax predicted token: ") + ::veloc::to_str(best_token) + std::string(" (Expected: 1337)")).c_str());

    assert_eq(best_token, 1337);
    assert_true(loss >= 0.0f && loss < 0.1f);
}

auto test_defer_blocks() -> void {
    printf("--- 2. Testing Defer Blocks with multiple statements ---\n");
    auto step = 1;
    {
        auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { step += 10; };
        assert_eq(step, 1);
    }
    assert_eq(step, 11);
    printf("%s\n", (std::string("Step after defer block = ") + ::veloc::to_str(step) + std::string(" (Expected: 11)")).c_str());
}

int main() {
    test_simd_loss_and_argmax();
    test_defer_blocks();
    printf("ALL VELOC 8.5 CHECKS PASSED WITH ABSOLUTE PERFECTION!\n");
    return 0;
}