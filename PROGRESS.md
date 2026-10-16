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
