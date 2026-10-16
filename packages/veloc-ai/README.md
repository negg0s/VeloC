# veloc-ai: High-Performance AI & Vector Math Engine for VeloC

`veloc-ai` provides fundamental deep learning primitives optimized for AVX2 and modern x86_64 architectures.

## Architecture & Features

1. **N-Dimensional Tensor (`Tensor<T>`)**:
   - Continuous row-major memory with 32-byte AVX2 aligned allocations.
   - Strided indexing (`at2D`), deep copy, and zero-allocation views (`wrap`).
2. **AVX2 + FMA Accelerated Compute Kernels**:
   - `gemm_avx2`: General matrix-matrix multiplication reaching **30.72 GFLOPS** on a single thread.
   - `gemv_avx2`: Matrix-vector multiplication vectorized with `f32x8_hsum`.
   - `softmax_avx2`: Numerically stable vectorized softmax ($\max(x)$ shift).
   - `rmsnorm_avx2`: Root Mean Square Normalization (as used in LLaMA 3 and DeepSeek).
   - `scaled_dot_product_attention`: Core Transformer multi-head attention kernel.
   - `apply_rope`: Rotary Position Embedding for large language models.
3. **Byte-Pair Encoding (`BPETokenizer`)**:
   - Fast sub-word tokenization and detokenization.
4. **Autograd & Neural Networks (`MLP`)**:
   - Multi-layer perceptron with automated backpropagation and stochastic gradient descent (SGD).
   - Capable of learning non-linear functions (e.g. XOR) to 0.000000 MSE loss in 329 ms.

## Benchmarks (Intel Core i5-10400F, Clang 20, AVX2)

| Kernel | Size | Latency | Throughput | Baseline Speedup |
|---|---|---|---|---|
| **Naive Scalar GEMM** | 256x256 | 1.19 ms | 28.31 GFLOPS | 1.0x (Reference) |
| **AVX2+FMA VeloC GEMM**| 256x256 | 1.09 ms | **30.72 GFLOPS** | **1.1x** |
| **XOR MLP Convergence**| 20,000 epochs | 329.54 ms | 60,700 epochs/s | 100% Accuracy (0.000000 MSE) |

## Running Tests & Demonstrations

```bash
# Run unit tests (Tensor, Softmax, RMSNorm, Attention, BPE)
python veloc.py run packages/veloc-ai/tests/test_ai.vc

# Run AVX2 GEMM benchmark
python veloc.py run packages/veloc-ai/benchmarks/bench_gemm.vc

# Run MLP training & inference demo
python veloc.py run packages/veloc-ai/examples/demo_ai.vc
```
