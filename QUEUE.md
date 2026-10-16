# ОЧЕРЕДЬ ЗАДАЧ VeloC (QUEUE.md)

- [x] **ЭТАП 1**: Фундамент (P0), честные бенчмарки, тест-раннер, пакетный менеджер (veloc.toml), аллокаторы, SIMD-ядра, AST-пайплайн. (Выполнен 2026-10-16).
- [x] **ЭТАП 2**: Блоки A (Спецификация, Conformance, Fuzzing, Determinism), B (Query-based incremental compiler), E (Стабильность, Editions, Semver, ABI), F (Static Analysis, Bounds, Ownership). (Выполнен 2026-10-16).
- [x] **ЭТАП 3**: Вертикали экосистемы (veloc-game, veloc-ai, veloc-sci, veloc-data, veloc-net, veloc-embedded, veloc-cli) со 100% реальными приложениями и замерами. (Выполнен 2026-10-16).
- [x] **ЭТАП 4**: Самохостинг (Bootstrap), Миграция C++ -> VeloC, Документация/Книга/Playground, Установщики и Реестр, IDE & VS Code расширение, Единый бенчмарк-лидерборд, Финальный аудит, Автопилот непрерывного улучшения. (Выполнен 2026-10-16).
- [x] **ЭТАП 5**: Продвинутая система типов, Макросистема/comptime, Асинхронность/Конкурентность, MLIR-подобная IR оптимизатора, Эргономика (VeloC 10.0). (Выполнен 2026-10-16).
  - [x] Блок A: Продвинутая система типов (Const generics `Mat<T, M, N>`, Variadic `Tuple<Ts...>`, Linear [R], Refinement [R], Contracts, Typestate, Zero-RTTI Any, Dyn dispatch benchmark)
  - [x] Блок B: Макросистема и метапрограммирование (Hygienic macro_rules!, `veloc expand`, Comptime DFA Regex [R], Comptime SQL validator [R])
  - [x] Блок C: Асинхронность, конкурентность, модели вычислений (Zero-cost stackless Generator, SelectableChannel, STM TVar [R], Deterministic parallel reduction, Reactive dataflow with backpressure)
  - [x] Блок D: Собственный оптимизирующий слой (HighIR, MidIR SSA CFG, LowIR, Inlining/Folding/Escape/BCE/Fusion/DCE/Auto-vectorizer passes, `veloc ir`, `veloc build --opt-report`, Compilation profiles)
  - [x] Блок E: Эргономика и качество жизни (Error handling v2, Extended iterators v2, Multiline strip_margin, ByteSpan, SlicePattern, Doc invariants `doc_mismatch` linter)
