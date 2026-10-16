# VeloC-LLM

High-performance Transformer Large Language Model (LLM) autoregressive inference engine written in VeloC.

## Architecture
- **Attention**: Multi-Head Self-Attention with causal masking and KV Cache.
- **Positional Encoding**: Rotary Position Embeddings (RoPE) with frequency bands.
- **Normalization**: Root Mean Square Normalization (RMSNorm) with learnable scale.
- **Feed-Forward**: SwiGLU activation (`w2(SiLU(w1(x)) * w3(x))`).
- **Autoregressive Generation**: KV cache updates across successive decode steps.

## Performance
- **Throughput**: ~6,238 tokens/sec (Intel Core i5-10400F CPU).
- **Latency**: 0.16 ms per generated token.
