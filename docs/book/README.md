# The VeloC Book: Comprehensive Language & Systems Guide

Welcome to **The VeloC Book**, the definitive guide to systems programming with VeloC - the zero-cost high-performance language designed for game engines, machine learning, numerical science, and real-time systems.

---

## Table of Contents

### Part I: Fundamentals
- **Chapter 1: Getting Started** - Installing toolchain, `veloc new`, directory layout (`src/`, `tests/`, `veloc.toml`).
- **Chapter 2: Variables & Types** - `let` vs `let mut`, primitives (`i32`, `f32`, `usize`), and type inference.
- **Chapter 3: Control Flow** - `if`, `else`, `while`, and Python-like `for in range()`.
- **Chapter 4: Functions & Modules** - `pub fn`, `module`, and `import`.
- **Chapter 5: Error Handling** - `Option<T>`, `Result<T, E>`, and the monadic `?` (Try Operator).

### Part II: Data Structures & Pattern Matching
- **Chapter 6: Pattern Matching** - Exhaustive `match` statements and expressions.
- **Chapter 7: Memory Slices & Views** - `Slice<T>` and `Span<T>` with zero allocations.
- **Chapter 8: Standard Collections** - `SmallVec`, `FlatMap`, and `FixedQueue`.
- **Chapter 9: Native JSON Processing** - Built-in SIMD-accelerated JSON parser.

### Part III: Memory Management & Safety
- **Chapter 10: The VeloC Memory Model** - 32-byte/64-byte alignment and cache hierarchy.
- **Chapter 11: Controlled Allocators** - `VeloC_Arena`, `TrackingAllocator`, and `TempAllocator`.
- **Chapter 12: Zero-Heap Real-Time Programming** - `StaticPool` and freestanding mode.
- **Chapter 13: Static Bounds Elimination** - How the static analyzer proves safe array accesses.

### Part IV: Extreme Performance & Vectorization
- **Chapter 14: Data-Oriented Design** - Cache locality and Array of Structures (AoS) pitfalls.
- **Chapter 15: Structure-of-Arrays (SoA)** - First-class `soa struct` with auto AVX2 alignment.
- **Chapter 16: AVX2 & FMA3 Vector Intrinsics** - 256-bit SIMD registers (`f32x8`, `i32x8`).
- **Chapter 17: Deep Learning Acceleration** - Vectorized GEMM, Softmax, RMSNorm, and Attention.
- **Chapter 18: Digital Signal Processing** - Cooley-Tukey Radix-2 FFT at 56 Million samples/second.

### Part V: Systems Architecture & Tooling
- **Chapter 19: Game Engine ECS** - Sparse-Set ECS architecture with 1 Billion entities/s throughput.
- **Chapter 20: Network Engines** - Asynchronous non-blocking HTTP/1.1 and Rollback Netcode.
- **Chapter 21: Embedded & Fixed-Point** - Q16.16 math and deterministic FSMs without an FPU.
- **Chapter 22: C++ Migration & Interoperability** - Zero-cost C++ calls and `veloc from-cpp`.
- **Chapter 23: Package Management** - `veloc.toml`, `veloc.lock`, and semantic versioning.
- **Chapter 24: Compiler Internals & Incremental Build** - Salsa-style query engines and CAS caching.
- **Chapter 25: Performance Engineering Checklist** - Profiling with Chrome Tracing, cache lines, and avoiding optimizer traps.
