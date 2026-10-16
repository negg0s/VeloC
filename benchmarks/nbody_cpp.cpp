#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>

// Standard C++ OOP 3D Particle
struct Particle3D {
    float x, y, z;
    float vx, vy, vz;
    float mass;

    Particle3D(float px, float py, float pz, float m)
        : x(px), y(py), z(pz), vx(0), vy(0), vz(0), mass(m) {}
};

void compute_forces_standard(std::vector<Particle3D>& p, float dt) {
    const float G = 6.674e-5f;
    const float EPS = 1e-3f;
    size_t n = p.size();

    for (size_t i = 0; i < n; i++) {
        float fx = 0, fy = 0, fz = 0;
        for (size_t j = 0; j < n; j++) {
            if (i == j) continue;
            float dx = p[j].x - p[i].x;
            float dy = p[j].y - p[i].y;
            float dz = p[j].z - p[i].z;
            float dist_sq = dx*dx + dy*dy + dz*dz + EPS;
            float inv_dist = 1.0f / std::sqrt(dist_sq);
            float inv_dist3 = inv_dist * inv_dist * inv_dist;
            float force = G * p[j].mass * inv_dist3;

            fx += force * dx;
            fy += force * dy;
            fz += force * dz;
        }
        p[i].vx += fx * dt;
        p[i].vy += fy * dt;
        p[i].vz += fz * dt;
        p[i].x += p[i].vx * dt;
        p[i].y += p[i].vy * dt;
        p[i].z += p[i].vz * dt;
    }
}

int main() {
    const size_t NUM_PARTICLES = 16384; // 16K particles = 268 Million interactions
    std::cout << "[Standard C++] Simulating N-Body (16,384 particles)..." << std::endl;

    std::vector<Particle3D> particles;
    particles.reserve(NUM_PARTICLES);
    for (size_t i = 0; i < NUM_PARTICLES; i++) {
        particles.emplace_back((float)(i % 100), (float)(i % 200), (float)(i % 50), 10.0f);
    }

    auto t0 = std::chrono::high_resolution_clock::now();
    compute_forces_standard(particles, 0.016f);
    auto t1 = std::chrono::high_resolution_clock::now();

    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    std::cout << "[Standard C++] N-Body Step Time: " << ms << " ms" << std::endl;
    std::cout << "[Standard C++] Particle 0 pos: (" << particles[0].x << ", " << particles[0].y << ", " << particles[0].z << ")" << std::endl;
    return 0;
}
