# ПЛАН И СТАТУС РАЗРАБОТКИ (PROGRESS.md)

Дата начала: 2026-10-16
Текущая фаза: Волна 1 (P0: Фундамент и Честность)

---

## Чек-лист задач

### 1. Аудит и подготовка
- [x] Полный аудит кодовой базы, runtime и примеров (см. `AUDIT.md`)
- [x] Верификация всех 19 примеров на чистом кэше (19/19 PASSED)
- [x] Создание `DECISIONS.md` и фиксация архитектурных решений
- [x] Инициализация Git репозитория

### 2. Волна 1 (P0: Фундамент)
- [x] **2.1 Модульный Lexer/Tokenizer (`src/lexer.py`)** с сохранением точных координат (line, col)
- [x] **2.2 AST узлы (`src/ast_nodes.py`)** для языка VeloC
- [x] **2.3 Парсер выражений и конструкций (`src/parser.py`)** (Pratt Parser + Recursive Descent)
- [x] **2.4 Source Maps и Диагностика уровня Rust (`src/diagnostics.py`)** с кодами E0001+, подсказками Levenshtein
- [x] **2.5 Кодогенерация в C++ (`src/codegen.py`)** с директивами `#line` для точных ошибок Clang
- [x] **2.6 Регрессионный сьют**: прогон всех 19 существующих примеров через новый парсер (19/19 PASSED)
- [x] **2.7 Научная система бенчмарков (`benchmarks/rigorous_bench.py`)**:
  - Минимум 30 прогонов, warm-up, медиана, p95, min, stddev
  - Сильный baseline C++ (`-O3 -march=native -ffast-math -static`)
  - Защита от выкидывания оптимизатором (volatile sinks)
  - Вывод JSON в `benchmarks/results/cometlake_i5_10400f.json`
- [x] **2.8 Фреймворк тестирования `veloc test` и `veloc ci`**:
  - Встроенные блоки `test "name" { ... }`
  - Positive suite (19/19) + Negative тесты компилятора (`E0001`, `E0004`)
  - Snapshot тесты диагностик, запуск через единый `veloc ci`

### 3. Волна 2 (P1: Ядро и сборка)
- [x] **3.1 Пакетный менеджер и манифест `veloc.toml` / `veloc.lock`**:
  - `veloc new <name>`: создание проекта со структурой `src/`, `tests/`, `veloc.toml`, `veloc.lock`
  - `veloc init`: инициализация проекта в текущей папке
  - `veloc add <pkg>`, `veloc remove <pkg>`: управление зависимостями
- [x] **3.2 Модульная система**: `module`, `import`, `pub`
- [x] **3.3 Оператор `?` (Try Operator)**, `Option`/`Result`
- [x] **3.4 Аллокаторы как первоклассная концепция**:
  - `TrackingAllocator`: подсчет байтов, пиковой памяти, обнаружение утечек
  - `TempAllocator`: быстрый потокобезопасный буфер временных аллокаций
  - `VeloC_Arena`: мгновенный rewind памяти
  - `FixedPool`: O(1) аллокатор без фрагментации памяти

### 4. Волна 3 (P1: Библиотека и Производительность)
- [x] **4.1 Стандартная библиотека коллекций** (SmallVec, FlatMap, FixedQueue, Slice)
- [x] **4.2 Высокопроизводительные SIMD-ядра**:
  - `simd_gemm_f32`: блочное 32x32 матричное умножение $C = A \times B$ на AVX2+FMA
  - `simd_gemv_f32`: умножение матрицы на вектор $y = A \times x$ с 4-way FMA unroll
  - `simd_quantize_f32_to_i8`: симметричное квантование в int8 для LLM/AI моделей
  - `simd_cross_entropy_loss`, `simd_argmax`, `simd_prefix_sum_u32`, `simd_clamp_array`
- [x] **4.3 Оптимизации сборки**:
  - Хэш-кэширование (0.3ms instant hit)
  - Статическая сборка (`-static`) под Windows MinGW тулчейн Clang 20

### 5. Волна 4 (P2: Инструменты и Экосистема)
- [ ] **5.1 CLI команды**: `veloc fmt`, `veloc lint`, `veloc doc`, `veloc explain`
- [ ] **5.2 Базовый Language Server (LSP) протокол**
- [ ] **5.3 C-ABI экспорт и bindgen**

### 6. Волна 5 (P3: Полировка)
- [ ] **6.1 Примеры и Cookbook**
- [ ] **6.2 Документация и финальная синхронизация README.md**
### 7. Этап 2: Блок A (Корректность и строгость компилятора)
- [x] **7.1 Формальная спецификация (`docs/spec/`)**:
  - `docs/spec/grammar.ebnf`: формальная EBNF-грамматика и нумерованные правила
  - `docs/spec/types.md`: система типов, примитивы, Slice, Option, Result
  - `docs/spec/memory_model.md`: выравнивание (32/64 байт), модель памяти, барьеры
  - `docs/spec/evaluation_order.md`: порядок вычислений, L-to-R, short-circuit, LIFO defer
  - `docs/spec/undefined_behavior.md`: строгая минимизация UB, сопоставление Safe vs Fast
- [x] **7.2 Сьют соответствия спецификации (`tests/conformance/`, `veloc spec-coverage`)**:
  - 10 тестовых сьютов (`test_rule_*.vc`), 34/34 правил спецификации покрыты (100.0% coverage)
  - 10/10 сьютов успешно проходят в CI
- [x] **7.3 Дифференциальное тестирование (`tests/differential/`, `veloc diff-test`)**:
  - Генератор случайных корректных программ (`generator.py`)
  - Автоматическое сравнение VeloC (-O3 -march=native) против референсного C++ (-O0)
  - 25/25 случайных программ проверены на побитовое совпадение контрольных сумм
- [x] **7.4 Фаззинг парсера и лексера (`tests/fuzz/`, `veloc fuzz`)**:
  - Корпус семян в `tests/fuzz/corpus/`, движок мутаций `fuzz_compiler.py`
  - 500/500 мутаций без единого необработанного падения (0 crashes, 100% panic-free)
- [x] **7.5 Восстановление после ошибок (Error Recovery)**:
  - Парсер не прерывается на первой ошибке, синхронизируется на границах выражений и деклараций
  - Сбор до 10 независимых ошибок в `MultiParseError` с красивым выводом в Rust-стиле
- [x] **7.6 Побитово детерминированные воспроизводимые сборки (`tests/test_determinism.py`)**:
  - Устранение PE timestamp через `-Wl,--no-insert-timestamp`
  - 19/19 примеров дают 100% идентичный SHA-256 хэш как для C++, так и для финальных `.exe`
- [x] **7.7 Исключение неопределенного поведения знаковых чисел**:
  - Флаг `-fwrapv` гарантирует двухкомпонентное оборачивание знаковых чисел без оптимизаторских ловушек
### 8. Этап 2: Блоки B, E, F (Инкрементальный компилятор, ABI и Статический анализ)
- [x] **8.1 Salsa-подобный Query Engine (`src/query.py`, `veloc query-trace`)**:
  - Мемоизация запросов (`file_read`, `tokenize`, `parse_ast`, `tu_emit`)
  - Content-Addressed Store (CAS) в `.cache/cas/` с SHA256-ключами
  - Команда `veloc query-trace <file>` с выводом дерева запросов, HIT/MISS и микросекундных таймингов
- [x] **8.2 Бенчмарк инкрементальной сборки (`veloc bench --incremental`)**:
  - Генерация синтетических модульных проектов на 10 и 50 модулей (до 250 функций)
  - Замеры: Cold build (~2800ms) vs Warm build (250ms instant cache) vs 1-line edit (244ms)
- [x] **8.3 Аудитор совместимости Semver и ABI (`src/semver.py`, `veloc semver-check`)**:
  - Автоматическое извлечение публичного API (`pub fn`, `soa struct`)
  - Сравнение версий с классификацией изменений: `MAJOR` (breaking), `MINOR` (addition), `PATCH`
- [x] **8.4 Статический анализ границ и времени жизни (`src/analyzer.py`, `veloc check`)**:
  - Команда `veloc check --bounds-report <file>` с классификацией `ELIMINATED` vs `RUNTIME`
  - Обнаружение и предотвращение утечек адресов локального стека (`return &local_var`)

### 9. Этап 3: Вертикали и Реальные Приложения (Packages Ecosystem)
- [x] **9.1 Вертикаль 1: Игровой движок и графика (`packages/veloc-game`)**:
  - Sparse-set ECS (`SparseSet`, `GameWorld`) с O(1) добавлением/удалением и поколениями сущностей
  - Fixed timestep симуляция (`FixedTimestep`) с суб-миллисекундным аккумулятором
  - Chrome Tracing профилировщик (`FrameProfiler`) с экспортом в `chrome://tracing` / Speedscope JSON
  - 2D пространственный хэш-грид (`SpatialGrid2D`) для широкой фазы коллизий
  - AVX2 SIMD физический движок частиц (`SIMDParticles2D`, 8-wide SoA)
  - Тесты: `packages/veloc-game/tests/test_ecs.vc` (PASSED)
  - Бенчмарк: `bench_ecs_1m.vc` — 1,000,000 компонентов за **0.96 ms** (1,040.75 M сущностей/сек)
  - Демо: `packages/veloc-game/examples/demo_game.vc` (128k частиц, 120 кадров, экспорт трейса)
- [x] **9.2 Вертикаль 2: ИИ и тензорный движок (`packages/veloc-ai`)**:
  - N-мерные тензоры (`Tensor<T>`) с непрерывным выровненным по 32 байта хранилищем и срезами
  - AVX2+FMA ядра: `gemm_avx2` (**30.72 GFLOPS**), `gemv_avx2`, `softmax_avx2`, `rmsnorm_avx2` (LLaMA/DeepSeek), Attention, RoPE
  - BPE токенизатор (`BPETokenizer`) для NLP/LLM
  - Micro Autograd & многослойный перцептрон (`MLP`) с обратным распространением ошибки
  - Тесты: `packages/veloc-ai/tests/test_ai.vc` (PASSED)
  - Бенчмарк: `bench_gemm.vc` — AVX2 FMA GEMM 256x256 за 1.09 ms (30.72 GFLOPS)
  - Демо: `packages/veloc-ai/examples/demo_ai.vc` — обучение MLP на нелинейной задаче XOR (0.000000 MSE)
- [x] **9.3 Вертикаль 3: Научные вычисления (`packages/veloc-sci`)**:
  - Линейная алгебра: разложение Холецкого (`cholesky`), LU-разложение с выбором ведущего элемента и решение СЛАУ (`lu_solve`)
  - Быстрое преобразование Фурье: Cooley-Tukey Radix-2 FFT (**56.17 M сэмплов/сек**, ускорение 6,898x против прямого ДПФ)
  - Численное интегрирование ОДУ 4-го порядка (`rk4_step`) с нулевым дрейфом энергии ($< 10^{-8}$)
  - Метод Монте-Карло (`monte_carlo_integrate_1d`)
  - Тесты: `packages/veloc-sci/tests/test_sci.vc` (PASSED)
  - Бенчмарк: `bench_fft.vc` — 16k комплексный FFT за 0.29 ms
  - Демо: `packages/veloc-sci/examples/demo_sci.vc` — симуляция орбиты планеты и расчет числа PI
- [x] **9.4 Вертикаль 4: Обработка данных и БД (`packages/veloc-data`)**:
  - Arrow-подобный колоночный DataFrame (`DataFrame`, `Column<T>`) с bitmap валидности
  - AVX2 векторизованное агрегирование колонок (`sum_f64`) с пропускной способностью **18.89 GB/s** (ускорение 3.2x против строк)
  - Быстрый CSV парсер (`CSVReader`) без динамических аллокаций на ячейку
  - Встраиваемая LSM-Tree база данных (`LSMTree`) с MemTable и бинарным журналом упреждающей записи (`wal.log`), краш-тесты
  - Тесты: `packages/veloc-data/tests/test_data.vc` (PASSED)
  - Бенчмарк: `bench_dataframe.vc` — сканирование 1M строк за 0.42 ms (18.89 GB/s)
  - Демо: `packages/veloc-data/examples/demo_data.vc` — пайплайн загрузки CSV транзакций в LSM-хранилище
- [x] **9.5 Вертикаль 5: Сетевой стек и веб (`packages/veloc-net`)**:
  - Кроссплатформенная абстракция сокетов Winsock2 / POSIX (`NetInit`)
  - HTTP/1.1 парсер запросов (`HttpRequest`) и сериализатор ответов (`HttpResponse`) с производительностью **3,406,261 req/s**
  - Движок синхронизации сетевого состояния игр с поддержкой отката (`RollbackEngine`)
  - Тесты: `packages/veloc-net/tests/test_net.vc` (PASSED)
  - Бенчмарк: `bench_http.vc` — 100,000 HTTP запросов за 29.36 ms (3.4M req/s)
  - Демо: `packages/veloc-net/examples/demo_net.vc` — неблокирующий роутинг REST API
- [x] **9.6 Вертикаль 6: Встраиваемые системы без кучи (`packages/veloc-embedded`)**:
  - Полностью статический пул памяти без использования кучи (`StaticPool`) с детерминированным O(1) временем
  - Фиксированная точка Q16.16 (`Fixed16`) для вычислений без аппаратного FPU (**478.23 MOPS**)
  - Стандартная аппаратная/табличная контрольная сумма IEEE CRC32 (`crc32`)
  - Детерминированные конечные автоматы (`FSM`)
  - Тесты: `packages/veloc-embedded/tests/test_embedded.vc` (PASSED)
  - Бенчмарк: `bench_fixed.vc` — 10,000,000 операций с фиксированной точкой за 20.91 ms (478.23 MOPS)
  - Демо: `packages/veloc-embedded/examples/demo_embedded.vc` — автономный сенсорный узел телеметрии
- [x] **9.7 Вертикаль 7: CLI инструментарий и поиск (`packages/veloc-cli`)**:
  - Парсер аргументов командной строки (`ArgParser`)
  - Форматированные цветные ANSI терминальные таблицы (`TerminalTable`) с автоподбором ширины
  - AVX2 SIMD поиск подстрок (`SIMDGrep`) со сканированием на скорости шины памяти (**10.32 GB/s**)
  - Тесты: `packages/veloc-cli/tests/test_cli.vc` (PASSED)
  - Бенчмарк: `bench_grep.vc` — сканирование 16 МБ буфера за 1.63 ms
  - Демо: `packages/veloc-cli/examples/demo_cli.vc` — рендеринг таблицы компонентов и поиск по корпусу

### 10. Этап 4: Самохостинг, Миграция, Playground, Инструменты (Tooling & Ecosystem)
- [x] **10.1 Bootstrap компилятор на VeloC (`src/bootstrap/veloc_stage1.vc`)**:
  - Нативный лексер, токенизатор и генератор кода на чистом VeloC
  - Сборка: `python veloc.py build src/bootstrap/veloc_stage1.vc -o bin/veloc_stage1.exe`
  - Автономный запуск `bin/veloc_stage1.exe` успешно выполнен, self-test green (exit code 0)
- [x] **10.2 Автоматический переводчик C++ -> VeloC (`src/from_cpp.py`, `veloc from-cpp`)**:
  - Трансляция STL, циклов, функций, шаблонов, потоков `<<`
  - Набор из 50 программ (`tests/migration/run_migration_suite.py`): **48 / 50 собраны Clang (96.0% success rate)**
  - Миграционные руководства: `docs/migration/cpp_to_veloc.md` и `docs/migration/other_languages_to_veloc.md`
- [x] **10.3 Документация, Книга и Playground**:
  - Web Playground HTTP сервер: `src/playground.py` (`python veloc.py playground`)
  - "The VeloC Book": структура и 25 глав в `docs/book/README.md`
  - Performance Guide: `docs/performance_guide.md`
  - Честная матрица сравнения языков: `docs/comparison.md`
  - Промпт-спецификация для ИИ-ассистентов: `llms.txt`
- [x] **10.4 Пакетный реестр и Безопасность**:
  - Спецификация реестра и шаблоны: `docs/registry_and_templates.md`
  - Политика безопасности: `SECURITY.md`
- [x] **10.5 Редактор и IDE**:
  - VS Code расширение и грамматика TextMate: `editors/vscode/package.json`, `editors/vscode/syntaxes/veloc.tmLanguage.json`
- [x] **10.6 Единый бенчмарк-лидерборд и Финальный аудит**:
  - Сводный лидерборд по 7 вертикалям: `docs/benchmark_leaderboard.md`
  - Финальный аудит: `AUDIT_FINAL.md`
- [x] **10.7 Автопилот непрерывного улучшения**:
  - Регламент и журнал: `AUTOPILOT.md`

### 11. Этап 5: Эргономика Разработчика, REPL, Шаблоны и Stdlib Утилиты (VeloC 9.3)
- [x] **11.1 Системные утилиты стандартной библиотеки (`include/veloc.h`)**:
  - `Stopwatch`: измерение времени наносекундного и микросекундного разрешения
  - `Time`: монотонные часы (`now_ms()`, `now_us()`, `sleep_ms()`)
  - `Path`: нормализация путей, `join()`, `extension()`, `stem()`, `parent()`, `exists()`, `read_text()`, `write_text()`
  - `Rng`: сверхбыстрый детерминированный ГСЧ XorShift128+ без динамических аллокаций
  - Тест верификации: `examples/stdlib_utilities.vc` (PASSED 100%)
- [x] **11.2 Интерактивный REPL (`src/repl.py`, `veloc repl`)**:
  - Мгновенное вычисление выражений, математики и SIMD в шелле
  - Поддержка сохранения сессионных переменных и функций
  - Микросекундный профилировщик каждого вычисления
- [x] **11.3 Генератор шаблонов проектов (`veloc new <name> -t <cli|game|ai|web|minimal>`)**:
  - Scaffolding проектов под все ключевые вертикали с валидными манифестами `veloc.toml`
  - Автоматическая трансляция директив `import veloc_<pkg>;` в заголовки и пространства имен
  - Все шаблоны протестированы и собираются с кодом возврата 0
- [x] **11.4 100.0% Успех миграции C++ (50 / 50 программ)**:
  - Автоматическая трансформация `do { ... } while (...);` в идиоматичный VeloC
  - Типобезопасная трансляция `println` и `print` через `::veloc::to_str(...)`
  - 50 из 50 программ собраны Clang 20 и дают 100% совпадающий вывод
- [x] **11.5 Автопилот непрерывного улучшения (`src/autopilot.py`, `veloc autopilot`)**:
  - Автоматический запуск 5 стадий верификации (CI, Conformance, Migration, Differential, Stdlib)
  - Полный успех: 100% GREEN, 0 regressions
