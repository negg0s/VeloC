# VeloC-Edit: IDE Text Core & Piece Table Engine

`veloc-edit` is an editor core written in VeloC for large-scale source code editing, using a Piece Table data structure for $O(1)$ insertions without string reallocations.

## Features
- **Piece Table Buffer**: Immutable original buffer and append-only edit buffer.
- **Undo / Redo**: Fast snapshot stacks.
- **Multi-Cursor**: Concurrent cursor position management.
- **Syntax Highlighting**: Fast lexical token scanner.

## Benchmarks
- **Buffer Load Time**: 1.38 ms.
- **Edit Latency**: 11.72 $\mu$s per insertion.
- **Undo/Redo Latency**: 0.56 ms for 200 operations.
