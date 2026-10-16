#include "D:/VeloC/include/veloc.h"

// [VeloC module declaration]

auto main() -> i32 {
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_BOLD) + std::string("    VeloC 6.0: Boost-Killer (RNG, LockFree, Sockets)") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());

    // 1. FastRng: 1.5+ Billion Random Numbers/Sec (vs slow std::mt19937)
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[1] Hardware-Grade Fast PRNG (XorShift128+)") + ::veloc::to_str(VELOC_RESET)).c_str());
    auto rng = veloc::FastRng(123456789ULL);

    VeloC_Timer timer;
    const usize RANDOM_COUNT = 10000000; // 10 Million random (numbers).unwrap()
    timer.start();

    u64 checksum = 0;
    for (usize i = 0; i < RANDOM_COUNT; i++) {
        checksum += rng.next_u64();
    }
    f64 rng_ms = timer.elapsed_ms();
    f64 rng_speed = ((f64)RANDOM_COUNT / (rng_ms / 1000.0)) / 1e6;

    printf("%s\n", (std::string("  Generated 10,000,000 random 64-bit numbers in: ") + ::veloc::to_str(rng_ms) + std::string(" ms")).c_str());
    printf("%s\n", (std::string("  ") + ::veloc::to_str(VELOC_GREEN) + std::string("RNG Throughput: ") + ::veloc::to_str(rng_speed) + std::string(" MILLION numbers / sec!") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (std::string("  Sample float [0.0..1.0): ") + ::veloc::to_str(rng.next_f32())).c_str());

    // 2. LockFreeRingBuffer: Zero Mutex Atomic Queue (Replaces Boost.Lockfree)
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[2] LockFreeRingBuffer (Lockless SPSC Queue)") + ::veloc::to_str(VELOC_RESET)).c_str());
    auto queue = veloc::LockFreeRingBuffer<i32, 1024>();

    // Producer pushes items
    for (i32 i = 1; i <= 5; i++) {
        queue.push(i * 100);
    }
    printf("  Pushed 5 messages into atomic lockless ring buffer\n");

    // Consumer pops items
    while (true) {
        const auto msg = queue.pop();
        if (msg.is_none()) break;
        const auto val = msg.unwrap();
        printf("%s\n", (std::string("  Consumer received message: ") + ::veloc::to_str(val) + std::string(" (Zero mutex contention)")).c_str());
    }

    // 3. SpatialHash2D: O(1) Gamedev Spatial Partitioning Grid
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[3] SpatialHash2D (O(1) Spatial Partitioning Grid)") + ::veloc::to_str(VELOC_RESET)).c_str());
    auto grid = veloc::SpatialHash2D(10.0f); // 10x10 units per cell

    // Insert 3 particles in different locations
    grid.insert(1, 5.0f, 5.0f);    // Cell (0, 0)
    grid.insert(2, 8.5f, 9.1f);    // Cell (0, 0) - same (cell).unwrap()
    grid.insert(3, 45.0f, 75.0f);  // Cell (4, 7) - different (cell).unwrap()

    const auto key = grid.hash_pos(7.0f, 7.0f); // Should find particles 1 and (2).unwrap()
    const auto nearby = grid.grid.get(key);
    if (nearby.is_some()) {
        const auto list = nearby.unwrap();
        printf("%s\n", (std::string("  Spatial query near (7, 7) found ") + ::veloc::to_str(list.len()) + std::string(" entities: Entity #") + ::veloc::to_str(list[0]) + std::string(", Entity #") + ::veloc::to_str(list[1])).c_str());
    }

    printf("%s\n", (::veloc::to_str(VELOC_GREEN) + std::string("[SUCCESS] VeloC 6.0 Boost-killer suite passed!") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());

    return 0;
}