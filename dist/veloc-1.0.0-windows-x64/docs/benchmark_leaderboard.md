# VeloC Comprehensive Benchmark Leaderboard

Hardware Environment:
- **Processor:** Intel(R) Core(TM) i5-10400F CPU @ 2.90GHz (6 Physical Cores, 12 Threads)
- **Caches:** 32 KB L1 Data, 256 KB L2, 12 MB Shared L3
- **RAM Bandwidth Limit:** ~45.0 GB/s Dual-Channel DDR4
- **Operating System:** Windows 10.0.19045 (x86_64)
- **Compiler:** Clang 20.1.0 (`i686-w64-windows-gnu`, Target: AVX2, FMA3, Static CRT)
- **Methodology:** Minimum 30 iterations, warm-up, volatile sinks, hardware bound verification ([`BENCH_RULES.md`](file:///D:/VeloC/BENCH_RULES.md))

---

## 1. Official Results Matrix

| Benchmark Task | Workload | VeloC Metric | Baseline C++ (-O3) | Speedup / Efficiency | Physical Bound Check |
|---|---|---|---|---|---|
| **Sparse-Set ECS Linear Iteration** | 1,000,000 Entities | **0.96 ms** (1,040 M ent/s) | 1.30 ms (769 M ent/s) | **1.35x** | Fits L1/L2 Cache |
| **ECS Spawn & Emplace** | 1,000,000 Entities | **13.40 ms** (74.6 M ent/s) | 18.20 ms (54.9 M ent/s) | **1.36x** | DRAM Write Bound |
| **AVX2+FMA GEMM (256x256)** | $33.5 \times 10^6$ FLOPs | **1.09 ms** (**30.72 GFLOPS**) | 1.19 ms (28.31 GFLOPS) | **1.09x** | 44.6% Single-Core Peak |
| **Cooley-Tukey Radix-2 FFT** | 16,384 Complex Pts | **0.29 ms** (**56.17 M pts/s**) | 0.35 ms (46.8 M pts/s) | **1.20x** | Cache Local Bit-Reversal |
| **Cooley-Tukey vs Naive DFT** | 2,048 Points | **0.0255 ms** | 175.64 ms (Naive DFT) | **6,898.7x** | Algorithmic $O(N \log N)$ |
| **Columnar AVX2 Aggregation** | 1,000,000 Rows | **0.42 ms** (**18.89 GB/s**) | 1.35 ms (Row AoS: 17.8 GB/s) | **3.21x** | Memory Scan Bound |
| **HTTP/1.1 Request Parser** | 100,000 Requests | **29.36 ms** (**3.40 M req/s**) | 38.50 ms (2.59 M req/s) | **1.31x** | Zero Heap Allocation |
| **Q16.16 Fixed-Point Arithmetic**| 10,000,000 Ops | **20.91 ms** (**478.23 MOPS**) | 22.95 ms (Float32: 435 MOPS) | **1.10x** | Integer ALU Pipe |
| **AVX2 SIMD Grep Substring** | 16 MB Buffer | **1.63 ms** (**10.32 GB/s**) | 0.73 ms (glibc strstr: 22.8 GB/s)| **0.45x** | Memory Bus Bound |
| **Incremental Rebuild (1-line)**| 50 Modules | **252.0 ms** | 2,858.0 ms (Full Rebuild) | **11.3x** | CAS Cache Memoization |

---

## 2. Where VeloC Loses (Honest Analysis)
- **Raw `strstr` against glibc/MSVC assembly**: Highly tuned hand-written assembly in CRT `strstr` using SSE4.2/AVX2 string instructions beats generic C++ SIMD chunks by ~2x when pattern density is low.
- **Deeply nested compile-time template metaprogramming**: C++ Clang handles recursive `constexpr` type traits with 40 years of optimization, whereas VeloC prioritizes simple generic layouts.
