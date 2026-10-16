#include "D:/VeloC/include/veloc.h"

// [VeloC module declaration]

// Auto-generated VeloC Struct-of-Arrays (SoA) for SIMD acceleration
struct Particle_SoA {
    usize capacity;
    usize count;
    f32* VELOC_RESTRICT x;
    f32* VELOC_RESTRICT y;
    f32* VELOC_RESTRICT vx;
    f32* VELOC_RESTRICT vy;

    static Particle_SoA create(usize cap) {
        Particle_SoA s;
        s.capacity = cap;
        s.count = 0;
        s.x = (f32*)veloc_aligned_alloc(32, sizeof(f32) * cap);
        s.y = (f32*)veloc_aligned_alloc(32, sizeof(f32) * cap);
        s.vx = (f32*)veloc_aligned_alloc(32, sizeof(f32) * cap);
        s.vy = (f32*)veloc_aligned_alloc(32, sizeof(f32) * cap);
        return s;
    }

    VELOC_INLINE void push(f32 val_x, f32 val_y, f32 val_vx, f32 val_vy) {
        if (count < capacity) {
            this->x[count] = val_x;
            this->y[count] = val_y;
            this->vx[count] = val_vx;
            this->vy[count] = val_vy;
            count++;
        }
    }

    void destroy() {
        if (x) { veloc_aligned_free(x); x = NULL; }
        if (y) { veloc_aligned_free(y); y = NULL; }
        if (vx) { veloc_aligned_free(vx); vx = NULL; }
        if (vy) { veloc_aligned_free(vy); vy = NULL; }
        capacity = 0;
        count = 0;
    }

    // Auto-generated Reflection: to_json()
    std::string to_json(usize i) const {
        if (i >= count) return "{}";
        std::ostringstream ss;
        ss << "{";
        ss << "\"x\": " << this->x[i] << ", ";
        ss << "\"y\": " << this->y[i] << ", ";
        ss << "\"vx\": " << this->vx[i] << ", ";
        ss << "\"vy\": " << this->vy[i] << "";
        ss << "}";
        return ss.str();
    }

    static const char* type_name() { return "Particle_SoA"; }
    static usize field_count() { return 4; }
};


// Ultra-fast AVX2 SIMD Kernel: 64 particles per loop + Non-Temporal Streaming Stores
VELOC_INLINE void update_particles_avx2_stream(f32* VELOC_RESTRICT x, f32* VELOC_RESTRICT y,
                                              const f32* VELOC_RESTRICT vx, const f32* VELOC_RESTRICT vy,
                                              usize start, usize end, f32 dt) {
    f32x8 dt_vec = f32x8_set1(dt);
    usize i = start;
    usize count = end;

    // Unroll 8x (64 particles per (iteration).unwrap())
    for (; i + 63 < count; i += 64) {
        veloc_prefetch(&x[i + 128]);
        veloc_prefetch(&y[i + 128]);

        // Load X
        f32x8 px0 = f32x8_load(&x[i]);
        f32x8 px1 = f32x8_load(&x[i + 8]);
        f32x8 px2 = f32x8_load(&x[i + 16]);
        f32x8 px3 = f32x8_load(&x[i + 24]);
        f32x8 px4 = f32x8_load(&x[i + 32]);
        f32x8 px5 = f32x8_load(&x[i + 40]);
        f32x8 px6 = f32x8_load(&x[i + 48]);
        f32x8 px7 = f32x8_load(&x[i + 56]);

        // Load VX
        f32x8 pvx0 = f32x8_load(&vx[i]);
        f32x8 pvx1 = f32x8_load(&vx[i + 8]);
        f32x8 pvx2 = f32x8_load(&vx[i + 16]);
        f32x8 pvx3 = f32x8_load(&vx[i + 24]);
        f32x8 pvx4 = f32x8_load(&vx[i + 32]);
        f32x8 pvx5 = f32x8_load(&vx[i + 40]);
        f32x8 pvx6 = f32x8_load(&vx[i + 48]);
        f32x8 pvx7 = f32x8_load(&vx[i + 56]);

        // FMA & Stream store directly to RAM
        f32x8_stream_aligned(&x[i],      f32x8_fmadd(pvx0, dt_vec, px0));
        f32x8_stream_aligned(&x[i + 8],  f32x8_fmadd(pvx1, dt_vec, px1));
        f32x8_stream_aligned(&x[i + 16], f32x8_fmadd(pvx2, dt_vec, px2));
        f32x8_stream_aligned(&x[i + 24], f32x8_fmadd(pvx3, dt_vec, px3));
        f32x8_stream_aligned(&x[i + 32], f32x8_fmadd(pvx4, dt_vec, px4));
        f32x8_stream_aligned(&x[i + 40], f32x8_fmadd(pvx5, dt_vec, px5));
        f32x8_stream_aligned(&x[i + 48], f32x8_fmadd(pvx6, dt_vec, px6));
        f32x8_stream_aligned(&x[i + 56], f32x8_fmadd(pvx7, dt_vec, px7));

        // Load Y
        f32x8 py0 = f32x8_load(&y[i]);
        f32x8 py1 = f32x8_load(&y[i + 8]);
        f32x8 py2 = f32x8_load(&y[i + 16]);
        f32x8 py3 = f32x8_load(&y[i + 24]);
        f32x8 py4 = f32x8_load(&y[i + 32]);
        f32x8 py5 = f32x8_load(&y[i + 40]);
        f32x8 py6 = f32x8_load(&y[i + 48]);
        f32x8 py7 = f32x8_load(&y[i + 56]);

        // Load VY
        f32x8 pvy0 = f32x8_load(&vy[i]);
        f32x8 pvy1 = f32x8_load(&vy[i + 8]);
        f32x8 pvy2 = f32x8_load(&vy[i + 16]);
        f32x8 pvy3 = f32x8_load(&vy[i + 24]);
        f32x8 pvy4 = f32x8_load(&vy[i + 32]);
        f32x8 pvy5 = f32x8_load(&vy[i + 40]);
        f32x8 pvy6 = f32x8_load(&vy[i + 48]);
        f32x8 pvy7 = f32x8_load(&vy[i + 56]);

        // FMA & Stream store directly to RAM
        f32x8_stream_aligned(&y[i],      f32x8_fmadd(pvy0, dt_vec, py0));
        f32x8_stream_aligned(&y[i + 8],  f32x8_fmadd(pvy1, dt_vec, py1));
        f32x8_stream_aligned(&y[i + 16], f32x8_fmadd(pvy2, dt_vec, py2));
        f32x8_stream_aligned(&y[i + 24], f32x8_fmadd(pvy3, dt_vec, py3));
        f32x8_stream_aligned(&y[i + 32], f32x8_fmadd(pvy4, dt_vec, py4));
        f32x8_stream_aligned(&y[i + 40], f32x8_fmadd(pvy5, dt_vec, py5));
        f32x8_stream_aligned(&y[i + 48], f32x8_fmadd(pvy6, dt_vec, py6));
        f32x8_stream_aligned(&y[i + 56], f32x8_fmadd(pvy7, dt_vec, py7));
    }

    // Remainder loop
    for (; i < count; i++) {
        x[i] += vx[i] * dt;
        y[i] += vy[i] * dt;
    }
}

int main() {
    printf("==========================================================\n");
    printf("    VeloC HYPER-TURBO Engine (AVX2 Stream + 12 Threads)   \n");
    printf("==========================================================\n");

    const usize NUM_PARTICLES = 5000000;
    const int STEPS = 20;

    printf("Allocating and initializing 5,000,000 particles (Aligned SoA)...\n");
    Particle_SoA particles = Particle_SoA::create(NUM_PARTICLES);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { particles.destroy(); };

    for (usize i = 0; i < NUM_PARTICLES; i++) {
        particles.x[i] = (f32)(i % 100);
        particles.y[i] = (f32)(i % 200);
        particles.vx[i] = 1.5f;
        particles.vy[i] = -0.5f;
    }
    particles.count = NUM_PARTICLES;

    // Warm-up Threadpool
    veloc::parallel_for(10000, 12, [&](usize s, usize e){});

    VeloC_Timer timer;
    printf("Simulating 20 steps with 12 lock-free workers & 64-unroll FMA...\n");

    timer.start();
    for (int step = 0; step < STEPS; step++) {
        veloc::parallel_for(NUM_PARTICLES, 12, [&](usize start, usize end) {
            update_particles_avx2_stream(particles.x, particles.y, particles.vx, particles.vy, start, end, 0.016f);
        });
        veloc_sfence();
    }
    f64 total_ms = timer.elapsed_ms();
    f64 per_step_ms = total_ms / STEPS;
    f64 throughput = ((f64)NUM_PARTICLES * STEPS) / (total_ms / 1000.0) / 1e6;

    printf("Complete!\n");
    printf("HYPER-TURBO Total Time:     %.2f ms\n", total_ms);
    printf("HYPER-TURBO Time per step:  %.3f ms\n", per_step_ms);
    printf("HYPER-TURBO Throughput:     %.2f MILLION particles/sec\n", throughput);
    printf("%s\n", "Sample Particle 0:    pos = (%.2f, %.2f)", particles.x[0], particles.y[0]);
    printf("%s\n", "Sample Particle 1000: pos = (%.2f, %.2f)", particles.x[1000], particles.y[1000]);
    printf("==========================================================\n");

    return 0;
}