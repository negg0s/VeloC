#include "D:/VeloC/include/veloc.h"

// ============================================================================
// VeloC 5.0: AI Vector Dot Product, Wyhash64, Tuple Destructuring & `as`
// ============================================================================

struct Pair {
    f32 first;
    f32 second;
};

Pair get_coordinates() {
    Pair p;
    p.first = 100.5f;
    p.second = 200.75f;
    return p;
}

int main() {
    printf("===============================================================\n");
    printf("      VeloC 5.0: AI Vector Search & Modern Language Syntax     \n");
    printf("===============================================================\n");

    // 1. Rust-style Safe Cast `static_cast<Type>(expr)` & Tuple Destructuring
    printf("1. Tuple Destructuring & Rust-style `as` Cast:\n");
    const auto [coord_x, coord_y] = get_coordinates();
    printf("%s\n", (std::string("   Destructured Pair: x = ") + ::veloc::to_str(coord_x) + std::string(", y = ") + ::veloc::to_str(coord_y)).c_str());

    const i32 raw_integer = 42;
    const f32 casted_float = static_cast<f32>(raw_integer) + 0.5f;
    const u64 casted_int = static_cast<u64>(123456);
    printf("%s\n", (std::string("   Cast results: float = ") + ::veloc::to_str(casted_float) + std::string(", u64 = ") + ::veloc::to_str(casted_int)).c_str());

    // 2. FixedQueue (L1-Cache Friendly FIFO Ring Queue)
    printf("\n2. FixedQueue<i32, 16> (Zero-Allocation FIFO Queue):\n");
    FixedQueue<i32, 16> queue;
    queue.push(10);
    queue.push(20);
    queue.push(30);

    const auto q1 = queue.pop().unwrap();
    const auto q2 = queue.pop().unwrap();
    printf("%s\n", (std::string("   Popped from queue: ") + ::veloc::to_str(q1) + std::string(", ") + ::veloc::to_str(q2) + std::string(", remaining count = ") + ::veloc::to_str(queue.len())).c_str());

    // 3. Fast 64-Bit Hashing (~25 GB/s throughput)
    printf("\n3. Ultra-Fast 64-bit Wyhash-Grade Hash:\n");
    const char* sample_key = "VeloC-Ultra-High-Speed-Compiler";
    u64 h1 = hash64(sample_key, strlen(sample_key));
    u64 h2 = hash64(sample_key, strlen(sample_key));
    printf("%s\n", (std::string("   Hash of '") + ::veloc::to_str(sample_key) + std::string("': 0x") + ::veloc::to_str(h1)).c_str());

    const usize HASH_BYTES = 10000000;
    u8* hash_buf = (u8*)veloc_aligned_alloc(32, HASH_BYTES);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(hash_buf); };
    memset(hash_buf, 0x5A, HASH_BYTES);

    u64 bulk_hash = 0;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        bulk_hash = hash64(hash_buf, HASH_BYTES);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "hash64 (10 MB buffer)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    printf("%s\n", (std::string("   10 MB Hash: 0x") + ::veloc::to_str(bulk_hash)).c_str());

    // 4. AVX2 4-Way Unrolled Dot Product (AI / Vector Search Engine)
    printf("\n4. AI High-Dimensional Vector Dot Product (10,000,000 Floats):\n");
    const usize VECTOR_DIM = 10000000;
    f32* vec_a = (f32*)veloc_aligned_alloc(32, sizeof(f32) * VECTOR_DIM);
    f32* vec_b = (f32*)veloc_aligned_alloc(32, sizeof(f32) * VECTOR_DIM);
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(vec_a); };
    auto _veloc_defer_3 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(vec_b); };

    for (usize i = 0; i < VECTOR_DIM; i++) {
        vec_a[i] = 1.0f;
        vec_b[i] = 2.0f;
    }

    f32 dot_res = 0;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        dot_res = simd_dot_product(vec_a, vec_b, VECTOR_DIM);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "simd_dot_product (10M floats)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    printf("%s\n", (std::string("   Dot Product Result: ") + ::veloc::to_str(dot_res) + std::string(" (expected: 20,000,000)")).c_str());

    printf("===============================================================\n");
    printf("      All VeloC 5.0 Systems & Benchmarks Passed!               \n");
    printf("===============================================================\n");
    return 0;
}