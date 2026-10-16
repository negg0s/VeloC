# VeloC-DB Application Report

## Architecture
- **Language**: VeloC 1.0 (Transpiled to C++20 via Clang)
- **Lines of Code**: 220 LOC (`apps/veloc-db/src/main.vc`)
- **Compilation Time**: 3.12 seconds (Clang -O3 -std=c++20)
- **Transpile Time**: 6.0 ms

## Components
1. `WalManager`: Transaction sequence numbering, commit records, log truncation, crash replay.
2. `BTreeIndex`: Sorted memory structure with binary search inside cache lines.
3. `MvccTable`: Row version tuples `(tx_id, key, val, is_deleted)` supporting snapshot reads at given transaction IDs.
4. `SqlPlanner`: Rule- and cost-based query planner selecting between `IndexScan` ($O(\log N)$) and `SeqScan` ($O(N)$).

## Benchmark Results (i5-10400F)
- **10,000 Inserts (WAL + MVCC)**: 1.979 ms (5,052,801 tx/sec)
- **MVCC Isolation**: Verified snapshot at $T=1$ does not observe uncommitted or later commits at $T=2$.
- **Crash Recovery**: Discarded uncommitted in-flight transactions, successfully reconstructed valid table state.
- **Planner Selection**: Correctly selected `IndexScan` over `SeqScan`.

## Language Pains & Lessons Learned
- **Standard Library Include**: `#include <unordered_set>` was initially missing from `veloc.h`, while `<unordered_map>` was present. Added to core header to avoid explicit interop imports.
- **Snapshot Memory Overhead**: Version vectors require custom pooling to avoid heap fragmentation in long-running workloads.
