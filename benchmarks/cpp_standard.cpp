#include <iostream>
#include <vector>
#include <chrono>
#include <numeric>

// Standard C++ OOP Array-of-Structures (AoS)
struct Particle {
    float x;
    float y;
    float vx;
    float vy;

    Particle(float px, float py, float pvx, float pvy)
        : x(px), y(py), vx(pvx), vy(pvy) {}
};

void update_particles_standard(std::vector<Particle>& particles, float dt) {
    // Standard C++ loop over AoS (often causes cache misses & aliasing issues)
    for (auto& p : particles) {
        p.x += p.vx * dt;
        p.y += p.vy * dt;
    }
}

int main() {
    const size_t NUM_PARTICLES = 5000000;
    const int STEPS = 20;

    std::cout << "[Standard C++] Initializing " << NUM_PARTICLES << " particles..." << std::endl;
    auto t0 = std::chrono::high_resolution_clock::now();

    std::vector<Particle> particles;
    particles.reserve(NUM_PARTICLES);
    for (size_t i = 0; i < NUM_PARTICLES; i++) {
        particles.emplace_back((float)(i % 100), (float)(i % 200), 1.5f, -0.5f);
    }

    auto t1 = std::chrono::high_resolution_clock::now();
    double init_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    std::cout << "[Standard C++] Init Time: " << init_ms << " ms" << std::endl;

    std::cout << "[Standard C++] Running " << STEPS << " simulation steps..." << std::endl;
    auto t_sim_start = std::chrono::high_resolution_clock::now();

    for (int s = 0; s < STEPS; s++) {
        update_particles_standard(particles, 0.016f);
    }

    auto t_sim_end = std::chrono::high_resolution_clock::now();
    double sim_ms = std::chrono::duration<double, std::milli>(t_sim_end - t_sim_start).count();

    std::cout << "[Standard C++] Simulation Time: " << sim_ms << " ms" << std::endl;
    std::cout << "[Standard C++] Per step: " << (sim_ms / STEPS) << " ms" << std::endl;
    std::cout << "[Standard C++] Sample pos: (" << particles[0].x << ", " << particles[0].y << ")" << std::endl;

    return 0;
}
