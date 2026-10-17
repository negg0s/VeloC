# VeloC-Render Application Report

## Architecture
- **Language**: VeloC 1.0 (Transpiled to C++20 via Clang)
- **Lines of Code**: 130 LOC (`apps/veloc-render/src/main.vc`)
- **Compilation Time**: 2.92 seconds (Clang -O3)
- **Transpile Time**: 4.6 ms

## Components
1. `EcsWorld`: Structure-of-Arrays (SoA) component manager with contiguous memory vectors for positions, velocities, radii, visibility flags, and light buffers.
2. `update_physics`: Linear kinematics simulation iterating over SoA velocity and position channels.
3. `frustum_cull`: Near/far and field-of-view cone test filtering visible entities.
4. `compute_lighting`: Dynamic inverse-square falloff light energy accumulation with surface normal dot products.

## Benchmark Results (i5-10400F)
- **Scale**: 100,000 active entities.
- **Simulation**: 100 consecutive full frames.
- **Total Time**: 30.54 ms.
- **Average Frame Time**: 0.305 ms.
- **Frame Rate**: 3,274.4 FPS (far exceeding the 60 FPS real-time baseline).
- **Culling Rejection**: Rejects ~94.7% of off-screen entities per frame.

## Language Pains & Lessons Learned
- **Builtin Aligned Math Types**: VeloC's standard library already supplies `Vec3` (16-byte aligned for SSE/AVX vector operations). Declaring a duplicate `struct Vec3` caused a collision with `veloc.h`, highlighting the need for namespacing and explicit shadow warnings in the diagnostic engine.
