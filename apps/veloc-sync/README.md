# VeloC-Sync

High-throughput Content-Defined Chunking (CDC) deduplicating archiver engine written in VeloC.

## Architecture
- **FastCDC Gear Algorithm**: Fast sliding window rolling hash with bitmask matching avoiding variable-length window overhead.
- **FNV-1a 64-bit Chunk Digest**: Collision-resistant indexing identifying duplicated blocks across streams.
- **Deduplication Store**: Deduplication index saving physical storage by writing unique block payloads only once.

## Performance
- **Throughput**: ~424.2 MB/sec single-core streaming chunking.
- **Deduplication**: 160.0x compression ratio on repetitive data stream (99.4% storage savings).
