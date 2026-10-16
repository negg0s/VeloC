#include "D:/VeloC/include/veloc.h"

// ============================================================================
// VeloC Modern Community Wishlist & Ultra-Fast Subsystems
// ============================================================================

struct Particle {
    f32 x, y, z;
    f32 vx, vy, vz;
    u32 id;
};

int main() {
    printf("===============================================================\n");
    printf("      VeloC 3.0: Modern Systems Architecture & Hardware Speed   \n");
    printf("===============================================================\n");

    // 1. String Pattern Matching (Reddit #1 Missing Feature in C++)
    // Desugars into zero-overhead compile-time FNV-1a jump (table).unwrap()
    const auto cmd = "optimize";
    printf("%s", "1. Zero-Cost String Pattern Matching: 'optimize' => ");
    switch (::veloc::str_hash(cmd)) {
    case "build"_hash: { printf("Action: Build triggered!\n"); } break;
    case "optimize"_hash: { printf("Action: Extreme SIMD + AVX2 Optimization applied!\n"); } break;
    case "clean"_hash: { printf("Action: Cache wiped!\n"); } break;
    default: { printf("Action: Unknown command\n"); } break;
}

    // 2. Hardware-level Bit Manipulation & Fast BitSet
    printf("\n2. Hardware-Level Bit Operations & BitSet<256>:\n");
    BitSet<256> active_entities;
    active_entities.set(7);
    active_entities.set(42);
    active_entities.set(137);

    printf("%s\n", (std::string("   Entities marked active count: ") + ::veloc::to_str(active_entities.count()) + std::string(" (via hardware POPCNT)")).c_str());
    printf("%s\n", (std::string("   First active entity index: ") + ::veloc::to_str(active_entities.find_first()) + std::string(" (via hardware CTZ)")).c_str());

    const u64 test_val = 0x0000000000000008ULL;
    const auto clz = veloc::count_leading_zeros(test_val);
    const auto ctz = veloc::count_trailing_zeros(test_val);
    printf("%s\n", (std::string("   Value 8: Leading Zeros = ") + ::veloc::to_str(clz) + std::string(", Trailing Zeros = ") + ::veloc::to_str(ctz)).c_str());

    // 3. First-class bench "name" block with RDTSC Cycle Counter
    printf("\n3. First-Class Hardware Benchmark Blocks (Cycle Accurate):\n");
    
    // Benchmark 1: Zero-Allocation FixedPool vs Standard Heap
    FixedPool<Particle, 10000> pool;
    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        for (usize i = 0; i < 10000; i++) {
            Particle* p = pool.alloc();
            p->id = (u32)i;
            p->x = 1.0f;
        }
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "FixedPool 10,000 Allocs", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    printf("%s\n", (std::string("   Pool active objects: ") + ::veloc::to_str(pool.count()) + std::string(" / ") + ::veloc::to_str(pool.capacity())).c_str());

    // Benchmark 2: AVX2 256-bit Integer SIMD (i32x8)
    alignas(32) i32 arr_a[8] = {10, 20, 30, 40, 50, 60, 70, 80};
    alignas(32) i32 arr_b[8] = {1,  2,  3,  4,  5,  6,  7,  8 };
    alignas(32) i32 arr_res[8];

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        i32x8 va = i32x8_load_aligned(arr_a);
        i32x8 vb = i32x8_load_aligned(arr_b);
        i32x8 vres = i32x8_mul(va, vb);
        i32x8_store_aligned(arr_res, vres);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 i32x8 Vector Math", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}
    printf("%s\n", (std::string("   SIMD result: [") + ::veloc::to_str(arr_res[0]) + std::string(", ") + ::veloc::to_str(arr_res[1]) + std::string(", ") + ::veloc::to_str(arr_res[2]) + std::string(", ..., ") + ::veloc::to_str(arr_res[7]) + std::string("]")).c_str());

    // 4. Lock-Free Channel (Go/Rust style concurrency)
    printf("\n4. Lock-Free Thread Communication Channel:\n");
    veloc::Channel<i32, 128> channel;
    channel.send(42);
    channel.send(1337);
    channel.send(9999);

    const auto val1 = channel.recv().unwrap();
    const auto val2 = channel.recv().unwrap();
    const auto val3 = channel.recv().unwrap();
    printf("%s\n", (std::string("   Received from channel: ") + ::veloc::to_str(val1) + std::string(", ") + ::veloc::to_str(val2) + std::string(", ") + ::veloc::to_str(val3)).c_str());

    printf("===============================================================\n");
    printf("      All VeloC 3.0 Systems & Benchmarks Completed!            \n");
    printf("===============================================================\n");
    return 0;
}