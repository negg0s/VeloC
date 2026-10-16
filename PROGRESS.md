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
