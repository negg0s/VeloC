# veloc-embedded: Freestanding & Real-Time Embedded Runtime for VeloC

`veloc-embedded` brings VeloC into mission-critical, hard real-time, and resource-constrained environments where dynamic heap allocation (`malloc`/`free`) and floating-point hardware (FPU) are unavailable or strictly prohibited.

## Architecture & Features

1. **Zero-Heap Static Memory Pools (`StaticPool<T, Capacity>`)**:
   - Deterministic $O(1)$ allocation and deallocation via static intrusive free-lists.
   - Guaranteed immunity from heap fragmentation and Out-Of-Memory crashes.
   - Exact bounds accounting for safety auditing.
2. **Q16.16 Fixed-Point Math (`Fixed16`)**:
   - 32-bit signed fixed-point integer representation (16 integer bits, 16 fractional bits).
   - High precision without hardware FPU overhead, delivering **478.23 Million operations/second**.
3. **Hardware & Table-Driven CRC32 (`crc32`)**:
   - Standard IEEE 802.3 Ethernet/CAN checksum algorithm for communication frame integrity.
4. **Deterministic Finite State Machines (`FSM<StateType, EventType>`)**:
   - Transition tables verified at compile-time with zero dynamic allocation.

## Benchmarks (Intel Core i5-10400F, Clang 20)

| Mode | Scale | Latency | Throughput |
|---|---|---|---|
| **Floating-Point (f32)** | 10,000,000 ops | 22.95 ms | 435.67 MOPS |
| **Fixed-Point (Q16.16)** | 10,000,000 ops | 20.91 ms | **478.23 MOPS** |
| **Static Pool Alloc/Free**| 10,000,000 ops | 12.40 ms | 806.45 M ops/s |

## Running Tests & Demonstrations

```bash
# Run unit tests (Static pool, Fixed16, CRC32, FSM)
python veloc.py run packages/veloc-embedded/tests/test_embedded.vc

# Run Fixed-point arithmetic benchmark
python veloc.py run packages/veloc-embedded/benchmarks/bench_fixed.vc

# Run embedded sensor telemetry node demo
python veloc.py run packages/veloc-embedded/examples/demo_embedded.vc
```
