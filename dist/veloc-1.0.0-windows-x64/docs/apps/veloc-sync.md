# VeloC-Sync Application Report

## Architecture
- **Language**: VeloC 1.0 (Transpiled to C++20 via Clang)
- **Lines of Code**: 145 LOC (`apps/veloc-sync/src/main.vc`)
- **Compilation Time**: 3.05 seconds
- **Transpile Time**: 6.7 ms

## Components
1. `GEAR_TABLE`: 256-entry random matrix mapping byte values to pseudo-random 32-bit states.
2. `FastCdcChunker`: Sliding window rolling hash boundary detector operating within `[min_size, max_size]` boundaries with mask matching.
3. `compute_chunk_hash`: 64-bit FNV-1a fingerprint indexing chunk contents.
4. `Deduplication Index`: Inverted index mapping chunk hashes to physical offsets, eliminating redundant data storage.

## Benchmark Results (i5-10400F Single Thread)
- **Data Volume**: 10.0 MB synthetic data stream.
- **Chunks Produced**: 640 chunks (Average size: 16.0 KB).
- **Unique Chunks**: 4 unique chunks (64 KB stored).
- **Chunking Throughput**: 424.2 MB/sec (23.57 ms total time).
- **Deduplication Ratio**: 160.00x (99.4% storage savings).

## Language Pains & Lessons Learned
- **Compound Assignment Tokenization**: Compound operator `^=` was parsed as separate `^` and `=`, producing a syntax error in C++ output. Refactored to explicit `h = h ^ val;`. Noted for lexer compound assignment enhancement.
