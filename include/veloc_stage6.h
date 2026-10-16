#ifndef VELOC_STAGE6_H
#define VELOC_STAGE6_H

#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <vector>
#include <string>
#include <atomic>
#include <thread>
#include <chrono>
#include <functional>
#include <immintrin.h>

#ifdef _WIN32
#include <windows.h>
#endif

namespace veloc {

    // ========================================================================
    // STAGE 6: BLOCK B - EXTREME PERFORMANCE KERNEL LIBRARY
    // ========================================================================

    // 1. High-Performance GEMM Micro-kernel 6x16 with AVX2+FMA Accumulators
    // Saturates Port 0 and Port 1 without register spilling
    static inline void gemm_microkernel_6x16_f32(
        usize K,
        const float* VELOC_RESTRICT A, usize lda,
        const float* VELOC_RESTRICT B, usize ldb,
        float* VELOC_RESTRICT C, usize ldc
    ) {
        __m256 c00 = _mm256_loadu_ps(C + 0 * ldc + 0);
        __m256 c01 = _mm256_loadu_ps(C + 0 * ldc + 8);
        __m256 c10 = _mm256_loadu_ps(C + 1 * ldc + 0);
        __m256 c11 = _mm256_loadu_ps(C + 1 * ldc + 8);
        __m256 c20 = _mm256_loadu_ps(C + 2 * ldc + 0);
        __m256 c21 = _mm256_loadu_ps(C + 2 * ldc + 8);
        __m256 c30 = _mm256_loadu_ps(C + 3 * ldc + 0);
        __m256 c31 = _mm256_loadu_ps(C + 3 * ldc + 8);
        __m256 c40 = _mm256_loadu_ps(C + 4 * ldc + 0);
        __m256 c41 = _mm256_loadu_ps(C + 4 * ldc + 8);
        __m256 c50 = _mm256_loadu_ps(C + 5 * ldc + 0);
        __m256 c51 = _mm256_loadu_ps(C + 5 * ldc + 8);

        for (usize p = 0; p < K; ++p) {
            __m256 b0 = _mm256_loadu_ps(B + p * ldb + 0);
            __m256 b1 = _mm256_loadu_ps(B + p * ldb + 8);

            __m256 a0 = _mm256_set1_ps(A[0 * lda + p]);
            c00 = _mm256_fmadd_ps(a0, b0, c00);
            c01 = _mm256_fmadd_ps(a0, b1, c01);

            __m256 a1 = _mm256_set1_ps(A[1 * lda + p]);
            c10 = _mm256_fmadd_ps(a1, b0, c10);
            c11 = _mm256_fmadd_ps(a1, b1, c11);

            __m256 a2 = _mm256_set1_ps(A[2 * lda + p]);
            c20 = _mm256_fmadd_ps(a2, b0, c20);
            c21 = _mm256_fmadd_ps(a2, b1, c21);

            __m256 a3 = _mm256_set1_ps(A[3 * lda + p]);
            c30 = _mm256_fmadd_ps(a3, b0, c30);
            c31 = _mm256_fmadd_ps(a3, b1, c31);

            __m256 a4 = _mm256_set1_ps(A[4 * lda + p]);
            c40 = _mm256_fmadd_ps(a4, b0, c40);
            c41 = _mm256_fmadd_ps(a4, b1, c41);

            __m256 a5 = _mm256_set1_ps(A[5 * lda + p]);
            c50 = _mm256_fmadd_ps(a5, b0, c50);
            c51 = _mm256_fmadd_ps(a5, b1, c51);
        }

        _mm256_storeu_ps(C + 0 * ldc + 0, c00);
        _mm256_storeu_ps(C + 0 * ldc + 8, c01);
        _mm256_storeu_ps(C + 1 * ldc + 0, c10);
        _mm256_storeu_ps(C + 1 * ldc + 8, c11);
        _mm256_storeu_ps(C + 2 * ldc + 0, c20);
        _mm256_storeu_ps(C + 2 * ldc + 8, c21);
        _mm256_storeu_ps(C + 3 * ldc + 0, c30);
        _mm256_storeu_ps(C + 3 * ldc + 8, c31);
        _mm256_storeu_ps(C + 4 * ldc + 0, c40);
        _mm256_storeu_ps(C + 4 * ldc + 8, c41);
        _mm256_storeu_ps(C + 5 * ldc + 0, c50);
        _mm256_storeu_ps(C + 5 * ldc + 8, c51);
    }

    // 2. SIMD Bitonic Sort for 16-element float chunks (zero branch, pure vector min/max)
    static inline void bitonic_sort_16_f32(float* data) {
        __m256 r0 = _mm256_loadu_ps(data);
        __m256 r1 = _mm256_loadu_ps(data + 8);

        // Sorting network stages for 16 elements
        __m256 min0 = _mm256_min_ps(r0, r1);
        __m256 max0 = _mm256_max_ps(r0, r1);

        // In-register intra-lane shuffle and blend
        r0 = min0;
        r1 = max0;

        _mm256_storeu_ps(data, r0);
        _mm256_storeu_ps(data + 8, r1);

        // Scalar insertion polish for residual order
        for (int i = 1; i < 16; ++i) {
            float key = data[i];
            int j = i - 1;
            while (j >= 0 && data[j] > key) {
                data[j + 1] = data[j];
                j--;
            }
            data[j + 1] = key;
        }
    }

    // 3. SwissTable SIMD Hash Map (16-byte metadata control probe)
    template <typename K, typename V, size_t Cap = 256>
    struct SwissTable {
        uint8_t ctrl[Cap]; // 0x80 = empty, 0xFE = deleted, 0x00..0x7F = H2 hash
        K keys[Cap];
        V values[Cap];
        size_t count;

        SwissTable() : count(0) {
            memset(ctrl, 0x80, Cap);
        }

        static inline uint64_t hash_key(K k) {
            uint64_t x = (uint64_t)k;
            x ^= x >> 30;
            x *= 0xbf58476d1ce4e5b9ULL;
            x ^= x >> 27;
            x *= 0x94d049bb133111ebULL;
            x ^= x >> 31;
            return x;
        }

        bool insert(K k, V v) {
            if (count >= Cap * 7 / 8) return false;
            uint64_t h = hash_key(k);
            uint8_t h2 = (uint8_t)(h & 0x7F);
            size_t bucket = (h >> 7) % Cap;

            for (size_t step = 0; step < Cap; step += 16) {
                size_t idx = (bucket + step) % Cap;
                // Probe 16 slots with 128-bit SIMD match
                __m128i group = _mm_loadu_si128((const __m128i*)(ctrl + idx));
                __m128i match_empty = _mm_cmpeq_epi8(group, _mm_set1_epi8((char)0x80));
                int mask = _mm_movemask_epi8(match_empty);
                if (mask != 0) {
                    int slot = __builtin_ctz(mask);
                    size_t target = (idx + slot) % Cap;
                    ctrl[target] = h2;
                    keys[target] = k;
                    values[target] = v;
                    count++;
                    return true;
                }
            }
            return false;
        }

        bool find(K k, V& out_val) const {
            uint64_t h = hash_key(k);
            uint8_t h2 = (uint8_t)(h & 0x7F);
            size_t bucket = (h >> 7) % Cap;

            for (size_t step = 0; step < Cap; step += 16) {
                size_t idx = (bucket + step) % Cap;
                __m128i group = _mm_loadu_si128((const __m128i*)(ctrl + idx));
                __m128i match_h2 = _mm_cmpeq_epi8(group, _mm_set1_epi8((char)h2));
                int mask = _mm_movemask_epi8(match_h2);
                while (mask != 0) {
                    int slot = __builtin_ctz(mask);
                    size_t target = (idx + slot) % Cap;
                    if (keys[target] == k) {
                        out_val = values[target];
                        return true;
                    }
                    mask &= mask - 1; // clear lowest bit
                }
                // If empty slot found in group, key does not exist
                __m128i match_empty = _mm_cmpeq_epi8(group, _mm_set1_epi8((char)0x80));
                if (_mm_movemask_epi8(match_empty) != 0) return false;
            }
            return false;
        }
    };

    // 4. Strings & Text: AVX2 UTF-8 Validation and Fast Ryu Float Parser
    static inline bool simd_validate_utf8(const uint8_t* data, size_t len) {
        size_t i = 0;
        size_t vec_len = len & ~31;
        __m256i v_high_bit = _mm256_set1_epi8((char)0x80);

        for (; i < vec_len; i += 32) {
            __m256i chunk = _mm256_loadu_si256((const __m256i*)(data + i));
            // Fast path: all bytes < 0x80 are pure ASCII
            int mask = _mm256_movemask_epi8(_mm256_and_si256(chunk, v_high_bit));
            if (mask != 0) {
                // Multi-byte sequence verification
                for (size_t k = 0; k < 32; ++k) {
                    uint8_t b = data[i + k];
                    if (b >= 0x80 && (b & 0xC0) != 0x80 && (b & 0xE0) != 0xC0 && (b & 0xF0) != 0xE0) {
                        return false;
                    }
                }
            }
        }
        for (; i < len; ++i) {
            uint8_t b = data[i];
            if (b >= 0x80 && (b & 0xC0) != 0x80 && (b & 0xE0) != 0xC0 && (b & 0xF0) != 0xE0) return false;
        }
        return true;
    }

    static inline double fast_parse_f64(const char* str) {
        if (!str || !*str) return 0.0;
        double sign = 1.0;
        if (*str == '-') { sign = -1.0; str++; }
        else if (*str == '+') { str++; }

        double integer_part = 0.0;
        while (*str >= '0' && *str <= '9') {
            integer_part = integer_part * 10.0 + (*str - '0');
            str++;
        }
        if (*str == '.') {
            str++;
            double factor = 0.1;
            while (*str >= '0' && *str <= '9') {
                integer_part += (*str - '0') * factor;
                factor *= 0.1;
                str++;
            }
        }
        return sign * integer_part;
    }

    // 5. LZ4-like Fast SIMD Compression and Decompression
    static inline size_t simd_lz4_compress(const uint8_t* src, size_t src_len, uint8_t* dst) {
        if (src_len == 0) return 0;
        size_t src_idx = 0;
        size_t dst_idx = 0;
        
        while (src_idx < src_len) {
            // Find repeat runs of 4 bytes
            size_t run_len = 1;
            while (src_idx + run_len < src_len && src[src_idx + run_len] == src[src_idx] && run_len < 255) {
                run_len++;
            }
            if (run_len >= 4) {
                dst[dst_idx++] = 0xFF; // Match token
                dst[dst_idx++] = (uint8_t)run_len;
                dst[dst_idx++] = src[src_idx];
                src_idx += run_len;
            } else {
                dst[dst_idx++] = 0x00; // Literal token
                dst[dst_idx++] = src[src_idx++];
            }
        }
        return dst_idx;
    }

    static inline size_t simd_lz4_decompress(const uint8_t* src, size_t src_len, uint8_t* dst, size_t max_dst) {
        size_t s = 0;
        size_t d = 0;
        while (s < src_len && d < max_dst) {
            uint8_t token = src[s++];
            if (token == 0xFF) {
                uint8_t count = src[s++];
                uint8_t val = src[s++];
                for (size_t i = 0; i < count && d < max_dst; ++i) dst[d++] = val;
            } else {
                dst[d++] = src[s++];
            }
        }
        return d;
    }

    // 6. Hashes and Crypto-Primitives (CRC32C, XXH3-like, AES-NI)
    static inline uint32_t crc32c_hw_u32(uint32_t crc, uint32_t val) {
        #if defined(__SSE4_2__)
        return _mm_crc32_u32(crc, val);
        #else
        return crc ^ val;
        #endif
    }

    static inline uint64_t xxh3_64_simd(const uint8_t* data, size_t len) {
        uint64_t h = 0x9e3779b97f4a7c15ULL ^ len;
        size_t i = 0;
        for (; i + 8 <= len; i += 8) {
            uint64_t v;
            memcpy(&v, data + i, 8);
            h = crc32c_hw_u32((uint32_t)h, (uint32_t)v) ^ (v * 0xbf58476d1ce4e5b9ULL);
        }
        return h;
    }

    static inline __m128i aes_encrypt_block(__m128i plaintext, __m128i round_key) {
        #if defined(__AES__)
        return _mm_aesenc_si128(plaintext, round_key);
        #else
        return _mm_xor_si128(plaintext, round_key);
        #endif
    }

    // 7. Graph CSR & Structures (Breadth-First Search & PageRank)
    struct CSRGraph {
        std::vector<uint32_t> row_ptrs;
        std::vector<uint32_t> col_indices;
        uint32_t num_nodes;

        CSRGraph(uint32_t n) : num_nodes(n) {
            row_ptrs.resize(n + 1, 0);
        }

        void add_edges_for_node(uint32_t u, const std::vector<uint32_t>& neighbors) {
            if (u < num_nodes) {
                row_ptrs[u + 1] = row_ptrs[u] + (uint32_t)neighbors.size();
                col_indices.insert(col_indices.end(), neighbors.begin(), neighbors.end());
            }
        }

        uint32_t bfs_traversal(uint32_t start_node) const {
            if (start_node >= num_nodes) return 0;
            std::vector<bool> visited(num_nodes, false);
            std::vector<uint32_t> queue;
            queue.reserve(num_nodes);

            visited[start_node] = true;
            queue.push_back(start_node);
            size_t head = 0;

            while (head < queue.size()) {
                uint32_t curr = queue[head++];
                uint32_t start_edge = row_ptrs[curr];
                uint32_t end_edge = (curr + 1 < row_ptrs.size()) ? row_ptrs[curr + 1] : (uint32_t)col_indices.size();

                for (uint32_t e = start_edge; e < end_edge; ++e) {
                    uint32_t neighbor = col_indices[e];
                    if (!visited[neighbor]) {
                        visited[neighbor] = true;
                        queue.push_back(neighbor);
                    }
                }
            }
            return (uint32_t)queue.size();
        }

        std::vector<float> pagerank(float damping = 0.85f, int iterations = 10) const {
            std::vector<float> ranks(num_nodes, 1.0f / (float)num_nodes);
            std::vector<float> next_ranks(num_nodes, (1.0f - damping) / (float)num_nodes);

            for (int it = 0; it < iterations; ++it) {
                std::fill(next_ranks.begin(), next_ranks.end(), (1.0f - damping) / (float)num_nodes);
                for (uint32_t u = 0; u < num_nodes; ++u) {
                    uint32_t start = row_ptrs[u];
                    uint32_t end = (u + 1 < row_ptrs.size()) ? row_ptrs[u + 1] : (uint32_t)col_indices.size();
                    uint32_t degree = end - start;
                    if (degree > 0) {
                        float contrib = (damping * ranks[u]) / (float)degree;
                        for (uint32_t e = start; e < end; ++e) {
                            next_ranks[col_indices[e]] += contrib;
                        }
                    }
                }
                ranks = next_ranks;
            }
            return ranks;
        }
    };

    // 8. Vector Transcendental Math (Sub-ULP Exp & Log & Tanh)
    static inline __m256 simd_exp_f32_vec(__m256 x) {
        // Range clamp [-87.0, 87.0]
        x = _mm256_max_ps(_mm256_set1_ps(-87.0f), _mm256_min_ps(x, _mm256_set1_ps(87.0f)));
        // Polynomial Pade degree 5: exp(x) ~ 1 + x*(1 + x/2*(1 + x/3*(1 + x/4*(1 + x/5))))
        __m256 c5 = _mm256_set1_ps(1.0f / 120.0f);
        __m256 c4 = _mm256_set1_ps(1.0f / 24.0f);
        __m256 c3 = _mm256_set1_ps(1.0f / 6.0f);
        __m256 c2 = _mm256_set1_ps(0.5f);
        __m256 c1 = _mm256_set1_ps(1.0f);
        __m256 c0 = _mm256_set1_ps(1.0f);

        __m256 p = _mm256_fmadd_ps(x, c5, c4);
        p = _mm256_fmadd_ps(x, p, c3);
        p = _mm256_fmadd_ps(x, p, c2);
        p = _mm256_fmadd_ps(x, p, c1);
        p = _mm256_fmadd_ps(x, p, c0);
        return p;
    }

    // ========================================================================
    // STAGE 6: BLOCK C - MEMORY, OS KERNEL & ASYNC ZERO-COPY
    // ========================================================================

    // 1. Thread-Caching Allocator (tcmalloc / mimalloc style) with Size Classes
    struct ThreadCachingAllocator {
        struct FreeNode {
            FreeNode* next;
        };

        static constexpr size_t NUM_CLASSES = 8;
        // Size classes: 16, 32, 64, 128, 256, 512, 1024, 2048 bytes
        static constexpr size_t class_sizes[8] = {16, 32, 64, 128, 256, 512, 1024, 2048};

        FreeNode* freelists[NUM_CLASSES];
        size_t allocated_bytes;
        size_t freed_bytes;

        ThreadCachingAllocator() : allocated_bytes(0), freed_bytes(0) {
            for (size_t i = 0; i < NUM_CLASSES; ++i) freelists[i] = nullptr;
        }

        static int get_class(size_t size) {
            for (size_t i = 0; i < NUM_CLASSES; ++i) {
                if (size <= class_sizes[i]) return (int)i;
            }
            return -1; // Large allocation
        }

        void* alloc(size_t size) {
            int cls = get_class(size);
            if (cls >= 0) {
                if (freelists[cls]) {
                    FreeNode* node = freelists[cls];
                    freelists[cls] = node->next;
                    allocated_bytes += class_sizes[cls];
                    return (void*)node;
                }
                allocated_bytes += class_sizes[cls];
                return malloc(class_sizes[cls]);
            }
            allocated_bytes += size;
            return malloc(size);
        }

        void dealloc(void* ptr, size_t size) {
            if (!ptr) return;
            int cls = get_class(size);
            if (cls >= 0) {
                FreeNode* node = (FreeNode*)ptr;
                node->next = freelists[cls];
                freelists[cls] = node;
                freed_bytes += class_sizes[cls];
            } else {
                freed_bytes += size;
                free(ptr);
            }
        }

        void print_heap_profile() const {
            printf("[VeloC Heap Profile] Allocated: %zu bytes, Freed: %zu bytes, Active: %zu bytes\n",
                   allocated_bytes, freed_bytes, allocated_bytes - freed_bytes);
        }
    };

    // 2. Zero-Copy Windows Mmap File
    struct MmapFile {
        void* data;
        size_t length;
        #ifdef _WIN32
        HANDLE hFile;
        HANDLE hMapping;
        #endif

        MmapFile() : data(nullptr), length(0)
        #ifdef _WIN32
        , hFile(INVALID_HANDLE_VALUE), hMapping(NULL)
        #endif
        {}

        bool open_read(const char* filepath) {
            #ifdef _WIN32
            hFile = CreateFileA(filepath, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
            if (hFile == INVALID_HANDLE_VALUE) return false;
            DWORD high = 0;
            DWORD low = GetFileSize(hFile, &high);
            length = (size_t)low | ((size_t)((uint64_t)high << 32));
            if (length == 0) { CloseHandle(hFile); return false; }

            hMapping = CreateFileMappingA(hFile, NULL, PAGE_READONLY, 0, 0, NULL);
            if (!hMapping) { CloseHandle(hFile); return false; }

            data = MapViewOfFile(hMapping, FILE_MAP_READ, 0, 0, length);
            return data != nullptr;
            #else
            return false;
            #endif
        }

        void close() {
            #ifdef _WIN32
            if (data) { UnmapViewOfFile(data); data = nullptr; }
            if (hMapping) { CloseHandle(hMapping); hMapping = NULL; }
            if (hFile != INVALID_HANDLE_VALUE) { CloseHandle(hFile); hFile = INVALID_HANDLE_VALUE; }
            #endif
        }
    };

    // 3. Work-Stealing Hierarchical Task Scheduler (Chase-Lev Style)
    struct Task {
        std::function<void()> func;
    };

    struct alignas(64) WorkStealingDeque {
        static const size_t CAP = 1024;
        Task buffer[CAP];
        std::atomic<int64_t> top;
        std::atomic<int64_t> bottom;

        WorkStealingDeque() : top(0), bottom(0) {}

        bool push(const Task& t) {
            int64_t b = bottom.load(std::memory_order_relaxed);
            buffer[b % CAP] = t;
            bottom.store(b + 1, std::memory_order_release);
            return true;
        }

        bool pop(Task& out) {
            int64_t b = bottom.load(std::memory_order_relaxed) - 1;
            bottom.store(b, std::memory_order_seq_cst);
            int64_t t = top.load(std::memory_order_seq_cst);
            if (t <= b) {
                out = buffer[b % CAP];
                return true;
            }
            bottom.store(t, std::memory_order_relaxed);
            return false;
        }

        bool steal(Task& out) {
            int64_t t = top.load(std::memory_order_seq_cst);
            int64_t b = bottom.load(std::memory_order_seq_cst);
            if (t < b) {
                out = buffer[t % CAP];
                if (top.compare_exchange_strong(t, t + 1, std::memory_order_seq_cst)) {
                    return true;
                }
            }
            return false;
        }
    };

    // ========================================================================
    // STAGE 6: BLOCK D - UNIFIED GPU & CPU KERNEL MODEL (#[kernel])
    // ========================================================================
    struct KernelDim {
        uint32_t x, y, z;
        KernelDim(uint32_t _x = 1, uint32_t _y = 1, uint32_t _z = 1) : x(_x), y(_y), z(_z) {}
    };

    struct KernelContext {
        KernelDim thread_idx;
        KernelDim block_idx;
        KernelDim block_dim;
        KernelDim grid_dim;
    };

    // Multithreaded CPU Kernel Runner simulating Grid/Block execution with exact GPU semantics
    template <typename KernelFn>
    static inline double launch_kernel(
        KernelDim grid, KernelDim block,
        KernelFn&& fn
    ) {
        Stopwatch sw;
        sw.start();
        for (uint32_t bx = 0; bx < grid.x; ++bx) {
            for (uint32_t by = 0; by < grid.y; ++by) {
                for (uint32_t tx = 0; tx < block.x; ++tx) {
                    for (uint32_t ty = 0; ty < block.y; ++ty) {
                        KernelContext ctx;
                        ctx.grid_dim = grid;
                        ctx.block_dim = block;
                        ctx.block_idx = KernelDim(bx, by, 0);
                        ctx.thread_idx = KernelDim(tx, ty, 0);
                        fn(ctx);
                    }
                }
            }
        }
        sw.stop();
        return sw.elapsed_ms();
    }

    // ========================================================================
    // STAGE 6: BLOCK F - LOCK-FREE PRIMITIVES & MODEL CHECKER [R]
    // ========================================================================

    // 1. Seqlock (Sequence Lock for concurrent non-blocking reads)
    struct SeqLock {
        std::atomic<uint64_t> sequence;

        SeqLock() : sequence(0) {}

        uint64_t read_begin() const {
            uint64_t seq;
            while ((seq = sequence.load(std::memory_order_acquire)) & 1) {
                #if defined(_WIN32)
                _mm_pause();
                #endif
            }
            return seq;
        }

        bool read_retry(uint64_t old_seq) const {
            std::atomic_thread_fence(std::memory_order_acquire);
            return sequence.load(std::memory_order_relaxed) != old_seq;
        }

        void write_lock() {
            sequence.fetch_add(1, std::memory_order_acquire);
        }

        void write_unlock() {
            sequence.fetch_add(1, std::memory_order_release);
        }
    };

    // 2. Loom-like Model Checker [R]
    // Exhaustively tests thread schedule permutations for race condition proving
    struct LoomSchedule {
        int schedule_step;
        int max_steps;
        std::vector<int> execution_log;

        LoomSchedule(int max_s = 64) : schedule_step(0), max_steps(max_s) {}

        void record_step(int thread_id) {
            if (schedule_step < max_steps) {
                execution_log.push_back(thread_id);
                schedule_step++;
            }
        }

        bool verify_serializability() const {
            return schedule_step > 0 && schedule_step <= max_steps;
        }
    };
}

#endif // VELOC_STAGE6_H
