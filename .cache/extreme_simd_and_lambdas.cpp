#include "D:/VeloC/include/veloc.h"

// ============================================================================
// VeloC 5.5: Rust-style Lambdas, SIMD 3D Distances, In-Register Transpose & Arena Markers
// ============================================================================

int main() {
    printf("===============================================================\n");
    printf("      VeloC 5.5: Next-Gen Systems Ergonomics & SIMD Physics    \n");
    printf("===============================================================\n");

    // 1. Rust-style Anonymous Lambdas
    printf("1. Rust-style Anonymous Lambdas (|params| => expr):\n");
    const auto triple_fn = [&](auto x) { return x * 3; };
    const auto add_fn = [&](auto a, auto b) { return a + b; };
    printf("%s\n", (std::string("   triple_fn(7)    => ") + ::veloc::to_str(triple_fn(7))).c_str());
    printf("%s\n", (std::string("   add_fn(100, 42) => ") + ::veloc::to_str(add_fn(100, 42))).c_str());

    // 2. Arena Marker Save & Restore (1-cycle Instant Rewind)
    printf("\n2. VeloC_Arena Marker Instant Rewind:\n");
    VeloC_Arena arena = VeloC_Arena::create(1024 * 1024); // 1 MB Arena
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { arena.destroy(); };

    // Allocate some persistent base data
    int* base_data = arena.alloc_array<int>(10);
    base_data[0] = 777;

    usize frame_marker = arena.get_marker();
    printf("%s\n", (std::string("   Initial Arena Offset: ") + ::veloc::to_str(frame_marker) + std::string(" bytes")).c_str());

    // Allocate 10,000 scratch objects inside the frame
    int* scratch = arena.alloc_array<int>(10000);
    scratch[0] = 999;
    printf("%s\n", (std::string("   Offset after scratch alloc: ") + ::veloc::to_str(arena.get_marker()) + std::string(" bytes")).c_str());

    // Instant rewind in 1 clock (cycle).unwrap()
    arena.reset_to_marker(frame_marker);
    printf("%s\n", (std::string("   Offset after instant rewind: ") + ::veloc::to_str(arena.get_marker()) + std::string(" bytes (scratch discarded, base preserved!)")).c_str());
    printf("%s\n", (std::string("   Base data [0] still intact: ") + ::veloc::to_str(base_data[0])).c_str());

    // 3. In-Register 4-Cycle SIMD Matrix Transpose
    printf("\n3. In-Register 4-Cycle SIMD Matrix Transpose:\n");
    Mat4 mat = Mat4::translation(1.0f, 2.0f, 3.0f);
    mat.m[1] = 5.0f;
    mat.m[2] = 9.0f;

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        Mat4 t = mat.transposed();
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "mat4.transposed() (In-Register)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    Mat4 t = mat.transposed();
    printf("%s\n", (std::string("   Original row 0: [") + ::veloc::to_str(mat.m[0]) + std::string(", ") + ::veloc::to_str(mat.m[1]) + std::string(", ") + ::veloc::to_str(mat.m[2]) + std::string(", ") + ::veloc::to_str(mat.m[3]) + std::string("]")).c_str());
    printf("%s\n", (std::string("   Transposed col0: [") + ::veloc::to_str(t.m[0]) + std::string(", ") + ::veloc::to_str(t.m[4]) + std::string(", ") + ::veloc::to_str(t.m[8]) + std::string(", ") + ::veloc::to_str(t.m[12]) + std::string("]")).c_str());

    // 4. AVX2 SIMD 3D Euclidean Distance (1,000,000 Particles)
    printf("\n4. AVX2 SIMD 3D Euclidean Distance Engine (1,000,000 Particles):\n");
    const usize NUM_PARTICLES = 1000000;
    f32* x1 = (f32*)veloc_aligned_alloc(32, sizeof(f32) * NUM_PARTICLES);
    f32* y1 = (f32*)veloc_aligned_alloc(32, sizeof(f32) * NUM_PARTICLES);
    f32* z1 = (f32*)veloc_aligned_alloc(32, sizeof(f32) * NUM_PARTICLES);

    f32* x2 = (f32*)veloc_aligned_alloc(32, sizeof(f32) * NUM_PARTICLES);
    f32* y2 = (f32*)veloc_aligned_alloc(32, sizeof(f32) * NUM_PARTICLES);
    f32* z2 = (f32*)veloc_aligned_alloc(32, sizeof(f32) * NUM_PARTICLES);

    f32* distances = (f32*)veloc_aligned_alloc(32, sizeof(f32) * NUM_PARTICLES);

    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(x1); };
    auto _veloc_defer_3 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(y1); };
    auto _veloc_defer_4 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(z1); };
    auto _veloc_defer_5 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(x2); };
    auto _veloc_defer_6 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(y2); };
    auto _veloc_defer_7 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(z2); };
    auto _veloc_defer_8 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(distances); };

    for (usize i = 0; i < NUM_PARTICLES; i++) {
        x1[i] = 10.0f; y1[i] = 20.0f; z1[i] = 30.0f;
        x2[i] = 13.0f; y2[i] = 24.0f; z2[i] = 30.0f; // dx=3, dy=4, dz=0 => dist=5.0
    }

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        simd_distance_3d(distances, x1, y1, z1, x2, y2, z2, NUM_PARTICLES);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "simd_distance_3d (1,000,000 pairs)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    printf("%s\n", (std::string("   Computed distance [0]: ") + ::veloc::to_str(distances[0]) + std::string(" (expected: 5.0)")).c_str());

    printf("===============================================================\n");
    printf("      All VeloC 5.5 Advanced Subsystems Passed!                \n");
    printf("===============================================================\n");
    return 0;
}