# VeloC Performance Guide: Engineering for Extreme Speed

This guide explains how to write code that extracts maximum throughput from modern x86_64 CPUs (AVX2, FMA3, 256-bit SIMD) with VeloC.

---

## 1. The Core Performance Mental Model
Modern Intel/AMD CPUs are parallel execution beasts:
- 1 Core can execute **two 256-bit FMA operations per clock cycle** (16 single-precision floats per cycle).
- Memory bandwidth is strictly bounded (~45 GB/s dual-channel DDR4).
- Cache hierarchy latency:
  - L1 Data Cache (32 KB): ~4 cycles (0.9 ns)
  - L2 Cache (256 KB): ~12 cycles (2.8 ns)
  - L3 Cache (12 MB): ~40 cycles (10 ns)
  - Main RAM: ~200 cycles (50-70 ns)

**Golden Rule:** Keep active data in L1/L2 caches using Structure-of-Arrays (SoA) and continuous linear buffers (`veloc::ai::Tensor`, `veloc::game::SparseSet`).

---

## 2. Optimization Checklist

### Vectorization
- [x] Use 32-byte aligned allocations (`veloc_aligned_alloc(32, bytes)`).
- [x] Use 8-wide unrolled loops (`f32x8`) for bulk data math.
- [x] Use FMA intrinsics (`_mm256_fmadd_ps`) instead of separate multiply and add.

### Memory & Allocation
- [x] Avoid dynamic `malloc`/`free` inside per-frame or high-frequency loops.
- [x] Use `VeloC_Arena` or `TempAllocator` with instant rewind for temporary allocations.
- [x] Pre-reserve vector capacities (`reserve()`).

### Avoiding Optimizer Traps
- [x] Compile with `-fwrapv` to prevent undefined signed overflow optimization bugs.
- [x] Use `volatile` sinks in benchmarks to prevent compiler from eliminating unused results.

---

## 3. Anti-Patterns to Avoid

| Anti-Pattern | Why It Kills Speed | What to Do in VeloC |
|---|---|---|
| **Array of Structures (AoS)** | Loads unwanted padding/fields into cache line | Use `soa struct Particle` |
| **Virtual Methods / Dynamic Dispatch** | Indirect branch miss, destroys inlining | Use static dispatch or SparseSet ECS |
| **Pointer Chasing (Linked Lists)** | Constant cache misses (70ns per node) | Use contiguous arrays or `FlatMap` |
| **Hidden Heap Allocations** | Lock contention in CRT `malloc` | Use `Arena` or `StaticPool` |
