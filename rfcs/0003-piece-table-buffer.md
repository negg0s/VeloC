# RFC-0003: Piece Table Buffer for Ultra-Fast Text Manipulation

- **Feature Name**: `piece_table_buffer`
- **Start Date**: 2026-10-16
- **Status**: Accepted & Implemented

---

## 1. Summary
Adopts the Piece Table data structure as the recommended reference standard for text editing, string manipulation, and buffer pipelines within VeloC standard tooling.

## 2. Motivation
Traditional rope and gap buffers suffer from rebalancing overhead or contiguous block copies during large insertions. The Piece Table separates immutable original and append buffers from a lightweight piece descriptor list, enabling sub-millisecond document loading and microsecond edits on multi-megabyte files.
