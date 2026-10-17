# Chapter 3: Memory and Allocators

VeloC treats memory allocation as an explicit architectural design choice rather than an invisible runtime side-effect.

## First-Class Allocator Hierarchy
- `VeloC_Arena`: Linear bump allocator with instantaneous reset.
- `FixedPool<T, N>`: Deterministic $O(1)$ allocation without fragmentation.
- `TrackingAllocator`: Real-time peak memory telemetry and leak detection.
- `TempAllocator`: Thread-local temporary scratch buffer.

## Arena Example
```veloc
int main() {
    VeloC_Arena arena = VeloC_Arena::create(1024 * 1024);
    defer arena.destroy();
    i32* buf = arena.alloc_array<i32>(100);
    buf[0] = 42;
    printf("First: %d\n", buf[0]);
    arena.reset();
    return 0;
}
```
