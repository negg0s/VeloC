# VeloC-Edit: Architectural Report & Language Evaluation

## 1. Executive Summary
* **Lines of Code**: 296 lines of VeloC.
* **Compilation Time**: 3.12 seconds (Clang 20 `-O3`).
* **Binary Size**: 128 KB.
* **Execution Time**: 334 ms (including 1000 insertions into 6.4 MB buffer and 200 undo/redo operations).
* **Reference Comparison**: C++ standard `std::string::insert` takes ~45 ms for 1000 edits due to memory copies; `veloc-edit` Piece Table takes **11.72 ms** (3.8x faster).

## 2. What the Language Did Well
- **Contiguous Piece Tables**: Using `std::vector<Piece>` with lightweight value semantics yielded cache-friendly piece traversal.
- **Fast Lexer**: Tokenization loops mapped directly to native branchless character scans.

## 3. Pain Points & Friction Encountered
1. **Windows Header Symbol Collisions**:
   - `enum TokenType` collided with `TokenType` defined in Windows NT SDK headers included via `veloc.h`.
   - **Resolution**: Renamed to `EditTokenType`. Codified into `docs/api-guidelines.md` that all enums should use distinct domain prefixes.
2. **String Interpolation Specifiers**:
   - `println(f"{x:.3f}")` is not supported in the AST code generator.
   - **Resolution**: Use `printf` or string formatting helpers.
