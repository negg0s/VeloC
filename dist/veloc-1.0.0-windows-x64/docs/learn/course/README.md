# VeloC in 30 Days (Interactive Course)

Learn high-performance systems programming in VeloC through 30 hands-on, test-driven lessons.

| Day | Title | Goal | Verification |
|:---|:---|:---|:---|
| Day 01 | [Hello World and Console Output](day_01.md) | Write your first VeloC program that outputs formatted text to stdout. | Automated Test |
| Day 02 | [Variables, Primitive Types, and Mutability](day_02.md) | Declare immutable and mutable variables with explicit primitive types. | Automated Test |
| Day 03 | [Arithmetic Operations and Type Casting](day_03.md) | Perform scalar arithmetic and explicit type casting using `as`. | Automated Test |
| Day 04 | [Branching and Expressions](day_04.md) | Use if/else conditional expressions to determine maximum values. | Automated Test |
| Day 05 | [Iteration: For and While Loops](day_05.md) | Calculate the sum of integers from 1 to N using a loop. | Automated Test |
| Day 06 | [Pure Functions and Tail Expressions](day_06.md) | Implement a recursive factorial function with base cases. | Automated Test |
| Day 07 | [Slices and Contiguous Buffers](day_07.md) | Traverse and compute the mean of an array buffer. | Automated Test |
| Day 08 | [References and Pointers](day_08.md) | Pass variables by pointer/reference to mutate in-place. | Automated Test |
| Day 09 | [Enums and Pattern Matching](day_09.md) | Define an enum and evaluate cases with `match`. | Automated Test |
| Day 10 | [Error Handling with Result and Option](day_10.md) | Safely propagate errors with Option/Result patterns. | Automated Test |
| Day 11 | [Zero-Cost Defer and Scope Guards](day_11.md) | Guarantee resource cleanup at scope exit using `defer`. | Automated Test |
| Day 12 | [Structs and Layout Control](day_12.md) | Define a 2D Vector struct with an in-place add method. | Automated Test |
| Day 13 | [Linear Bump Allocation with VeloC_Arena](day_13.md) | Allocate an array of 1,000 items from a bump arena and reset it. | Automated Test |
| Day 14 | [FixedPool Allocation Without Fragmentation](day_14.md) | Manage fixed-size nodes with deterministic $O(1)$ allocation. | Automated Test |
| Day 15 | [TrackingAllocator and Leak Telemetry](day_15.md) | Verify memory allocation counts and peak usage tracking. | Automated Test |
| Day 16 | [Structure-of-Arrays (SoA) for SIMD Alignment](day_16.md) | Create and populate an SoA collection for entity data. | Automated Test |
| Day 17 | [SIMD Intrinsics Basics: 256-bit Vector Lanes](day_17.md) | Load and broadcast a float into an 8-lane AVX2 vector. | Automated Test |
| Day 18 | [Fused Multiply-Add (FMA) in SIMD](day_18.md) | Perform $a 	imes b + c$ across 8 lanes simultaneously. | Automated Test |
| Day 19 | [SIMD Tail Handling and Alignment](day_19.md) | Process buffers whose size is not a multiple of 8 without overrun. | Automated Test |
| Day 20 | [Zero-Copy String Slices](day_20.md) | Inspect string length and substrings without heap allocations. | Automated Test |
| Day 21 | [High-Performance SwissTable Map](day_21.md) | Insert and query keys in an open-addressing hash table. | Automated Test |
| Day 22 | [SmallVec Stack Optimization](day_22.md) | Store small collections entirely on the stack to prevent heap allocations. | Automated Test |
| Day 23 | [Deterministic Signed Integer Arithmetic](day_23.md) | Verify two's complement wrapping with `-fwrapv`. | Automated Test |
| Day 24 | [Floating-Point Safety & Accuracy Contracts](day_24.md) | Inspect NaN/Inf propagation and test math accuracy contracts. | Automated Test |
| Day 25 | [Work-Stealing and Parallel Scheduling](day_25.md) | Distribute work items evenly across worker threads. | Automated Test |
| Day 26 | [Lock-Free SPSC Ring Buffer](day_26.md) | Pass data between a producer and consumer without mutex locks. | Automated Test |
| Day 27 | [Package Management and Dependencies](day_27.md) | Understand package configuration in `veloc.toml`. | Automated Test |
| Day 28 | [C-ABI Interoperability](day_28.md) | Export a function callable from C without name mangling. | Automated Test |
| Day 29 | [Benchmarking and Roofline Analysis](day_29.md) | Measure CPU cycles and elapsed milliseconds with VeloC_Timer. | Automated Test |
| Day 30 | [Capstone: Real-Time Particle Physics Step](day_30.md) | Integrate SoA, SIMD, Arena allocation, and defer into a production kernel. | Automated Test |
