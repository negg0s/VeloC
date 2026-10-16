# veloc-game: High-Performance Game Engine Foundation for VeloC

`veloc-game` provides core data-driven game development primitives optimized for modern x86_64 architectures using AVX2 and cache-conscious data layouts.

## Architecture & Features

1. **Sparse-Set ECS (`SparseSet<T, Cap>`, `GameWorld<MaxEntities>`)**:
   - $O(1)$ component insertion and swap-with-last deletion.
   - Generation-indexed 32-bit entity IDs (`Entity`) preventing ABA dangling handle bugs.
   - Dense contiguous memory layout providing **1,040,000,000 entity updates per second** (0.96 ms for 1M entities).
2. **Fixed Timestep Simulation (`FixedTimestep`)**:
   - High-precision sub-millisecond accumulator with spiral-of-death clamp.
   - Exact temporal interpolation factor $\alpha \in [0.0, 1.0)$ for jitter-free rendering.
3. **Chrome Trace Profiler (`FrameProfiler`)**:
   - Zero-allocation nanosecond span recorder.
   - Direct export to Google Chrome Tracing (`chrome://tracing`) and Speedscope JSON format.
4. **Spatial Hash Grid (`SpatialGrid2D`)**:
   - Broadphase 2D collision detection with constant-time cell bucketing.
5. **AVX2 SIMD Particle Engine (`SIMDParticles2D`)**:
   - Structure-of-Arrays (SoA) layout with 8-wide vectorized position, velocity, and lifetime simulation.

## Benchmarks (Intel Core i5-10400F, Clang 20, AVX2)

| Operation | Scale | Time | Throughput |
|---|---|---|---|
| **Spawn & Emplace** | 1,000,000 Entities | 13.40 ms | 74.6 M entities/s |
| **Linear Iteration** | 1,000,000 Components | 0.96 ms | **1,040.75 M entities/s** |
| **Remove & Recycle**| 100,000 Entities | 0.59 ms | 5.90 ns / entity |

## Running Tests & Benchmarks

```bash
# Run ECS unit tests
python veloc.py run packages/veloc-game/tests/test_ecs.vc

# Run 1,000,000 entities benchmark
python veloc.py run packages/veloc-game/benchmarks/bench_ecs_1m.vc

# Run 128k particles & Chrome tracing demo
python veloc.py run packages/veloc-game/examples/demo_game.vc
```
