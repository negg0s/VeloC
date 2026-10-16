#include "D:/VeloC/include/veloc.h"

// VeloC Example: 5 Million Particles Simulation
// Demonstrates SoA (Struct-of-Arrays), VELOC_RESTRICT SIMD vectorization, defer, and Arena
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


// Vectorized physics update: VELOC_RESTRICT informs compiler pointers cannot overlap
VELOC_INLINE void update_particles(f32* VELOC_RESTRICT x, f32* VELOC_RESTRICT y, 
                                  const f32* VELOC_RESTRICT vx, const f32* VELOC_RESTRICT vy, 
                                  usize count, f32 dt) {
    #pragma clang loop vectorize(enable)
    for (usize i = 0; i < count; i++) {
        x[i] += vx[i] * dt;
        y[i] += vy[i] * dt;
    }
}

int main() {
    printf("==================================================\n");
    printf("           VeloC High-Performance Engine          \n");
    printf("==================================================\n");

    const usize NUM_PARTICLES = 5000000; // 5 Million (particles).unwrap()
    printf("Initializing %llu particles using SoA SIMD layout...\n", (unsigned long long)NUM_PARTICLES);

    // Create SoA particle storage with 32-byte SIMD alignment
    Particle_SoA particles = Particle_SoA::create(NUM_PARTICLES);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { particles.destroy(); }; // Zero-cost defer ensures automatic cleanup

    // Fill particles
    for (usize i = 0; i < NUM_PARTICLES; i++) {
        particles.x[i] = (f32)(i % 100);
        particles.y[i] = (f32)(i % 200);
        particles.vx[i] = 1.5f;
        particles.vy[i] = -0.5f;
    }
    particles.count = NUM_PARTICLES;

    // Test bump Arena Allocator
    VeloC_Arena arena = VeloC_Arena::create(16 * 1024 * 1024); // 16 MB arena
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { arena.destroy(); };
    f32* scratch = arena.alloc_array<f32>(100000);
    scratch[0] = 42.0f;
    printf("Arena allocation succeeded: scratch[0] = %.1f (zero-lock instant allocation)\n", scratch[0]);

    // Benchmark physics step
    VeloC_Timer timer;
    const int STEPS = 20;
    printf("Running %d physics simulation steps...\n", STEPS);

    timer.start();
    for (int step = 0; step < STEPS; step++) {
        update_particles(particles.x, particles.y, particles.vx, particles.vy, particles.count, 0.016f);
    }
    f64 total_ms = timer.elapsed_ms();
    f64 per_step_ms = total_ms / STEPS;
    f64 particles_per_sec = ((f64)NUM_PARTICLES * STEPS) / (total_ms / 1000.0) / 1e6;

    printf("Done!\n");
    printf("Total Time for %d steps: %.2f ms\n", STEPS, total_ms);
    printf("Average Time per step:    %.3f ms\n", per_step_ms);
    printf("Throughput:               %.2f Million particles/sec\n", particles_per_sec);
    printf("%s\n", "Sample Particle 0: pos = (%.2f, %.2f)", particles.x[0], particles.y[0]);
    printf("%s\n", "Sample Particle 1000: pos = (%.2f, %.2f)", particles.x[1000], particles.y[1000]);
    printf("==================================================\n");

    return 0;
}