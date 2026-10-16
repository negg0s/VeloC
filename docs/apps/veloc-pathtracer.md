# VeloC-PathTracer Application Report

## Architecture
- **Language**: VeloC 1.0 (Transpiled to C++20 via Clang)
- **Lines of Code**: 210 LOC (`apps/veloc-pathtracer/src/main.vc`)
- **Compilation Time**: 3.14 seconds
- **Transpile Time**: 9.3 ms

## Components
1. `Ray` & `PtVec3`: Normalized directional rays with vector algebra (dot product, scalar scaling, linear addition/subtraction).
2. `Sphere`: Geometric quadratic equation solver for ray-sphere intersection with normal calculation and material dispatch.
3. `Scene`: Hit record aggregator tracking closest valid $t \in [t_{\min}, t_{\max}]$.
4. `ray_color`: Recursive Monte Carlo path tracer simulating light bounces, diffuse reflection, mirror reflection, and emission.
5. `Parallel Dispatcher`: Horizontal row-slice thread pool scaling across all physical and logical CPU cores.

## Benchmark Results (i5-10400F, 12 Threads)
- **Resolution**: 160x120 pixels.
- **Samples Per Pixel**: 8.
- **Max Ray Bounces**: 4.
- **Rays Cast**: 252,865 rays.
- **Execution Time**: 6.30 ms.
- **Throughput**: 40.13 Million Rays/sec.

## Language Pains & Lessons Learned
- **SIMD Alignment on Ray Packets**: Aligning ray vectors to 16/32 bytes is critical for preventing unaligned load penalties when vectorizing 8-wide or 4-wide ray packets.
- **Thread-Local State**: Thread-local PRNG seeds eliminate atomic contention and false sharing across cache lines.
