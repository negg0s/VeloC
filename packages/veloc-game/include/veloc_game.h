#ifndef VELOC_GAME_H
#define VELOC_GAME_H

#include <veloc.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
#include <chrono>

namespace veloc {
namespace game {

    // ========================================================================
    // 1. Entity Definition & Generation Handle
    // ========================================================================
    typedef u32 Entity;
    static constexpr u32 ENTITY_INDEX_BITS = 20;
    static constexpr u32 ENTITY_INDEX_MASK = (1 << ENTITY_INDEX_BITS) - 1;
    static constexpr u32 ENTITY_GEN_SHIFT = ENTITY_INDEX_BITS;
    static constexpr Entity NULL_ENTITY = 0xFFFFFFFF;

    static VELOC_INLINE u32 entity_index(Entity e) { return e & ENTITY_INDEX_MASK; }
    static VELOC_INLINE u32 entity_gen(Entity e) { return e >> ENTITY_GEN_SHIFT; }
    static VELOC_INLINE Entity make_entity(u32 idx, u32 gen) { return (gen << ENTITY_GEN_SHIFT) | (idx & ENTITY_INDEX_MASK); }

    // ========================================================================
    // 2. High-Performance Sparse-Set Component Pool
    // O(1) insert, O(1) remove (swap-with-last), O(1) lookup, 100% linear cache-friendly iteration
    // ========================================================================
    template <typename T, usize Cap = 1048576>
    class SparseSet {
    public:
        T dense[Cap];
        Entity dense_entity[Cap];
        u32 sparse[Cap];
        usize count;

        SparseSet() : count(0) {
            std::memset(sparse, 0xFF, sizeof(sparse));
        }

        VELOC_INLINE bool has(Entity e) const {
            u32 idx = entity_index(e);
            if (idx >= Cap) return false;
            u32 dense_idx = sparse[idx];
            return dense_idx < count && dense_entity[dense_idx] == e;
        }

        VELOC_INLINE T* get(Entity e) {
            u32 idx = entity_index(e);
            u32 dense_idx = sparse[idx];
            if (dense_idx < count && dense_entity[dense_idx] == e) {
                return &dense[dense_idx];
            }
            return nullptr;
        }

        VELOC_INLINE const T* get(Entity e) const {
            u32 idx = entity_index(e);
            u32 dense_idx = sparse[idx];
            if (dense_idx < count && dense_entity[dense_idx] == e) {
                return &dense[dense_idx];
            }
            return nullptr;
        }

        VELOC_INLINE T* emplace(Entity e, const T& comp) {
            u32 idx = entity_index(e);
            if (has(e)) {
                dense[sparse[idx]] = comp;
                return &dense[sparse[idx]];
            }
            if (count >= Cap) return nullptr;
            u32 dense_idx = (u32)count++;
            dense[dense_idx] = comp;
            dense_entity[dense_idx] = e;
            sparse[idx] = dense_idx;
            return &dense[dense_idx];
        }

        VELOC_INLINE bool remove(Entity e) {
            if (!has(e)) return false;
            u32 idx = entity_index(e);
            u32 dense_idx = sparse[idx];
            u32 last_idx = (u32)(--count);

            if (dense_idx != last_idx) {
                // Swap with last dense element
                dense[dense_idx] = dense[last_idx];
                dense_entity[dense_idx] = dense_entity[last_idx];
                sparse[entity_index(dense_entity[last_idx])] = dense_idx;
            }
            sparse[idx] = 0xFFFFFFFF;
            return true;
        }

        VELOC_INLINE usize size() const { return count; }
        VELOC_INLINE T* begin() { return dense; }
        VELOC_INLINE T* end() { return dense + count; }
        VELOC_INLINE const T* begin() const { return dense; }
        VELOC_INLINE const T* end() const { return dense + count; }
    };

    // ========================================================================
    // 3. Game World Manager
    // ========================================================================
    template <usize MaxEntities = 1048576>
    class GameWorld {
    private:
        u32 generations[MaxEntities];
        u32 free_indices[MaxEntities];
        usize free_count;
        usize entity_count;

    public:
        GameWorld() : free_count(0), entity_count(0) {
            std::memset(generations, 0, sizeof(generations));
        }

        Entity spawn() {
            u32 idx;
            if (free_count > 0) {
                idx = free_indices[--free_count];
            } else {
                idx = (u32)entity_count++;
            }
            return make_entity(idx, generations[idx]);
        }

        bool is_alive(Entity e) const {
            u32 idx = entity_index(e);
            if (idx >= entity_count) return false;
            return generations[idx] == entity_gen(e);
        }

        bool destroy(Entity e) {
            if (!is_alive(e)) return false;
            u32 idx = entity_index(e);
            generations[idx]++; // Invalidate all handles
            free_indices[free_count++] = idx;
            return true;
        }

        usize alive_count() const {
            return entity_count - free_count;
        }
    };

    // ========================================================================
    // 4. Fixed Timestep Clock with State Interpolation Factor (Alpha)
    // ========================================================================
    class FixedTimestep {
    private:
        double dt;
        double accumulator;
        std::chrono::high_resolution_clock::time_point last_time;

    public:
        FixedTimestep(double target_dt = 1.0 / 60.0)
            : dt(target_dt), accumulator(0.0), last_time(std::chrono::high_resolution_clock::now()) {}

        void reset() {
            accumulator = 0.0;
            last_time = std::chrono::high_resolution_clock::now();
        }

        // Returns true as long as fixed simulation steps need to run
        bool step() {
            auto now = std::chrono::high_resolution_clock::now();
            double frame_time = std::chrono::duration<double>(now - last_time).count();
            last_time = now;
            if (frame_time > 0.25) frame_time = 0.25; // Clamp spiral of death
            accumulator += frame_time;

            if (accumulator >= dt) {
                accumulator -= dt;
                return true;
            }
            return false;
        }

        double alpha() const {
            return accumulator / dt;
        }

        double fixed_dt() const {
            return dt;
        }
    };

    // ========================================================================
    // 5. Chrome Tracing Frame Profiler (Exportable to chrome://tracing & Speedscope)
    // ========================================================================
    struct ProfileSpan {
        const char* name;
        u64 start_us;
        u64 duration_us;
    };

    class FrameProfiler {
    private:
        std::vector<ProfileSpan> spans;
        std::chrono::high_resolution_clock::time_point base_time;

    public:
        FrameProfiler() : base_time(std::chrono::high_resolution_clock::now()) {
            spans.reserve(4096);
        }

        u64 now_us() {
            auto now = std::chrono::high_resolution_clock::now();
            return std::chrono::duration_cast<std::chrono::microseconds>(now - base_time).count();
        }

        void record(const char* name, u64 start_us, u64 dur_us) {
            spans.push_back({name, start_us, dur_us});
        }

        bool export_chrome_trace(const char* filepath) const {
            FILE* f = fopen(filepath, "w");
            if (!f) return false;
            fprintf(f, "{\"traceEvents\": [\n");
            for (usize i = 0; i < spans.size(); i++) {
                const auto& s = spans[i];
                fprintf(f, "  {\"name\": \"%s\", \"ph\": \"X\", \"ts\": %llu, \"dur\": %llu, \"pid\": 1, \"tid\": 1}%s\n",
                        s.name, (unsigned long long)s.start_us, (unsigned long long)s.duration_us,
                        (i + 1 < spans.size()) ? "," : "");
            }
            fprintf(f, "]}\n");
            fclose(f);
            return true;
        }

        void clear() {
            spans.clear();
        }
    };

    // ========================================================================
    // 6. Spatial Hash Grid (2D Broadphase Collision Detection)
    // ========================================================================
    struct SpatialCellEntry {
        Entity entity;
        u32 next;
    };

    template <usize GridWidth = 128, usize GridHeight = 128, usize MaxEntries = 262144>
    class SpatialGrid2D {
    private:
        f32 cell_size;
        u32 head[GridWidth * GridHeight];
        SpatialCellEntry entries[MaxEntries];
        usize count;

    public:
        SpatialGrid2D(f32 size = 32.0f) : cell_size(size), count(0) {
            clear();
        }

        void clear() {
            std::memset(head, 0xFF, sizeof(head));
            count = 0;
        }

        VELOC_INLINE void insert(Entity e, f32 x, f32 y) {
            if (count >= MaxEntries) return;
            i32 cx = (i32)(x / cell_size);
            i32 cy = (i32)(y / cell_size);
            if (cx < 0 || cx >= (i32)GridWidth || cy < 0 || cy >= (i32)GridHeight) return;

            u32 cell_idx = (u32)(cy * GridWidth + cx);
            u32 entry_idx = (u32)count++;
            entries[entry_idx].entity = e;
            entries[entry_idx].next = head[cell_idx];
            head[cell_idx] = entry_idx;
        }

        template <typename Func>
        VELOC_INLINE void query_cell(f32 x, f32 y, Func&& fn) const {
            i32 cx = (i32)(x / cell_size);
            i32 cy = (i32)(y / cell_size);
            if (cx < 0 || cx >= (i32)GridWidth || cy < 0 || cy >= (i32)GridHeight) return;

            u32 cell_idx = (u32)(cy * GridWidth + cx);
            u32 curr = head[cell_idx];
            while (curr != 0xFFFFFFFF) {
                fn(entries[curr].entity);
                curr = entries[curr].next;
            }
        }
    };

    // ========================================================================
    // 7. AVX2 SIMD Particle System (100k+ particles with zero-overhead updates)
    // ========================================================================
    struct alignas(32) SIMDParticles2D {
        usize count;
        f32* x;
        f32* y;
        f32* vx;
        f32* vy;
        f32* life;

        static SIMDParticles2D create(usize num_particles) {
            SIMDParticles2D p;
            p.count = num_particles;
            usize bytes = num_particles * sizeof(f32);
            p.x = (f32*)veloc_aligned_alloc(32, bytes);
            p.y = (f32*)veloc_aligned_alloc(32, bytes);
            p.vx = (f32*)veloc_aligned_alloc(32, bytes);
            p.vy = (f32*)veloc_aligned_alloc(32, bytes);
            p.life = (f32*)veloc_aligned_alloc(32, bytes);
            return p;
        }

        void update(f32 dt, f32 gravity_y = -9.81f) {
            f32x8 dt_v = f32x8_set1(dt);
            f32x8 gy_v = f32x8_set1(gravity_y * dt);
            f32x8 decay_v = f32x8_set1(dt * 0.5f);

            usize i = 0;
            for (; i + 8 <= count; i += 8) {
                f32x8 vx_v = f32x8_load(&vx[i]);
                f32x8 vy_v = f32x8_load(&vy[i]);
                f32x8 x_v = f32x8_load(&x[i]);
                f32x8 y_v = f32x8_load(&y[i]);
                f32x8 l_v = f32x8_load(&life[i]);

                // vy += gravity * dt
                vy_v = _mm256_add_ps(vy_v, gy_v);
                // x += vx * dt; y += vy * dt
                x_v = _mm256_fmadd_ps(vx_v, dt_v, x_v);
                y_v = _mm256_fmadd_ps(vy_v, dt_v, y_v);
                // life -= decay
                l_v = _mm256_sub_ps(l_v, decay_v);

                f32x8_store(&vx[i], vx_v);
                f32x8_store(&vy[i], vy_v);
                f32x8_store(&x[i], x_v);
                f32x8_store(&y[i], y_v);
                f32x8_store(&life[i], l_v);
            }

            for (; i < count; i++) {
                vy[i] += gravity_y * dt;
                x[i] += vx[i] * dt;
                y[i] += vy[i] * dt;
                life[i] -= dt * 0.5f;
            }
        }
    };

} // namespace game
} // namespace veloc

// Expose in veloc namespace
using veloc::game::Entity;
using veloc::game::SparseSet;
using veloc::game::GameWorld;
using veloc::game::FixedTimestep;
using veloc::game::FrameProfiler;
using veloc::game::SpatialGrid2D;
using veloc::game::SIMDParticles2D;

#endif // VELOC_GAME_H
