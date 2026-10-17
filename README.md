# VeloC

VeloC (Velocity + C) - диалект системного программирования со строгой статической типизацией, компилируемый в нативный машинный код через бэкенд C++20 / Clang. Проект спроектирован для задач с высокими требованиями к задержке и пропускной способности (HFT, игровые движки, сетевые серверы, высокопроизводительные вычисления).

## Ключевые возможности

- **Детерминированная память**: арены памяти (Arena), линейные аллокаторы, перемотка маркеров (Rewind Markers) и zero-allocation контейнеры (SmallVec, StackString).
- **Векторизация AVX2/FMA3**: встроенные примитивы параллельной обработки данных (GEMM, ArgMax, Softmax, SiLU, RMSNorm, кумулятивные суммы, косинусная схожесть).
- **Предсказуемый рантайм**: отсутствие сборщика мусора (GC), отсутствие скрытых аллокаций, строгий контроль времени жизни объектов.
- **Кэш-эффективные структуры данных**: поиск Eytzinger с упреждающей выборкой строк кэша, хэш-таблицы SwissTable / FlatMap, lock-free MPSC очереди.
- **Стандарты вычислений**: строгий режим IEEE-754 по умолчанию, воспроизводимое параллельное сложение Kahan/Pairwise с контролем ULP-ошибок.

## Быстрый старт

### Требования к системе
- Python 3.10+
- Clang 18+ (с поддержкой C++20)
- Процессор x86_64 с инструкциями AVX2

### Клонирование

```bash
git clone https://github.com/NEGG0/VeloC.git
cd VeloC
```

### Проверка окружения

```bash
python veloc.py --version
python veloc.py hwinfo
```

## Примеры кода

### Hello World (`examples/hello.vc`)

```c
fn main() -> i32 {
    printf("Hello, VeloC!\n");
    return 0;
}
```

Запуск:
```bash
python veloc.py run examples/hello.vc
```

### Арены памяти и Zero-Allocation

```c
fn process_frame() {
    let mut arena = Arena::new(1024 * 1024);
    let marker = arena.mark();

    // Быстрые временные аллокации кадра в непрерывном буфере
    let buffer = arena.alloc_array<f32>(10000);

    // Мгновенный сброс указателя без вызовов free()
    arena.rewind(marker);
}
```

### Векторные операции AVX2

```c
// Скалярное произведение 10 миллионов float на AVX2
let dot = simd_dot_product(vec_a, vec_b, 10000000);

// Быстрый поиск в кэше CPU L1/L2
let index = branchless_lower_bound(sorted_data, count, target);
```

## Основные команды CLI

| Команда | Описание |
|---|---|
| `python veloc.py run <file.vc>` | Сборка и запуск файла |
| `python veloc.py build <file.vc> -o app.exe` | Компиляция исполняемого файла |
| `python veloc.py build <file.vc> --profile=max-perf` | Сборка с оптимизациями (-O3, native tune) |
| `python veloc.py test` | Запуск полного набора регрессионных тестов |
| `python veloc.py check <file.vc>` | Статический анализ типов и времени жизни |
| `python veloc.py fmt <file.vc>` | Форматирование исходного кода |
| `python veloc.py repl` | Интерактивная консоль VeloC |
| `python veloc.py clean --all` | Очистка временных файлов и кэша сборки |

## Архитектура репозитория

```text
VeloC/
├── src/          # Транслятор, лексер, парсер, PCH менеджер, кодогенерация
├── include/      # Заголовочный рантайм (C++20 ядра, SIMD, аллокаторы)
├── examples/     # Практические примеры и витрины возможностей
├── tests/        # Юнит-тесты, golden тесты, проверки компилятора
├── benchmarks/   # Эталонные замеры производительности
├── apps/         # Реальные приложения на VeloC (БД, трассировщик лучей, LLM)
├── docs/         # Спецификация языка, архитектурные решения и руководства
├── veloc.py      # Основной интерфейс командной строки (CLI)
└── veloc.bat     # Windows batch-обёртка для запуска veloc
```

## Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).
