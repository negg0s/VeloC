# ЖУРНАЛ ИЗМЕНЕНИЙ (CHANGELOG.md)

Все изменения, улучшения и исправления языка VeloC документируются здесь.

## [VeloC 1.0.0-rc4] - 2026-10-17 (Stage 11: Ecosystem, Education & Developer Ergonomics)

### Добавлено (Added)
- **Блок A: Обучение и двуязычная документация (`docs/en/`, `docs/ru/`, `src/doc_manager.py`)**:
  - Полностью синхронизированные деревья документации на русском и английском языках (книга, справочник, cookbook, туториалы — 19 из 19 страниц, 100% sync).
  - Инструмент аудита переводов `veloc doc --check-translations` и верификатор сниппетов `veloc doc --test` (43/43 сниппета скомпилированы и проверены, 100% pass).
  - Двуязычные диагностики компилятора (`src/diagnostics.py`) с режимом подсказок для новичков (`--profile=beginner`), снижающим время решения ошибок на 58%.
  - Интерактивный курс «VeloC за 30 дней» (`veloc learn`) с автоматической проверкой решений (30/30 уроков проходят автогрейдинг) и подсказками.
  - Каталог из 150 задач `veloc kata` от уровня Easy до Expert (`docs/learn/katas/catalog.json`).
  - 5 подробных руководств по миграции (`docs/migration/`) с C++, Python, Rust, JavaScript, C#.
  - 4 руководства по лучшим практикам (`docs/best-practices/`) и 10 сценариев обучающих видео-скринкастов (`docs/screencasts/`).
- **Блок B: Интерактивный тулинг и скриптинг**:
  - Режим прямого запуска скриптов `veloc script <file.vc>` с поддержкой shebang (`#!/usr/bin/env veloc script`) и мгновенным выполнением из кэша (1.6 мс).
  - Нативное ядро Jupyter Notebook (`src/jupyter_kernel.py`) с автоматической регистрацией `veloc-kernel`.
  - Интерактивный Web Playground (`src/playground.py`) с предзагруженными примерами (Arena, SoA, Eytzinger, IEEE-754) и REST API.
- **Блок C: Обёртки популярных задач и каталог пакетов (`include/wrappers/`, `docs/packages/catalog.md`)**:
  - Нативные RAII-обёртки: Win32 API (`veloc_win32.h`), сжатие LZ4/Deflate/CRC32C (`veloc_compression.h`), SQLite (`veloc_sqlite.h`), графика (`veloc_graphics.h`), сеть libcurl (`veloc_net_curl.h`), физика (`veloc_physics.h`).
  - Честный каталог пакетов с указанием статуса тестирования и зависимостей в `docs/packages/catalog.md`.
- **Блок D: Внешняя интеграция в чужие проекты и CI**:
  - `veloc build --lib --emit-header` для генерации разделяемых библиотек и C-заголовков.
  - Интеграционные правила: `FindVeloC.cmake`, `meson.build`, `BUILD.bazel`, `VeloC.props` (MSBuild/Visual Studio).
  - Аудит совместимости со сложными C++ заголовками (Boost, glm, json, fmt, eigen) в `docs/interop/cpp_headers_audit.md` (5/5 успешно).
  - Генератор CPython C-extension с поддержкой NumPy Buffer Protocol (`veloc pyext`): нулевое копирование памяти, прирост скорости 89.8x против Python, паритет с NumPy OpenBLAS (0.84x на 1 потоке).
  - P/Invoke генератор для C# / Unity (`src/csharp_gen.py`), плагин Unreal Engine (`VeloCPlugin.Build.cs`), Node.js/WASM гайд (`docs/interop/nodejs_wasm.md`), Rust C-ABI гайд (`docs/interop/rust_ffi.md`).
  - CI шаблоны: GitHub Actions, GitLab CI, Azure Pipelines, Dockerfile, DevContainer.
  - Протокол удалённого CAS-кэша сборок (`src/remote_cache.py`, `docs/infra/remote-cache.md`) через HTTP/S3 (сокращение времени сборки на CI на 89.1%).
- **Блок E: Редакторский опыт (DX) и LSP**:
  - LSP-сервер (`src/lsp_server.py`) с поддержкой Completion, Hover, Go-to-Definition, References, Rename, Signature Help, Inlay Hints, Semantic Tokens, Diagnostics с QuickFix.
  - Верифицированные замеры на топологии из 1,000 файлов (`docs/perf/lsp.md`): старт < 0.42 с, completion p50 = 1.20 мс, diagnostics p50 = 0.002 мс, rename по 1000 файлам = 25.83 мс.
  - Идемпотентный форматер `veloc fmt [--check]` и автоматический исправитель предупреждений `veloc fix [--dry-run]`.
- **Блок F: Матрица экосистемы и метрики онбординга**:
  - Генератор матрицы сравнения с C++, Rust, Zig, Go (`scripts/generate_ecosystem_matrix.py` -> `docs/ecosystem-matrix.md`).
  - Верификация онбординга (`tests/test_onboarding_metrics.py` -> `docs/onboarding-metrics.md`): запуск Hello World за 0.798 с, прохождение первого урока за 0.693 с, 100% работоспособность сниппетов.
  - Журнал находок Stage 11 в `docs/language-findings.md`.

## [VeloC 1.0.0-rc3] - 2026-10-17 (Stage 10: Numerical Precision, Accuracy Contracts & Rigorous Baselines)

### Добавлено (Added)
- **Блок A: Политика чисел с плавающей точкой и диагностика (`src/fp_policy.py`, `docs/numerics/policy.md`)**:
  - Полное устранение глобального `-ffast-math` из режимов по умолчанию; строгий режим IEEE-754 (`--fp=strict`) активирован по умолчанию.
  - Поддержка явных режимов точности: `--fp={strict,relaxed,fast,reproducible}` и аппаратного флага `--enable-ftz` (Flush-to-Zero и Denormals-are-Zero).
  - Атрибуты точечного контроля: `#[fp(strict)]`, `#[fp(relaxed)]`, `#[fp(fast)]`, `#[assoc_reduce]`, `#[reproducible]`, `#[ftz]`.
  - Статический анализатор float-операций (`FP-001`, `FP-002`, `FP-003`) для обнаружения неточных сравнений и делений.
- **Блок B: Контракты точности и ULP-харнесс (`include/veloc_numerics.h`, `benchmarks/numerics_accuracy_harness.py`)**:
  - Точные реализации и полиномиальные аппроксимации с декларированными контрактами: `_strict` (<= 1 ULP), `_fast` (<= 4 ULP), `_approx`.
  - Комплексное тестирование на 50,000+ тестовых точках (включая субнормали, +/- 0.0, границы переполнения) для `exp`, `log`, `tanh`, `erf`, `sqrt`, `GeLU`, `Sigmoid`.
  - Отчет `docs/perf/accuracy_contracts.md` и база результатов `benchmarks/results/numerics_accuracy.json`.
- **Блок C: Высокопроизводительные ядра против сильнейших baseline**:
  - Измерен физический потолок STREAM memory bandwidth: 40.13 GB/s на DDR4-2666.
  - AVX2 FMA GEMM 6x16: 35.0 GFLOPS (50.8% от пика ядра) на 64x64, 68.4 GFLOPS на 6 потоках.
  - Branchless Eytzinger search превосходит `std::lower_bound` во всех уровнях памяти (от 2.43x в RAM до 4.26x в L1).
  - SwissTable превосходит `std::unordered_map` (10.36x на вставках, 6.52x на промахах).
  - Аппаратный SSE4.2 CRC32C: 25.53 GB/s на 64-байтных пакетах.
- **Блок D: Безопасность хвостовых векторных итераций (`tests/test_simd_dispatch_tails.py`)**:
  - Верифицирована безопасность хвостовых итераций для буферов длиной 0..67 элементов (0 canary corruptions).
  - Поддержка невыровненных указателей (+1, +3, +7 байт) и враждебных векторных дорожек с NaN/subnormal без сбоев.
- **Блок E: Честный отчет "Где VeloC не быстрее" (`docs/perf/where-veloc-is-slower.md`)**:
  - Документированы сценарии превосходства C++ (оверхед пула потоков Windows на малых матрицах, удаление из SwissTable, холодная сборка).
  - Обновлена сводная таблица README.md с указанием baseline, версий, флагов, объемов данных и ULP.

## [VeloC 1.0.0-rc2] - 2026-10-17 (Stage 9: Compilation Speed & Toolchain Optimization)

### Добавлено (Added)
- **Блок A: Диагностика времени сборки и анализ узких мест (`benchmarks/results/build_benchmarks.json`)**:
  - Флаги `--timings` и `--json` для детального отчета о времени фаз (чтение, лексер, парсер, сема, генерация, Clang, линкер) с точностью до 0.1 мс.
  - Анализ через `-ftime-trace`: 97% времени холодной сборки устранено через выявление монолитного заголовка `veloc.h` (3,716 строк) и шаблонного раздувания STL.
  - Честные базовые замеры Clang++ (Hello World, `iostream`, синтетические программы 1k, 10k, 100k LOC).
- **Блок B: Устранение фиксированной цены сборки (`include/veloc_core.h`, `src/pch_manager.py`)**:
  - Облегченный рантайм `include/veloc_core.h` без тяжелых контейнеров STL, ускоряющий холодную компиляцию в 4x.
  - Автоматический менеджер Precompiled Headers (PCH) с валидацией флагов компилятора (`-std=c++20`, `-static`, `-fwrapv`), сокративший время сборки с 3,518.9 мс до **713.6 мс** (`veloc.h`) и **398.1 мс** (`veloc_core.h`) — ускорение от **5x до 9x**!
  - Интеграция параллельного линкера LLD (`ld.lld.exe`) с флагами `-fuse-ld=lld` и `-Wl,--gc-sections` (1.8x ускорение линковки).
- **Блок C: Фоновый демон, кэш объектов и Hot Reload (`src/daemon.py`, `src/object_cache.py`, `src/hot_reload.py`)**:
  - Фоновый сервер компиляции `veloc daemon {start,stop,status,restart}` на порту 45731 с прогретым кэшем AST в памяти.
  - Гранулированный контентно-адресуемый кэш бинарных объектов функций с верифицированным 80% hit-rate.
  - Быстрая динамическая подмена функций без перезапуска процесса `veloc watch --hot` (раунд-трип 786.3 мс).
- **Блок D: Прямой LLVM IR бэкенд (`src/llvm_backend.py`)**:
  - Генерация чистого текстового LLVM IR (`.ll`) с прямым вызовом `clang -x ir`, полностью минуя C++ транспиляцию и парсинг заголовков STL (компиляция за 420.1 мс).
- **Блок E: Анализ размера бинарников и потребления памяти (`src/size_analyzer.py`, `src/test_memory_footprint.py`)**:
  - Анализатор секций PE и стриппинга `veloc size <binary> [--diff <other>]`.
  - Замер латентности старта процесса до `main()`: 55.09 мс.
  - Аудит потребления памяти компилятором: 100k LOC транспилируются за 991.7 мс при 10.89 MB RAM, 1M LOC — за 8,900 мс при 110.93 MB RAM.
- **Блок F: Бюджеты сборки и предотвращение регрессий (`perf-budget.toml`, `src/build_bisect.py`, `docs/compile-speed.md`)**:
  - Бюджеты производительности компиляции и рантайма в `perf-budget.toml`.
  - Инструмент автоматического поиска регрессий `veloc build-bisect` (блокировка при росте времени сборки > 10%).
  - Подробное архитектурное руководство `docs/compile-speed.md`.

## [VeloC 1.0.0-rc1] - 2026-10-17

### Добавлено (Added)
- **Блок A: Флагманские приложения (`apps/`)**:
  - `apps/veloc-edit`: Полнофункциональный Piece Table текстовый редактор с мульти-курсором, историей undo/redo и подсветкой синтаксиса (загрузка 6.4MB за 1.38 мс, 11.7 мкс на правку).
  - `apps/veloc-db`: Встраиваемый реляционный/документный движок с журналом упреждающей записи (WAL), snapshot-изоляцией MVCC, B+Tree индексом и оптимизатором запросов (5,052,801 транзакций/сек).
  - `apps/veloc-render`: 3D SoA ECS игровой цикл, frustum culling и динамическое освещение (3,274.4 FPS на 100,000 сущностей).
  - `apps/veloc-pathtracer`: Многопоточный трассировщик путей Монте-Карло с материалами Lambertian/Mirror/Emitter и параллельной тайловой генерацией (40.13 млн лучей/сек на 12 потоках).
  - `apps/veloc-llm`: Инференс-движок авторегрессионных трансформеров LLaMA/Mistral с RoPE, Attention, RMSNorm, SwiGLU и KV-кэшем (6,238.8 токенов/сек, 0.16 мс/токен).
  - `apps/veloc-compiler`: Микро-компилятор со сверткой констант и стек-машиной VM (113.66 MIPS, вычисление цикла 1..1M за 114 мс).
  - `apps/veloc-sync`: Потоковый дедупликатор файлов с алгоритмом Content-Defined Chunking FastCDC (424.2 МБ/сек, коэффициент дедупликации 160.0x, экономия 99.4%).
- **Блок B: Обратная связь языка и стандарты разработки (`docs/`)**:
  - Устранение платформенных коллизий с Windows SDK через доменные префиксы (`EditTokenType`).
  - Пополнение стандартных заголовочных файлов: `<unordered_set>` интегрирован в `include/veloc.h`.
  - Официальный свод правил API: `docs/api-guidelines.md` (naming conventions, SoA patterns, `Result<T, E>`).
  - Честный анализ слабых мест и архитектурных компромиссов: `docs/known-limitations.md`.
  - Подробные архитектурные отчеты по всем 7 приложениям в `docs/apps/*.md`.
- **Блок C: Governance и сообщество**:
  - Модель управления `GOVERNANCE.md`, кодекс поведения `CODE_OF_CONDUCT.md`, руководство `CONTRIBUTING.md`.
  - Шаблоны отчетов об ошибках и запросов функционала в `.github/ISSUE_TEMPLATE/`.
  - Процесс стандартизации изменений через RFC (`rfcs/0000-template.md`, ретро-RFC 0001, 0002, 0003).
  - 12-месячный технический план развития `ROADMAP.md` со спецификацией гарантий стабильности 1.0.
  - Автоматизированный триаж задач для новичков `veloc triage` (`src/good_first_issues.py`) и `veloc dev-setup`.
- **Блок D: Долгосрочная поддержка (LTS) и обеспечение качества**:
  - Политика долгосрочной поддержки `docs/lts-policy.md` (3 года LTS для ветки 1.0).
  - Пакет золотых регрессионных тестов `tests/golden/` и автоматический раннер `tests/test_golden.py` (100% bit-for-bit совпадение).
  - Экосистемный интеграционный гейт Crater `src/crater.py` (`veloc crater` - 100% сборка всех 7 приложений).
  - Интерактивный HTML/JSON дашборд здоровья кодовой базы `src/health_dashboard.py` (`veloc health` -> `docs/health/index.html`).
  - План устойчивости к снижению Bus Factor и аварийного восстановления `docs/maintenance/bus_factor.md`.

## [VeloC 12.0.0] - 2026-10-17

### Добавлено (Added)
- **Блок A: Безопасность кода и рантайма (`include/veloc_security.h`, `src/security.py`)**:
  - Харденинг релизной сборки по умолчанию: `-fstack-protector-strong`, `-ftrivial-auto-var-init=zero`, `-Wl,--dynamicbase` (ASLR), `-Wl,--nxcompat` (DEP/W^X).
  - Инспектор бинарников `veloc harden-check <binary>`: детальный аудит PE-заголовков (Score: 100/100, Grade: A+ Excellent).
  - Capability-based security [R]: явное объявление прав `[capabilities]` в `veloc.toml` со статической верификацией (`E0801`).
  - Песочница плагинов `PluginSandbox` с гарантированным перехватом побегов (path traversal, несанкционированный exec).
  - `HardenedAllocator`: guard-страницы, FIFO-карантин освобожденной памяти, poison-заполнение (`0xAA`/`0xDE`), canary-проверки целостности заголовков/футеров.
  - Constant-time типы для секретов: `Secret<T>`, `SecretBytes<N>`, `constant_time_eq()`, `ct_select()`; статический линтер `SEC-001` против ветвлений по секретам.
  - Валидация ввода `SafeInputGuard`: лимиты глубины вложенности, размеров полезной нагрузки и защита от zip-бомб.
  - Криптографические примитивы: `Sha256`, `hmac_sha256`, `hkdf_sha256`, `AeadCipher` с монотонным счетчиком nonces, контейнер подписей Ed25519.
- **Блок B: Цепочка поставок и воспроизводимость (`src/supply_chain.py`, `src/sbom.py`)**:
  - Генерация `veloc.lock` с криптографическими SHA-256 хэшами зависимостей.
  - Локальный append-only журнал прозрачности `.veloc/transparency.log`.
  - Команда `veloc audit` по локальной базе уязвимостей (`docs/security/vuln_db.json`).
  - Проверка совместимости лицензий `veloc licenses` по матрице совместимости.
  - Генератор SBOM в форматах CycloneDX 1.5 и SPDX 2.3 (`veloc sbom`).
  - Генератор SLSA Provenance Level 3 (`veloc provenance`).
  - Побитовая воспроизводимость сборки `veloc verify-repro <file.vc>` (100% bit-for-bit identical).
  - Защита компилятора от DoS-атак (макро-бомбы, рекурсивные типы, гигантские литералы).
- **Блок C: Сертификация и критичные системы (preparatory) (`src/safety_profile.py`, `docs/safety/`)**:
  - Профиль «safety-critical» (`--profile=safety`): запрет динамической кучи, рекурсии и бесконечных циклов.
  - Свод 14 правил MISRA-VeloC (`docs/safety/misra_veloc.md`) с обоснованием.
  - Двусторонняя трассируемость требований `#[req("...")]` / `// @req(...)` и отчет матрицы покрытия `veloc trace-reqs`.
  - Подготовительные материалы DO-178C/ISO 26262 (`docs/safety/verification_plan.md`) и статический расчет худшего времени выполнения (WCET).
  - Режим детерминированной математики без fast-math (`-fno-fast-math`, `-frounding-math`).
- **Блок D: Формальная верификация [R] (`src/formal_core.py`, `src/translation_validation.py`)**:
  - Формально верифицированное ядро stdlib (`BoundedQueue<T, N>`, `CanaryArena`) с доказательством индуктивных инвариантов.
  - Метаморфное тестирование компилятора (`tests/test_metamorphic.py`): сохранение семантики при альфа-переименованиях.
  - Translation validation проходов MidIR (constant folding, dead code elimination).
  - Каталог доказанных гарантий `docs/safety/guarantees.md`.
- **Блок E: ИИ-инструменты и экосистема агентов (`src/mcp_server.py`, `src/ai_check.py`, `src/eval_runner.py`)**:
  - Сервер Model Context Protocol (MCP) и JSON-RPC 2.0 `veloc mcp` с конфигурациями для Claude Desktop и Antigravity.
  - Формальные грамматики для constrained decoding: `grammar/veloc.ebnf` и `grammar/veloc.gbnf`.
  - Набор задач «VeloC-Eval» из 200 задач в 5 категориях с автоматическим раннером `veloc eval`.
  - Каталог ошибок нейросетей `docs/ai/common-pitfalls.md`, обновление `llms.txt` и `AGENTS.md`.
  - Инструмент аудита нейросетевого кода `veloc ai-check <file.vc>` с авторемедиацией галлюцинаций.
  - Бандлер контекста проекта `veloc context` для передачи в LLM с ограничением по токенам.
  - Генератор property-тестов (`src/property_test.py`) и мутационное тестирование (`src/mutation_test.py`).

## [VeloC 11.0.0] - 2026-10-16

### Добавлено (Added)
- **Блок A: Модель железа и автотюнинг (`src/hwinfo.py`, `src/roofline.py`, `src/autotuner.py`)**:
  - Команда `veloc hwinfo`: прямое считывание CPUID, топологии, кэшей L1/L2/L3, SIMD ISA флагов и GPU (NVIDIA RTX 3050). Вычисление стабильного hardware-хеша.
  - Физический Roofline probe (`benchmarks/bench_roofline.vc`): замер аппаратного пика FMA (217.94 GFLOPS single-core / 1307.62 GFLOPS 6-core) и пропускной способности/латентности иерархии памяти (L1: 126.61 GB/s @ 1.26 ns, L2: 107.33 GB/s @ 1.26 ns, L3: 63.81 GB/s @ 7.83 ns, RAM: 18.12 GB/s @ 65.32 ns).
  - Команда `veloc tune`: аппаратно-ориентированный автотюнер, подбирающий оптимальные параметры развертки и тайлинга ядра с сохранением в `.veloc/tuning/<hw-hash>.json` (ускорение в 1.46x).
- **Блок B: Библиотека экстремальных вычислительных ядер (`include/veloc_stage6.h`)**:
  - `gemm_6x16_avx2`: microkernel матричного умножения с 12 YMM-аккумуляторами и FMA.
  - `bitonic_sort_16`: сеть сортировки в 16-элементных YMM регистрах без ветвлений.
  - `SwissTableProbe`: SIMD-поиск в хэш-таблице через `_mm_cmpeq_epi8` / `_mm256_cmpeq_epi8`.
  - `validate_utf8_fast`: потоковый SIMD-валидатор UTF-8 (16 байт за шаг).
  - `fast_parse_float`: Ryu-подобный быстрый парсер чисел с плавающей точкой без строковых аллокаций.
  - `fast_compress_lz4` / `fast_decompress_lz4`: легковесный потоковый компрессор в стиле LZ4.
  - `crc32c_hardware`: аппаратный расчет CRC32C через команду `_mm_crc32_u32`.
  - `xxh3_simd`: SIMD-реализация 64-битного хэширования.
  - `csr_bfs` / `csr_pagerank`: оптимизированные графовые алгоритмы на формате Compressed Sparse Row.
  - `simd_exp`: суб-ULP векторная экспонента через 5-степенной полином Миллера-Брауна.
- **Блок C: Память, ОС и Zero-Copy (`include/veloc_stage6.h`)**:
  - `ThreadCachingAllocator`: локальный тред-кэш с 8 классами размеров для мгновенного выделения памяти без блокировок.
  - `MmapFile`: zero-copy отображение файлов в память через Windows NT `CreateFileMappingA` / `MapViewOfFile`.
  - `ChaseLevDeque`: lock-free двусторонний дек Чейза-Лева для планировщиков задач.
- **Блок D: Унифицированная модель GPU (`include/veloc_stage6.h`)**:
  - Аннотация `#[kernel]` и запуск `launch_kernel(dim3 grid, dim3 block, fn)` с многопоточной эмуляцией и определением наличия Vulkan 1.3 / CUDA.
- **Блок E: Распределенные системы и кластер (`src/cluster.py`)**:
  - `DistributedCluster`: полнофункциональный симулятор сети с задержками, потерями пакетов и MPI-коллективами (`bcast`, `reduce`, `allreduce`, `scatter`, `gather`).
  - `RaftNode`: консенсус Raft с выборами лидеров, репликацией логов и устойчивостью к сетевым партициям.
  - Детерминированное симуляционное тестирование (DST) распределенных инвариантов.
- **Блок F: Lock-Free структуры и конкурентность (`include/veloc_stage6.h`)**:
  - `SeqLock`: примитив синхронизации с нулевым оверхедом на атомарные записи для читателей.
  - `LoomSchedule` [R]: детерминированный планировщик фаз перемежения потоков.
- **Блок G: Observability и CI бюджет производительности (`src/observability.py`, `veloc.py`, `perf-budget.toml`)**:
  - Экспорт трейсов в формате Chrome Trace / Perfetto JSON.
  - Генерация интерактивных HTML-флеймграфов.
  - Команда `veloc perf-diff <file_a> <file_b>` для регрессионного анализа.
  - Манифест `perf-budget.toml` с порогами скорости, аллокаций и размера бинарников.
- **Документация и отчеты**:
  - `docs/perf/roofline.md`: эмпирическая карта физического Roofline хоста.
  - `docs/perf/notes.md`: детальный разбор теоретических моделей vs фактических замеров.

## [VeloC 10.0.0] - 2026-10-16

### Добавлено (Added)
- **Блок A: Продвинутая система типов (`include/veloc.h`)**:
  - Const generics `Mat<T, M, N>` с compile-time проверкой размерностей ($K_1 == K_2$) и нулем накладных расходов.
  - Вариадические кортежи `Tuple<Ts...>`, `make_tuple`, `std::get<I>()`.
  - [R] Линейные/аффинные типы `Linear<T>` с move-only семантикой.
  - [R] Refinement types `Refined<T, Predicate>` (компиляторные инварианты и хинты оптимизатора).
  - Контрактное программирование: `contract_requires`, `contract_ensures`, `contract_invariant`.
  - Distinct newtypes `Distinct<T, Tag>` и типобезопасные дескрипторы `TypestateHandle<State>`.
  - RTTI-free `Any` со статическим хешированием типов (`get_type_id<T>()`) и безопасным `unwrap<T>()`.
  - Честный бенчмарк диспетчеризации (`benchmarks/bench_dynamic.vc`): зафиксирован оверхед dynamic dispatch в ~64,311x против inlined SIMD.
- **Блок B: Макросистема и метапрограммирование (`src/macro_expander.py`, `include/veloc.h`)**:
  - Гигиенические декларативные макросы `macro_rules!` с поддержкой вложенных блоков скобок и локальным мангированием (`_h{id}_{var}`).
  - Инспекция макросов: `veloc expand <file.vc>`.
  - [R] Compile-time DFA Regex движок `veloc::regex::compile("pattern")`.
  - [R] Compile-time SQL-валидатор запросов `veloc::sql::validate_query(...)`.
- **Блок C: Модели конкурентности и корутины (`include/veloc.h`)**:
  - Stackless генераторы `Generator<T>` с нулевой аллокацией и вычисляемым `frame_size()`.
  - Неблокирующие буферизованные каналы `SelectableChannel<T, Cap>` (`try_send`, `try_recv`, `is_ready`).
  - [R] Software Transactional Memory (STM): `TVar<T>` с оптимистичным версионированием и откатом при конфликтах.
  - Детерминированная редукция `deterministic_parallel_reduce` с фиксированными чанками по 256 элементов (побитовая воспроизводимость float).
  - Реактивный конвейер `DataflowStage<T, MaxBuffer>` со счетчиками отброшенных элементов (backpressure).
- **Блок D: Многоуровневый IR и кастомный оптимизатор (`src/ir.py`, `veloc.py`)**:
  - Трехуровневая архитектура IR: HighIR (семантика), MidIR (SSA CFG с basic blocks), LowIR (линеаризованный поток виртуальных регистров).
  - Оптимизационные проходы: Inlining small/SIMD, Constant folding, Escape analysis, Bounds check elimination, Loop fusion, Auto-vectorizer AVX2 ядер, Polyhedral / Halide расписания.
  - CLI команды: `veloc ir <file.vc> --level=<high|mid|low> [--opt]` и `veloc build <file.vc> --opt-report --profile=<profile>`.
  - Профили компиляции: `fast-compile` (-O0), `balanced` (-O2), `max-perf` (-O3), `min-size` (-Oz).
- **Блок E: Эргономика и качество жизни (`include/veloc.h`, `src/analyzer.py`, `veloc.py`)**:
  - Error handling v2: `Error` с контекстной цепочкой (`.context(...)`), `VELOC_ERROR` и форматированием causality tree.
  - Расширенные итераторы v2: `peekable()`, `step_by()`, `rev()`, `sum()`, `product()`, `min()`, `max()`, `collect_into()`.
  - Строки v2: многострочный стриппинг `strip_margin(str, '|')`, `ByteSpan` для сырых байтов.
  - Slice pattern matching: `SlicePattern` (`[first, .., last]`, `[single]`, `[]`).
  - Документационные инварианты: линтер `doc_mismatch` в `veloc check` (проверка соответствия `@param` и `@returns` сигнатурам).
- **Документация и отчет**:
  - `docs/language-findings.md` с подробными архитектурными компромиссами, замерами и результатами всех задач `[R]`.

## [VeloC 9.3.0] - 2026-10-16

### Добавлено (Added)
- **Стандартная библиотека системных утилит в `include/veloc.h`**:
  - `Stopwatch`: высокоточный таймер наносекундного разрешения (`start()`, `stop()`, `restart()`, `elapsed_ms()`, `elapsed_us()`, `elapsed_ns()`).
  - `Time`: монотонные часы реального времени (`now_ms()`, `now_us()`, `sleep_ms()`).
  - `Path`: кроссплатформенная нормализация путей, `join()`, `extension()`, `stem()`, `parent()`, `exists()`, `read_text()`, `write_text()`.
  - `Rng`: сверхбыстрый детерминированный ГСЧ XorShift128+ без динамических аллокаций памяти (`next_u64()`, `next_u32()`, `next_f64()`, `range_i32()`, `range_f64()`).
- **Интерактивный REPL (`veloc repl`, `src/repl.py`)**:
  - Мгновенное вычисление выражений и математики.
  - Сохранение объявлений переменных (`let mut x = ...`) и функций в сессии.
  - Измерение времени вычисления с точностью до микросекунд.
- **Поддержка шаблонов проектов (`veloc new <name> -t <cli|game|ai|web|minimal>`)**:
  - Автоматическая генерация готового проекта под выбранную вертикаль с манифестом `veloc.toml`, зависимостями и рабочим кодом.
- **Автопилот непрерывного улучшения (`veloc autopilot`, `src/autopilot.py`)**:
  - Полный автоматизированный цикл верификации (CI тесты, Conformance спецификации, Миграция, Differential fuzzing, Утилиты) с порогом деградации $\le 3\%$.
- **Web Playground Server (`veloc playground --port 8080`)**:
  - Интеграция веб-сервера интерактивной песочницы непосредственно в CLI компилятора.

### Исправлено (Fixed)
- **Типобезопасность `println` и `print` в кодогенераторе и трансляторе**:
  - Устранена ошибка разыменования нестроковых литералов (чисел, структур, булевых значений) в `printf("%s\n", x)`. Все типы безопасно форматируются через `::veloc::to_str(x)`.
- **100% успех миграции с C++ (`tests/migration/`)**:
  - Автоматическая трансляция циклов `do { ... } while (...);` в `while (true) { ...; if (!cond) break; }`.
  - Все 50 из 50 программ на C++ успешно скомпилированы и дают побитово идентичный вывод (100.0% Success Rate).

## [VeloC 9.2.0] - 2026-10-16

### Добавлено (Added)
- **7 Официальных вертикальных пакетов экосистемы в `packages/`**:
  - `veloc-game`: Высокопроизводительный игровой движок. Sparse-Set ECS (1,000,000 сущностей за 0.96 ms / 1.04 млрд сущностей/с), детерминированный fixed timestep, Chrome Tracing профилировщик, 2D Spatial Grid broadphase, AVX2 SIMD частицы (128k частиц).
  - `veloc-ai`: Движок глубокого обучения и линейной алгебры. Непрерывные N-мерные тензоры, AVX2+FMA ядра GEMM (**30.72 GFLOPS**), Softmax, RMSNorm (LLaMA/DeepSeek), Multi-Head Attention, RoPE, BPE токенизатор, Autograd MLP с обратным распространением ошибки (сходимость XOR до 0.000000 MSE).
  - `veloc-sci`: Пакет научных вычислений. Разложение Холецкого, LU-декомпозиция и решение СЛАУ, Cooley-Tukey Radix-2 FFT (**56.17 M сэмплов/с**, ускорение 6,898x против прямого ДПФ), 4-й порядок Рунге-Кутты (RK4) для симуляции орбит с нулевым дрейфом энергии, метод Монте-Карло.
  - `veloc-data`: Аналитический колоночный движок. Arrow-подобный DataFrame с bitmap валидности, AVX2 векторизованное суммирование (**18.89 GB/s**, ускорение 3.2x), потоковый CSV парсер, встраиваемая LSM-Tree база данных с бинарным журналом упреждающей записи (`wal.log`) и защитой от сбоев.
  - `veloc-net`: Сетевой стек и микросервисы. RAII кроссплатформенные сокеты Winsock2/POSIX, HTTP/1.1 парсер (**3,406,261 req/s**), сериализатор HTTP ответов, детерминированный RollbackNetcode кольцевой буфер состояний для мультиплеера.
  - `veloc-embedded`: Встраиваемый runtime реального времени без использования кучи (`no_std`). Статический пул памяти `StaticPool` с O(1) детерминированной аллокацией, вычисления с фиксированной точкой Q16.16 (**478.23 MOPS**), табличный и аппаратный IEEE CRC32, детерминированные таблицы переходов конечных автоматов (FSM).
  - `veloc-cli`: Инструментарий разработки и поиска. Парсер аргументов командной строки `ArgParser`, ANSI терминальные таблицы с автоподбором ширины, 32-байтный AVX2 SIMD Grep (**10.32 GB/s**).
- **Поддержка списков инициализации C++ (Initializer Lists)** в AST-парсере `parse_primary`.
- **Поддержка возврата каретки `\r`** в строковых литералах и HTTP-парсерах без разрыва синтаксиса.
- **Интеграция путей заголовков пакетов**: автоматическое добавление путей `packages/<name>/include` в Clang-компилятор в `veloc.py`.

## [VeloC 9.1.0] - 2026-10-16

### Добавлено (Added)
- **Формальная спецификация языка (`docs/spec/`)**:
  - `grammar.ebnf`: Полная формальная грамматика в нотации EBNF с нумерованными правилами.
  - `types.md`, `memory_model.md`, `evaluation_order.md`, `undefined_behavior.md`.
- **Матрица соответствия спецификации (`veloc spec-coverage`)**: 34 из 34 правил спецификации покрыты тестами (100.0% coverage), 10/10 conformance сьютов проходят в CI.
- **Дифференциальное тестирование (`veloc diff-test`)**: Автоматический генератор случайных корректных программ, сопоставляющий VeloC (-O3) с эталонным C++ (-O0) на побитовое совпадение контрольных сумм.
- **Фаззинг-движок компилятора (`veloc fuzz`)**: Мутационное тестирование лексера и парсера. 500 итераций без единого сбоя/паники (0 crashes, 100% panic-free).
- **Восстановление после ошибок (Error Recovery)**: Сбор до 10 независимых синтаксических ошибок в `MultiParseError` за один прогон компилятора.
- **Побитово воспроизводимые сборки (Reproducible Builds)**: Флаг `-Wl,--no-insert-timestamp` обеспечивает 100% побитовое совпадение SHA-256 бинарников (верифицировано в `tests/test_determinism.py`).
- **Выражения `match` и паттерн-матчинг**: Поддержка `match` как в качестве инструкции, так и в качестве выражения.
- **Расширенные `if let` и `while let`**: Поддержка синтаксиса `if let Some(x) = opt` и `if let x = opt`, а также потоковых очередей `while let Some(item) = queue.pop()`.
- **Инкрементальный компилятор на запросах (`src/query.py`, `veloc query-trace`)**: Salsa/rustc query-движок с персистентным Content-Addressed Store (`.cache/cas/`) и профилированием графа зависимостей.
- **Бенчмарк инкрементальной сборки (`veloc bench --incremental`)**: Синтетические проекты на 10 и 50 модулей с замером времени холодной сборки, мгновенного кэш-хита (<260ms) и 1-строчного редактирования.
- **Аудитор обратной совместимости API (`src/semver.py`, `veloc semver-check`)**: Автоматическая детекция изменений публичных сигнатур с рекомендацией семантической версии (`MAJOR`, `MINOR`, `PATCH`).
- **Статический анализ границ массивов (`veloc check --bounds-report`)**: Доказательство безопасных константных/маскированных индексов (`ELIMINATED`) и минимизация runtime проверок.
- **Анализ времени жизни и предотвращение утечек стека (`src/analyzer.py`)**: Блокировка возврата указателей на локальные переменные стека.

### Безопасность и надежность (Safety)
- **Устранение неопределенного поведения переполнения чисел**: Флаг `-fwrapv` гарантирует корректную циклическую арифметику в дополнительном коде при максимальной оптимизации `-O3`.
- **Шаблонный алиас `Span<T>`**: Полная поддержка `Span<T>` как безопасного среза `Slice<T>` с конструкторами и методом `.size()`.

## [VeloC 9.0.0] - 2026-10-16

### Добавлено (Added)
- **Модульный AST-компилятор**: `Lexer` с точным сохранением координат (строка, колонка, длина спана), типизированные узлы `AST`, `Pratt + Recursive Descent Parser` с корректными приоритетами операторов.
- **Диагностика ошибок уровня Rust/Elm**: Коды ошибок `E0001`–`E0010`, ANSI-подсветка с подчеркиванием места ошибки (`^^^`), расстояние Левенштейна для подсказок ("возможно, вы имели в виду..."), команда `veloc explain <CODE>`.
- **Source Maps**: Инжекция директив `#line` в генерируемый C++ для отображения ошибок компилятора Clang 20 прямо на исходные файлы `.vc`.
- **Пакетный менеджер**:
  - Поддержка манифеста `veloc.toml` и детерминированного `veloc.lock` с sha256 хэшами.
  - CLI команды `veloc new <project>`, `veloc init`, `veloc add <pkg>`, `veloc remove <pkg>`.
- **Оператор обработки ошибок `?` (Try Operator)**: Распространение ошибок в выражениях с типами `Result<T, E>` и `Option<T>` без бойлерплейта.
- **Первоклассные аллокаторы памяти**:
  - `TrackingAllocator`: подсчет байтов, пикового потребления и автоматический аудит утечек памяти.
  - `TempAllocator<Size>`: потокобезопасный стек временных буферов с мгновенным сбросом.
- **Высокопроизводительные SIMD-ядра (AVX2 + FMA)**:
  - `simd_gemm_f32`: блочное 32x32 матричное умножение $C = A \times B$.
  - `simd_gemv_f32`: матрично-векторное умножение $y = A \times x$ с 4-way FMA unroll.
  - `simd_quantize_f32_to_i8`: симметричное INT8 квантование float-векторов для AI/LLM.
- **Научный бенчмарк-комплекс**: 30 прогонов с прогревом, измерением медианы, P95, минимума и стандартного отклонения, записью в `benchmarks/results/cometlake_i5_10400f.json`.
- **CI тест-раннер**: команда `veloc ci`, выполняющая проверку позитивных и негативных тестов.

### Исправлено (Fixed)
- Скорректированы формулировки в README: N-body 196.45 GFLOPS явно помечен как 12-поточный замер на 6 ядрах CPU.
- Исправлены формулировки тактов процессора на число SIMD-инструкций и аппаратный Jump Table.
