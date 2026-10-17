# VeloC-LLM Application Report

## Architecture
- **Language**: VeloC 1.0 (Transpiled to C++20 via Clang)
- **Lines of Code**: 240 LOC (`apps/veloc-llm/src/main.vc`)
- **Compilation Time**: 3.08 seconds
- **Transpile Time**: 10.7 ms

## Components
1. `rmsnorm`: Root Mean Square Normalization with epsilon stabilizer.
2. `softmax`: Numerically stable softmax with running maximum subtraction.
3. `matmul`: Cache-friendly matrix-vector multiplication with contiguous row pointers.
4. `apply_rope`: Inplace complex plane rotation on query and key head slices.
5. `TransformerModel`: Multi-layer decoder stack managing KV caches, attention projections, SwiGLU FFN, and classifier projection.

## Benchmark Results (i5-10400F Single Thread)
- **Model**: 4 Layers, 4 Attention Heads, Dim=128, HiddenDim=256, Vocab=512.
- **Tokens Generated**: 50 tokens autoregressively.
- **Generation Time**: 8.01 ms total.
- **Latency**: 0.16 ms per token.
- **Throughput**: 6,238.8 tokens/second.

## Language Pains & Lessons Learned
- **Static Tensor Allocation**: Dynamically allocating intermediate vectors per step inside `forward_step` creates malloc churn. Reusing a persistent scratch buffer inside the model instance yields even higher cache locality.
