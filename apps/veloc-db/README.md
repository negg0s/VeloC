# VeloC-DB

Embedded relational/document storage engine written in VeloC.

## Features
- **Write-Ahead Log (WAL)**: Append-only durability with transaction commit records and crash recovery replay.
- **Multi-Version Concurrency Control (MVCC)**: Snapshot isolation ensuring readers do not block writers and writers do not block readers.
- **B+Tree Indexing**: Cache-line conscious sorted indexing for range scans and $O(\log N)$ point lookups.
- **SQL Cost-Based Query Planner**: Automatic selection between full table scans and index scans based on predicates and estimated cost.

## Performance
- **10,000 Transactions**: ~1.98 ms (~5.05M tx/sec in-memory WAL buffer).
- **Crash Recovery**: Instantaneous forward replay of committed transactions discarding aborted/uncommitted writes.
