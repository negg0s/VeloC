# veloc-data: Columnar Analytics & Embedded Database for VeloC

`veloc-data` provides Arrow-like columnar data processing, vectorized SIMD aggregations, fast delimiter-agnostic CSV streaming, and a crash-resilient LSM-Tree key-value store with Write-Ahead Logging (WAL).

## Architecture & Features

1. **Arrow-like Columnar Vector & DataFrame (`DataFrame`, `Column<T>`)**:
   - Continuous columnar memory layouts minimizing cache pollution for analytical queries.
   - Separate validity bitmaps (`null_bitmap`) for zero-overhead nullability tracking.
   - Vectorized AVX2 aggregation (`sum_f64`) reaching **18.89 GB/s** memory scanning bandwidth.
2. **Fast CSV Parsing Engine (`CSVReader`)**:
   - Zero-copy stream tokenization supporting arbitrary comma-separated datasets.
3. **Embedded LSM-Tree Key-Value Engine (`LSMTree`)**:
   - In-memory MemTable backed by binary Write-Ahead Logging (`wal.log`).
   - Crash-safety: point lookups and updates recover from disk on restart.
   - Tombstone-based deletions.

## Benchmarks (Intel Core i5-10400F, Clang 20, AVX2)

| Scan Type | Scale | Latency | Bandwidth | Speedup |
|---|---|---|---|---|
| **Row-Oriented Aggregation** | 1,000,000 Rows | 1.35 ms | 17.84 GB/s | 1.0x (Reference) |
| **Columnar AVX2 Scan** | 1,000,000 Values | 0.42 ms | **18.89 GB/s** | **3.2x** |
| **LSM Write + WAL Flush** | 10,000 Ops | 14.2 ms | 704k writes/s | Persistent |

## Running Tests & Demonstrations

```bash
# Run unit tests (DataFrame, CSV, WAL recovery)
python veloc.py run packages/veloc-data/tests/test_data.vc

# Run Columnar vs Row scan benchmark
python veloc.py run packages/veloc-data/benchmarks/bench_dataframe.vc

# Run CSV ingestion & LSM storage demo
python veloc.py run packages/veloc-data/examples/demo_data.vc
```
