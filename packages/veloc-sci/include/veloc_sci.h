#ifndef VELOC_SCI_H
#define VELOC_SCI_H

#include <veloc.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <complex>

namespace veloc {
namespace sci {

    // ========================================================================
    // 1. Linear Algebra: Cholesky Decomposition (A = L * L^T)
    // Suitable for symmetric positive-definite systems
    // ========================================================================
    static bool cholesky(const f64* A, f64* L, usize N) {
        std::memset(L, 0, N * N * sizeof(f64));
        for (usize i = 0; i < N; i++) {
            for (usize j = 0; j <= i; j++) {
                f64 sum = 0.0;
                for (usize k = 0; k < j; k++) {
                    sum += L[i * N + k] * L[j * N + k];
                }
                if (i == j) {
                    f64 val = A[i * N + i] - sum;
                    if (val <= 0.0) return false; // Not positive definite
                    L[i * N + j] = sqrt(val);
                } else {
                    L[i * N + j] = (A[i * N + j] - sum) / L[j * N + j];
                }
            }
        }
        return true;
    }

    // ========================================================================
    // 2. Linear Algebra: LU Decomposition with Partial Pivoting (P * A = L * U)
    // ========================================================================
    static bool lu_decompose(const f64* A, f64* LU, usize* P, usize N) {
        std::memcpy(LU, A, N * N * sizeof(f64));
        for (usize i = 0; i < N; i++) P[i] = i;

        for (usize i = 0; i < N; i++) {
            // Find pivot
            f64 max_val = 0.0;
            usize pivot_row = i;
            for (usize k = i; k < N; k++) {
                f64 abs_val = fabs(LU[k * N + i]);
                if (abs_val > max_val) {
                    max_val = abs_val;
                    pivot_row = k;
                }
            }
            if (max_val < 1e-12) return false; // Singular matrix

            // Swap rows
            if (pivot_row != i) {
                usize tmp_p = P[i]; P[i] = P[pivot_row]; P[pivot_row] = tmp_p;
                for (usize k = 0; k < N; k++) {
                    f64 tmp = LU[i * N + k];
                    LU[i * N + k] = LU[pivot_row * N + k];
                    LU[pivot_row * N + k] = tmp;
                }
            }

            // Elimination
            for (usize j = i + 1; j < N; j++) {
                LU[j * N + i] /= LU[i * N + i];
                for (usize k = i + 1; k < N; k++) {
                    LU[j * N + k] -= LU[j * N + i] * LU[i * N + k];
                }
            }
        }
        return true;
    }

    // Solve A * x = b using precomputed LU decomposition
    static void lu_solve(const f64* LU, const usize* P, const f64* b, f64* x, usize N) {
        std::vector<f64> y(N);
        // Forward substitution (L * y = P * b)
        for (usize i = 0; i < N; i++) {
            f64 sum = 0.0;
            for (usize k = 0; k < i; k++) {
                sum += LU[i * N + k] * y[k];
            }
            y[i] = b[P[i]] - sum;
        }

        // Backward substitution (U * x = y)
        for (i64 i = (i64)N - 1; i >= 0; i--) {
            f64 sum = 0.0;
            for (usize k = (usize)i + 1; k < N; k++) {
                sum += LU[(usize)i * N + k] * x[k];
            }
            x[(usize)i] = (y[(usize)i] - sum) / LU[(usize)i * N + (usize)i];
        }
    }

    // ========================================================================
    // 3. Fast Fourier Transform (Cooley-Tukey Radix-2 FFT)
    // ========================================================================
    typedef std::complex<f64> c64;

    static void fft_radix2(std::vector<c64>& a, bool invert = false) {
        usize n = a.size();
        if (n <= 1) return;

        // Bit-reversal permutation
        for (usize i = 1, j = 0; i < n; i++) {
            usize bit = n >> 1;
            for (; j & bit; bit >>= 1) j ^= bit;
            j ^= bit;
            if (i < j) std::swap(a[i], a[j]);
        }

        for (usize len = 2; len <= n; len <<= 1) {
            f64 ang = 2.0 * 3.14159265358979323846 / (f64)len * (invert ? -1 : 1);
            c64 wlen(cos(ang), sin(ang));
            for (usize i = 0; i < n; i += len) {
                c64 w(1);
                for (usize j = 0; j < len / 2; j++) {
                    c64 u = a[i + j];
                    c64 v = a[i + j + len / 2] * w;
                    a[i + j] = u + v;
                    a[i + j + len / 2] = u - v;
                    w *= wlen;
                }
            }
        }

        if (invert) {
            for (c64& x : a) x /= (f64)n;
        }
    }

    // ========================================================================
    // 4. Runge-Kutta 4th Order (RK4) ODE Integrator
    // Solves dy/dt = f(t, y) with 4th order accuracy
    // ========================================================================
    template <typename Func>
    static void rk4_step(Func&& f, f64& t, std::vector<f64>& y, f64 dt) {
        usize n = y.size();
        std::vector<f64> k1(n), k2(n), k3(n), k4(n), y_tmp(n);

        f(t, y, k1);

        for (usize i = 0; i < n; i++) y_tmp[i] = y[i] + 0.5 * dt * k1[i];
        f(t + 0.5 * dt, y_tmp, k2);

        for (usize i = 0; i < n; i++) y_tmp[i] = y[i] + 0.5 * dt * k2[i];
        f(t + 0.5 * dt, y_tmp, k3);

        for (usize i = 0; i < n; i++) y_tmp[i] = y[i] + dt * k3[i];
        f(t + dt, y_tmp, k4);

        for (usize i = 0; i < n; i++) {
            y[i] += (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
        t += dt;
    }

    // ========================================================================
    // 5. Monte Carlo Integrator (N-dimensional)
    // ========================================================================
    template <typename Func>
    static f64 monte_carlo_integrate_1d(Func&& f, f64 a, f64 b, usize num_samples) {
        f64 sum = 0.0;
        f64 range = b - a;
        for (usize i = 0; i < num_samples; i++) {
            f64 x = a + ((f64)rand() / (f64)RAND_MAX) * range;
            sum += f(x);
        }
        return (sum / (f64)num_samples) * range;
    }

} // namespace sci
} // namespace veloc

#endif // VELOC_SCI_H
