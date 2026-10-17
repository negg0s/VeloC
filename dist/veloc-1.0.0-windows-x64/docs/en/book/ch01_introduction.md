# Chapter 1: Introduction to VeloC

VeloC is a modern systems programming language built for zero-cost performance, predictable memory layouts, and clean hardware control.

## Key Tenets
1. **Zero-Cost Abstractions**: High-level ergonomics without hidden allocations.
2. **First-Class Memory Control**: Explicit Arenas, Pools, and Tracking Allocators.
3. **Hardware Alignment**: Native SoA (Structure of Arrays) and AVX2/FMA SIMD intrinsics.
4. **Strict Safety Profiles**: Deterministic signed integer arithmetic (`-fwrapv`) and IEEE-754 strict floating-point compliance.

## Hello, World!
```veloc
fn main() -> i32 {
    printf("Hello, VeloC!\n");
    return 0;
}
```
