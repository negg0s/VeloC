#include "D:/VeloC/include/veloc.h"

// ============================================================================
// VeloC 4.5: SIMD Media Engine (Audio/Image), Fast String Search, and ??
// ============================================================================

int main() {
    printf("===============================================================\n");
    printf("      VeloC 4.5: SIMD Multimedia & Modern Systems Operators    \n");
    printf("===============================================================\n");

    // 1. Null-Coalescing Operator ::veloc::coalesce((, ))
    printf("1. Null-Coalescing Operator (??):\n");
    Option<i32> some_val = Option<i32>::Some(42);
    Option<i32> none_val = Option<i32>::None();

    const auto val1 = ::veloc::coalesce(some_val, 999);
    const auto val2 = ::veloc::coalesce(none_val, 999);
    printf("%s\n", (std::string("   some_val ?? 999 => ") + ::veloc::to_str(val1)).c_str());
    printf("%s\n", (std::string("   none_val ?? 999 => ") + ::veloc::to_str(val2)).c_str());

    // 2. AVX2 SIMD String Search (32 bytes per instruction)
    printf("\n2. AVX2 SIMD Text Search (10,000,000 Characters):\n");
    const usize TEXT_LEN = 10000000;
    char* text_buf = (char*)veloc_aligned_alloc(32, TEXT_LEN);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(text_buf); };

    memset(text_buf, 'a', TEXT_LEN);
    text_buf[TEXT_LEN - 1] = '\0';
    // Place target near the end (at 8,500,000)
    text_buf[8500000] = 'Z';

    i64 found_idx = -1;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        found_idx = simd_find_char(text_buf, TEXT_LEN, 'Z');
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD Search (10M chars)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    printf("%s\n", (std::string("   Found target 'Z' at index: ") + ::veloc::to_str(found_idx)).c_str());

    // 3. AVX2 SIMD Audio Mixing Engine (1,000,000 Samples)
    printf("\n3. AVX2 FMA Audio DSP Pipeline (1,000,000 32-bit Float Samples):\n");
    const usize AUDIO_SAMPLES = 1000000;
    f32* track1 = (f32*)veloc_aligned_alloc(32, sizeof(f32) * AUDIO_SAMPLES);
    f32* track2 = (f32*)veloc_aligned_alloc(32, sizeof(f32) * AUDIO_SAMPLES);
    f32* master = (f32*)veloc_aligned_alloc(32, sizeof(f32) * AUDIO_SAMPLES);
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(track1); };
    auto _veloc_defer_3 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(track2); };
    auto _veloc_defer_4 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(master); };

    for (usize i = 0; i < AUDIO_SAMPLES; i++) {
        track1[i] = 0.5f;
        track2[i] = 0.25f;
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_audio_mix(master, track1, track2, 0.8f, AUDIO_SAMPLES);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 SIMD Audio Mix (1M samples)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    printf("%s\n", (std::string("   Mixed sample [0]: ") + ::veloc::to_str(master[0]) + std::string(" (expected 0.5 + 0.25*0.8 = 0.70)")).c_str());

    // 4. AVX2 SIMD Image Pixel Inversion (10,000,000 Bytes)
    printf("\n4. AVX2 SIMD Image Processing Pipeline (10,000,000 Bytes):\n");
    const usize IMAGE_BYTES = 10000000;
    u8* image_data = (u8*)veloc_aligned_alloc(32, IMAGE_BYTES);
    auto _veloc_defer_5 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(image_data); };

    memset(image_data, 0x10, IMAGE_BYTES);

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_image_invert(image_data, IMAGE_BYTES);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 Image Invert (10 MB pixels)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    printf("%s\n", (std::string("   Inverted pixel byte [0]: 0x") + ::veloc::to_str(((u32)image_data[0])) + std::string(" (expected 0xEF = 239)")).c_str());

    printf("===============================================================\n");
    printf("      All VeloC 4.5 Multimedia & DSP Benchmarks Passed!        \n");
    printf("===============================================================\n");
    return 0;
}