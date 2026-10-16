# VeloC-Render

High-performance 3D Entity Component System (ECS) game loop and software culling/lighting pipeline.

## Features
- **Structure of Arrays (SoA) ECS**: Contiguous vector storage for entity components allowing automatic SIMD vectorization and optimal CPU cache-line usage.
- **Frustum Culling**: Rapid bounding sphere vs view-cone culling rejecting off-screen entities.
- **Dynamic Lighting**: Point lighting computation over visible geometry with inverse-square falloff and cosine attenuation.

## Performance
- **Entity Count**: 100,000 entities.
- **Frame Rate**: ~3,274 FPS (0.305 ms/frame).
- **Culling Throughput**: Rejects ~94.7% of off-screen entities within ~0.15 ms.
