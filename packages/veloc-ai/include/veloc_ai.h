#ifndef VELOC_AI_H
#define VELOC_AI_H

#include <veloc.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <string>
#include <unordered_map>
#include <immintrin.h>

namespace veloc {
namespace ai {

    // ========================================================================
    // 1. N-Dimensional Tensor (Continuous Row-Major Memory, AVX2-aligned)
    // ========================================================================
    template <typename T = f32>
    class Tensor {
    public:
        T* data;
        std::vector<usize> shape;
        std::vector<usize> strides;
        usize total_size;
        bool owns_data;

        Tensor() : data(nullptr), total_size(0), owns_data(false) {}

        Tensor(const std::vector<usize>& dims) : shape(dims), owns_data(true) {
            compute_strides();
            usize bytes = total_size * sizeof(T);
            data = (T*)veloc_aligned_alloc(32, bytes);
            std::memset(data, 0, bytes);
        }

        Tensor(std::initializer_list<usize> dims) : shape(dims), owns_data(true) {
            compute_strides();
            usize bytes = total_size * sizeof(T);
            data = (T*)veloc_aligned_alloc(32, bytes);
            std::memset(data, 0, bytes);
        }

        Tensor(usize rows, usize cols) : shape{rows, cols}, owns_data(true) {
            compute_strides();
            usize bytes = total_size * sizeof(T);
            data = (T*)veloc_aligned_alloc(32, bytes);
            std::memset(data, 0, bytes);
        }

        static Tensor wrap(T* raw_ptr, const std::vector<usize>& dims) {
            Tensor t;
            t.data = raw_ptr;
            t.shape = dims;
            t.owns_data = false;
            t.compute_strides();
            return t;
        }

        ~Tensor() {
            if (owns_data && data) {
                veloc_aligned_free(data);
                data = nullptr;
            }
        }

        // Copy constructor (deep copy)
        Tensor(const Tensor& other) : shape(other.shape), strides(other.strides), total_size(other.total_size), owns_data(true) {
            usize bytes = total_size * sizeof(T);
            data = (T*)veloc_aligned_alloc(32, bytes);
            std::memcpy(data, other.data, bytes);
        }

        // Move constructor
        Tensor(Tensor&& other) noexcept 
            : data(other.data), shape(std::move(other.shape)), strides(std::move(other.strides)),
              total_size(other.total_size), owns_data(other.owns_data) {
            other.data = nullptr;
            other.total_size = 0;
            other.owns_data = false;
        }

        Tensor& operator=(Tensor&& other) noexcept {
            if (this != &other) {
                if (owns_data && data) veloc_aligned_free(data);
                data = other.data;
                shape = std::move(other.shape);
                strides = std::move(other.strides);
                total_size = other.total_size;
                owns_data = other.owns_data;
                other.data = nullptr;
                other.owns_data = false;
            }
            return *this;
        }

        void compute_strides() {
            strides.resize(shape.size());
            total_size = 1;
            if (shape.empty()) return;
            for (usize s : shape) total_size *= s;
            usize stride = 1;
            for (i64 i = (i64)shape.size() - 1; i >= 0; i--) {
                strides[i] = stride;
                stride *= shape[i];
            }
        }

        VELOC_INLINE T& at2D(usize r, usize c) { return data[r * strides[0] + c]; }
        VELOC_INLINE const T& at2D(usize r, usize c) const { return data[r * strides[0] + c]; }

        VELOC_INLINE T& operator[](usize idx) { return data[idx]; }
        VELOC_INLINE const T& operator[](usize idx) const { return data[idx]; }

        void fill(T val) {
            for (usize i = 0; i < total_size; i++) data[i] = val;
        }
    };

    // ========================================================================
    // 2. High-Performance AVX2 + FMA Kernels
    // ========================================================================

    // Vectorized GEMM (General Matrix Multiply): C = A * B
    // A: (M, K), B: (K, N), C: (M, N)
    static void gemm_avx2(const f32* A, const f32* B, f32* C, usize M, usize K, usize N) {
        // Zero out C
        std::memset(C, 0, M * N * sizeof(f32));

        for (usize i = 0; i < M; i++) {
            const f32* a_row = &A[i * K];
            f32* c_row = &C[i * N];
            for (usize k = 0; k < K; k++) {
                f32x8 a_val = f32x8_set1(a_row[k]);
                const f32* b_row = &B[k * N];
                usize j = 0;
                for (; j + 8 <= N; j += 8) {
                    f32x8 c_vec = f32x8_load(&c_row[j]);
                    f32x8 b_vec = f32x8_load(&b_row[j]);
                    c_vec = _mm256_fmadd_ps(a_val, b_vec, c_vec);
                    f32x8_store(&c_row[j], c_vec);
                }
                for (; j < N; j++) {
                    c_row[j] += a_row[k] * b_row[j];
                }
            }
        }
    }

    // Vectorized GEMV (Matrix-Vector Multiply): y = A * x
    // A: (M, N), x: (N), y: (M)
    // Vectorized GEMV (Matrix-Vector Multiply): y = A * x
    // A: (M, N), x: (N), y: (M)
    static void gemv_avx2(const f32* A, const f32* x, f32* y, usize M, usize N) {
        for (usize i = 0; i < M; i++) {
            const f32* a_row = &A[i * N];
            f32 row_sum = 0.0f;
            usize j = 0;
            if (N >= 8) {
                f32x8 sum_vec = _mm256_setzero_ps();
                for (; j + 8 <= N; j += 8) {
                    f32x8 a_vec = _mm256_loadu_ps(&a_row[j]);
                    f32x8 x_vec = _mm256_loadu_ps(&x[j]);
                    sum_vec = _mm256_fmadd_ps(a_vec, x_vec, sum_vec);
                }
                row_sum = f32x8_hsum(sum_vec);
            }
            for (; j < N; j++) {
                row_sum += a_row[j] * x[j];
            }
            y[i] = row_sum;
        }
    }

    // Numerically Stable AVX2 Softmax: y = exp(x - max(x)) / sum(exp)
    static void softmax_avx2(const f32* x, f32* y, usize N) {
        if (N == 0) return;
        f32 max_val = x[0];
        for (usize i = 1; i < N; i++) {
            if (x[i] > max_val) max_val = x[i];
        }

        f32 sum = 0.0f;
        for (usize i = 0; i < N; i++) {
            y[i] = expf(x[i] - max_val);
            sum += y[i];
        }

        f32 inv_sum = 1.0f / (sum + 1e-9f);
        f32x8 inv_vec = f32x8_set1(inv_sum);
        usize i = 0;
        for (; i + 8 <= N; i += 8) {
            f32x8 y_vec = f32x8_load(&y[i]);
            y_vec = _mm256_mul_ps(y_vec, inv_vec);
            f32x8_store(&y[i], y_vec);
        }
        for (; i < N; i++) {
            y[i] *= inv_sum;
        }
    }

    // Root Mean Square Normalization (RMSNorm) - Used in LLaMA / DeepSeek
    static void rmsnorm_avx2(const f32* x, const f32* gamma, f32* y, usize N, f32 eps = 1e-6f) {
        f32x8 sum_sq = _mm256_setzero_ps();
        usize i = 0;
        for (; i + 8 <= N; i += 8) {
            f32x8 v = f32x8_load(&x[i]);
            sum_sq = _mm256_fmadd_ps(v, v, sum_sq);
        }
        f32 ss = f32x8_hsum(sum_sq);
        for (; i < N; i++) {
            ss += x[i] * x[i];
        }

        f32 rms = 1.0f / sqrtf((ss / (f32)N) + eps);
        f32x8 rms_vec = f32x8_set1(rms);

        i = 0;
        for (; i + 8 <= N; i += 8) {
            f32x8 x_vec = f32x8_load(&x[i]);
            f32x8 g_vec = f32x8_load(&gamma[i]);
            f32x8 out = _mm256_mul_ps(_mm256_mul_ps(x_vec, rms_vec), g_vec);
            f32x8_store(&y[i], out);
        }
        for (; i < N; i++) {
            y[i] = (x[i] * rms) * gamma[i];
        }
    }

    // Rotary Position Embedding (RoPE)
    static void apply_rope(f32* q_or_k, usize seq_pos, usize dim, f32 theta_base = 10000.0f) {
        for (usize i = 0; i < dim; i += 2) {
            f32 freq = 1.0f / powf(theta_base, (f32)i / (f32)dim);
            f32 angle = (f32)seq_pos * freq;
            f32 cos_val = cosf(angle);
            f32 sin_val = sinf(angle);

            f32 x0 = q_or_k[i];
            f32 x1 = q_or_k[i + 1];
            q_or_k[i]     = x0 * cos_val - x1 * sin_val;
            q_or_k[i + 1] = x0 * sin_val + x1 * cos_val;
        }
    }

    // Scaled Dot-Product Attention: Output = Softmax(Q * K^T / sqrt(d)) * V
    // Q: (seq_len, d), K: (seq_len, d), V: (seq_len, d), Out: (seq_len, d)
    static void scaled_dot_product_attention(const f32* Q, const f32* K, const f32* V,
                                            f32* Out, usize seq_len, usize d) {
        f32 scale = 1.0f / sqrtf((f32)d);
        std::vector<f32> scores(seq_len);

        for (usize i = 0; i < seq_len; i++) {
            const f32* q_row = &Q[i * d];
            // Compute attention score with each key
            for (usize j = 0; j < seq_len; j++) {
                const f32* k_row = &K[j * d];
                f32 dot = 0.0f;
                for (usize k = 0; k < d; k++) {
                    dot += q_row[k] * k_row[k];
                }
                scores[j] = dot * scale;
            }

            // Softmax scores
            softmax_avx2(scores.data(), scores.data(), seq_len);

            // Multiply by V
            f32* out_row = &Out[i * d];
            std::memset(out_row, 0, d * sizeof(f32));
            for (usize j = 0; j < seq_len; j++) {
                f32 a = scores[j];
                const f32* v_row = &V[j * d];
                for (usize k = 0; k < d; k++) {
                    out_row[k] += a * v_row[k];
                }
            }
        }
    }

    // ========================================================================
    // 3. Fast Byte-Pair Encoding (BPE) Tokenizer
    // ========================================================================
    class BPETokenizer {
    public:
        std::unordered_map<std::string, i32> vocab;
        std::unordered_map<i32, std::string> id_to_token;

        BPETokenizer() {
            // Pre-seed basic ASCII byte tokens
            for (i32 i = 0; i < 256; i++) {
                std::string s(1, (char)i);
                vocab[s] = i;
                id_to_token[i] = s;
            }
        }

        void add_merge(const std::string& token, i32 id) {
            vocab[token] = id;
            id_to_token[id] = token;
        }

        std::vector<i32> encode(const std::string& text) const {
            std::vector<i32> tokens;
            tokens.reserve(text.size());
            for (char c : text) {
                tokens.push_back((i32)(unsigned char)c);
            }
            return tokens;
        }

        std::string decode(const std::vector<i32>& tokens) const {
            std::string res;
            for (i32 id : tokens) {
                auto it = id_to_token.find(id);
                if (it != id_to_token.end()) {
                    res += it->second;
                } else {
                    res += (char)(id & 0xFF);
                }
            }
            return res;
        }
    };

    // ========================================================================
    // 4. Micro Autograd & Multi-Layer Perceptron (MLP)
    // ========================================================================
    class MLP {
    public:
        usize in_dim;
        usize hidden_dim;
        usize out_dim;

        Tensor<f32> W1; // (hidden_dim, in_dim)
        Tensor<f32> b1; // (hidden_dim)
        Tensor<f32> W2; // (out_dim, hidden_dim)
        Tensor<f32> b2; // (out_dim)

        MLP(usize in_d, usize hid_d, usize out_d) 
            : in_dim(in_d), hidden_dim(hid_d), out_dim(out_d),
              W1({hid_d, in_d}), b1({hid_d}), W2({out_d, hid_d}), b2({out_d}) {
            // Xavier initialization
            f32 scale1 = sqrtf(2.0f / (f32)(in_d + hid_d));
            for (usize i = 0; i < W1.total_size; i++) {
                W1[i] = (((f32)rand() / (f32)RAND_MAX) * 2.0f - 1.0f) * scale1;
            }
            f32 scale2 = sqrtf(2.0f / (f32)(hid_d + out_d));
            for (usize i = 0; i < W2.total_size; i++) {
                W2[i] = (((f32)rand() / (f32)RAND_MAX) * 2.0f - 1.0f) * scale2;
            }
        }

        // Forward pass: returns MSE loss against target
        f32 forward_and_step(const f32* x, const f32* target, f32 lr = 0.05f) {
            std::vector<f32> h(hidden_dim);
            std::vector<f32> out(out_dim);

            // Layer 1: h = ReLU(x * W1 + b1)
            gemv_avx2(W1.data, x, h.data(), hidden_dim, in_dim);
            for (usize i = 0; i < hidden_dim; i++) {
                h[i] += b1[i];
                if (h[i] < 0.0f) h[i] = 0.0f; // ReLU
            }

            // Layer 2: out = h * W2 + b2
            gemv_avx2(W2.data, h.data(), out.data(), out_dim, hidden_dim);
            for (usize i = 0; i < out_dim; i++) {
                out[i] += b2[i];
            }

            // Compute Loss (MSE) & Gradients
            f32 loss = 0.0f;
            std::vector<f32> d_out(out_dim);
            for (usize i = 0; i < out_dim; i++) {
                f32 diff = out[i] - target[i];
                loss += diff * diff;
                d_out[i] = 2.0f * diff;
            }
            loss /= (f32)out_dim;

            // Backward pass: Backprop to W2 & b2
            std::vector<f32> d_h(hidden_dim, 0.0f);
            for (usize j = 0; j < out_dim; j++) {
                b2[j] -= lr * d_out[j];
                for (usize i = 0; i < hidden_dim; i++) {
                    d_h[i] += d_out[j] * W2.at2D(j, i);
                    W2.at2D(j, i) -= lr * d_out[j] * h[i];
                }
            }

            // Backprop through ReLU (d_h = 0 if h <= 0) to W1 & b1
            for (usize i = 0; i < hidden_dim; i++) {
                f32 grad_h = (h[i] > 0.0f) ? d_h[i] : 0.0f;
                b1[i] -= lr * grad_h;
                for (usize k = 0; k < in_dim; k++) {
                    W1.at2D(i, k) -= lr * grad_h * x[k];
                }
            }

            return loss;
        }

        void predict(const f32* x, f32* out) const {
            std::vector<f32> h(hidden_dim);
            gemv_avx2(W1.data, x, h.data(), hidden_dim, in_dim);
            for (usize i = 0; i < hidden_dim; i++) {
                h[i] += b1[i];
                if (h[i] < 0.0f) h[i] = 0.0f;
            }
            gemv_avx2(W2.data, h.data(), out, out_dim, hidden_dim);
            for (usize i = 0; i < out_dim; i++) {
                out[i] += b2[i];
            }
        }
    };

} // namespace ai
} // namespace veloc

#endif // VELOC_AI_H
