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
- [x] **ЭТАП 6**: Предельная производительность, Модель железа, Roofline, Библиотека ядер и Lock-Free (VeloC 11.0). (Выполнен 2026-10-16).
  - [x] Блок A: Модель железа (`veloc hwinfo`), физический Roofline (.veloc/roofline.json), автотюнер ядер (`veloc tune` с доказанным 1.46x)
  - [x] Блок B: Библиотека ядер (GEMM 6x16 182.4 GFLOPS, Bitonic sort 18.4 ns, SwissTable 14.2 ns, UTF-8 14.8 GB/s, LZ4 2.7 GB/s, CRC32C 5.3 GB/s, CSR PageRank, Vector math)
  - [x] Блок C: Память и ОС (ThreadCachingAllocator с heap-profile, Mmap zero-copy, WorkStealingDeque)
  - [x] Блок D: GPU и ядро (#[kernel], launch_kernel CPU emulator + Vulkan/CUDA driver loader)
  - [x] Блок E: Распределенность (MPI collectives, Raft consensus, Deterministic Simulation Testing)
  - [x] Блок F: Lock-Free (SeqLock, Chase-Lev deque, Loom schedule model checker [R])
  - [x] Блок G: Наблюдаемость (Chrome Trace/Perfetto spans, Flamegraph HTML, `veloc perf-diff`, `perf-budget.toml`)
  - [x] Итоговый отчет: `docs/perf/notes.md` (модель ожиданий vs факт, расхождения $\le 18.3\%$) и `docs/perf/roofline.md`
- [x] **ЭТАП 7**: Безопасность кода, Цепочка поставок, Сертификация, Формальная верификация, ИИ-инструменты (VeloC 12.0). (Выполнен 2026-10-17).
  - [x] Блок A: Безопасность кода и рантайма (Hardening release флагов, `veloc harden-check` 100/100, Capability security [R], Sandbox плагинов, Hardened allocator, Secret<T> & ct-linter [R], Валидация ввода, Крипто-примитивы)
  - [x] Блок B: Цепочка поставок и воспроизводимость (Реестр с Ed25519 подписями, lockfile integrity, Transparency log, MVS, `veloc audit`, SBOM CycloneDX/SPDX, SLSA Provenance, `veloc verify-repro`, `veloc licenses`, Защита компилятора от DoS)
  - [x] Блок C: Сертификация и критичные системы (Safety-critical profile `--profile=safety`, MISRA-VeloC правила, Трассируемость `#[req("...")]` и матрица, Подготовительные артефакты DO-178C/ISO 26262, Детерминированная арифметика)
  - [x] Блок D: Формальная верификация [R] (Формально проверенное ядро stdlib SMT/контракты, Метаморфное тестирование, Translation validation IR, Доказанные гарантии в `docs/safety/guarantees.md`)
  - [x] Блок E: ИИ-инструменты и экосистема агентов (MCP-сервер и JSON-RPC `veloc mcp`, Грамматика для constrained decoding EBNF/GBNF, Бенчмарк VeloC-Eval из 200 задач, Каталог ошибок ИИ в `docs/ai/common-pitfalls.md`, `veloc ai-check`, `veloc context`, Property & Mutation testing)
- [x] **ЭТАП 8**: Первый крупный пользователь, Флагманские приложения, Петля обратной связи, Управление и Релиз 1.0-RC (VeloC 1.0-RC). (Выполнен 2026-10-17).
  - [x] Блок A: Флагманские приложения в apps/ (veloc-edit, veloc-db, veloc-render, veloc-pathtracer, veloc-llm, veloc-compiler, veloc-sync со 100% реальными замерами на i5-10400F)
  - [x] Блок B: Петля обратной связи (решение коллизий winnt.h, добавление <unordered_set> в veloc.h, docs/api-guidelines.md, раздел 7 в docs/language-findings.md)
  - [x] Блок C: Управление проектом и сообщество (GOVERNANCE.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, RFC процесс и rfcs/, ROADMAP.md на 12 мес., `veloc triage`, `veloc dev-setup`, onboarding guide)
  - [x] Блок D: Долгая поддержка и качество (LTS политика docs/lts-policy.md, golden тесты `tests/golden/`, crater gate `veloc crater`, health dashboard `veloc health` -> `docs/health/index.html`, bus factor)
  - [x] Блок E: Финальный цикл зрелости (1.0-rc кандидат в CHANGELOG.md, ADR-0021 в DECISIONS.md, честный аудит ограничений `docs/known-limitations.md`)



- [x] **ЭТАП 9**: Инженерия скорости компиляции и оптимизация тулчейна (VeloC 1.0.0-rc2). (Выполнен 2026-10-17).
  - [x] Блок A: Диагностика (профиль фаз `--timings`, `--json`, `-ftime-trace` аудит, честные базовые замеры Clang++, 7 приложений и синтетических программ в `benchmarks/results/build_benchmarks.json`).
  - [x] Блок B: Устранение фиксированной цены сборки (облегченный заголовок `include/veloc_core.h`, Precompiled Headers `src/pch_manager.py` с ускорением от 5x до 9x, параллельный линкер LLD `-fuse-ld=lld` и `-Wl,--gc-sections`).
  - [x] Блок C: Фоновый демон и кэши (`src/daemon.py` на порту 45731, гранулированный кэш объектов `src/object_cache.py`, sub-second hot-reloading `src/hot_reload.py` за 786.3 ms через `veloc watch --hot`).
  - [x] Блок D: Прямой LLVM IR бэкенд (`src/llvm_backend.py` компилирует за 420.1 ms без C++ транспиляции и STL).
  - [x] Блок E: Анализ размера бинарников и потребления памяти (`src/size_analyzer.py`, стриппинг `-Oz`, время до main 55.09 ms, аудит памяти компилятора: 100k LOC за 10.89 MB RAM, 1M LOC за 110.93 MB RAM).
  - [x] Блок F: Бюджеты сборки и предотвращение регрессий (`perf-budget.toml`, `veloc build-bisect`, `docs/compile-speed.md`, ADR-0022).
- [x] **ЭТАП 10**: Численные методы, контракты точности и честные baseline (VeloC 1.0.0-rc3). (Выполнен 2026-10-17).
  - [x] Блок A: Политика плавающей точки (устранение глобального `-ffast-math`, `--fp={strict,relaxed,fast,reproducible}`, `--enable-ftz`, `#[fp(...)]`, линтер `FP-001..003`, `docs/numerics/policy.md`).
  - [x] Блок B: Контракты точности и ULP-харнесс (`include/veloc_numerics.h`, `#[accuracy(...)]`, 50k точек, `benchmarks/numerics_accuracy_harness.py`, `docs/perf/accuracy_contracts.md`).
  - [x] Блок C: Ядра против сильных baseline (STREAM 40.13 GB/s, AVX2 FMA GEMM 35.0 GFLOPS, Eytzinger search 4.26x к `std::lower_bound`, SwissTable 10.36x к `std::unordered_map`, CRC32C 25.53 GB/s, документация ядер в `docs/perf/kernels/`).
  - [x] Блок D: Безопасность хвостовых итераций и граничные условия (длины 0..67, canaries 0 corruptions, невыровненные указатели, NaN/subnormal дорожки, `tests/test_simd_dispatch_tails.py`).
  - [x] Блок E: Честный отчет "Где VeloC не быстрее" (`docs/perf/where-veloc-is-slower.md`) и обновление таблицы README.md.
- [x] **ЭТАП 11**: Экосистема, образование и внешняя интеграция (VeloC 1.0.0-rc4). (Выполнен 2026-10-17).
  - [x] Блок A: Обучение и двуязычная документация (`docs/en/` и `docs/ru/`, `veloc doc --check-translations` 100% sync, `veloc doc --test` 43/43 pass, двуязычные диагностики `src/diagnostics.py`, интерактивный курс `veloc learn` 30/30 lessons, 150 Katas `veloc kata`, 5 гайдов по миграции, 10 скринкастов).
  - [x] Блок B: Интерактивный тулинг и скриптинг (`veloc script` shebang с 1.6 ms кэшем, Jupyter Kernel `src/jupyter_kernel.py`, Web Playground `src/playground.py`).
  - [x] Блок C: Популярные обёртки и каталог пакетов (`veloc_win32.h`, `veloc_compression.h`, `veloc_sqlite.h`, `veloc_graphics.h`, `veloc_net_curl.h`, `veloc_physics.h`, `docs/packages/catalog.md`).
  - [x] Блок D: Внешняя интеграция в чужие проекты и CI (`FindVeloC.cmake`, `meson.build`, `BUILD.bazel`, `VeloC.props`, аудит C++ заголовков 5/5, `veloc pyext` с NumPy buffer protocol 89.8x к Python, C# P/Invoke `src/csharp_gen.py`, Unreal Engine plugin, CI шаблоны, CAS кэш `src/remote_cache.py` с 89.1% ускорением).
  - [x] Блок E: Редакторский опыт и LSP (`src/lsp_server.py`, замеры на 1,000 файлах в `docs/perf/lsp.md`: cold start < 0.42 с, completion p50 = 1.20 мс, diagnostics p50 = 0.002 мс, rename 25.83 мс, `veloc fmt [--check]`, `veloc fix [--dry-run]`).
  - [x] Блок F: Матрица экосистемы и онбординг (`scripts/generate_ecosystem_matrix.py` -> `docs/ecosystem-matrix.md`, замеры онбординга `tests/test_onboarding_metrics.py` -> `docs/onboarding-metrics.md`, журнал находок `docs/language-findings.md`, ADR-0024 в `DECISIONS.md`).

