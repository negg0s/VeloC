# VeloC-PathTracer

High-throughput Monte Carlo path tracer with multi-bounce global illumination, emissive lighting, reflection, and parallel tile dispatching.

## Features
- **Monte Carlo Sampling**: Cosine-weighted hemisphere scattering for soft indirect diffuse lighting.
- **Surface Materials**: Lambertian diffuse, perfect specular mirror reflection, and emissive light sources.
- **Multi-Threaded Work Partitioning**: Workload partitioned across hardware concurrency threads (`std::thread::hardware_concurrency()`).
- **Fast Pseudo-Random Generator**: Inline LCG RNG generating uniform random numbers per sample without mutex contention.

## Performance
- **Throughput**: ~40.13 Million Rays/sec (Intel Core i5-10400F, 12 threads).
- **Latency**: 160x120 frame at 8 samples/pixel with 4 bounces completes in 6.30 ms.
