# Best Practices: How to Read Compiler Diagnostic Messages

VeloC provides Elm- and Rust-grade compiler diagnostics. Every message is designed to tell you **where** the error occurred, **what** rule was breached, and **how** to fix it.

---

## Anatomy of a Diagnostic

```text
error[E0003]: Undeclared Identifier: Symbol could not be resolved in the current scope.
  --> src/physics.vc:42:15
     |
 42  |     let acc = gravity_force / mass;
     |               ^^^^^^^^^^^^^
     = help: Did you mean `gravitational_force`?
     = beginner tip: Make sure the variable is declared with `let` before use.
     |
```

1. **Header**: `error[Code]`: The unique error code (e.g. `E0001` to `E0015`). Use `veloc explain E0003` to get full documentation.
2. **Location Pointer**: `--> file:line:col`: Clickable in VS Code and modern terminal emulators.
3. **Source Gutter & Caret**: Pinpoints the exact span of offending tokens.
4. **Help / Levenshtein Suggestion**: Automatic typo correction checking against symbols in scope.
5. **Beginner Tip**: Active when `--profile=beginner` is passed or in the learning mode.

---

## Error Code Quick Reference

- `E0001`: Syntax error (missing semicolon, brace mismatch).
- `E0002`: Type mismatch (cannot assign float to int without `as`).
- `E0003`: Symbol not declared.
- `E0005`: Variable redeclaration in same block.
- `E0006`: Panic on unwrap of `None` or `Err`.
- `E0009`: Incomplete `match` expression (missing arms or wildcard `_`).
- `E0011`: Lifetime/dangling reference violation.
- `E0013`: Static bounds violation.
- `E0015`: High-cost allocation warning in hot loop.
