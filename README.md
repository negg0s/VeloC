# VeloC

[![CI](https://github.com/negg0s/VeloC/actions/workflows/ci.yml/badge.svg)](https://github.com/negg0s/VeloC/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

VeloC (Velocity + C) — экспериментальный компилятор и диалект C++, написанный
на Python: исходник `.vc` транслируется в C++ и собирается локальным Clang
(Windows-first). **Статус проекта: исследовательский прототип, не production** —
см. [docs/known-limitations.md](docs/known-limitations.md) и
[docs/audit/claims-audit.md](docs/audit/claims-audit.md).

Открыто и честно:

- работает только на **Windows** (сборка использует `-static`, `-lws2_32`,
  PE-флаги линкера; Linux/macOS не проверялись);
- тулчейн ищется в порядке `VELOC_CLANG` → `clang++` на PATH → типовые пути
  Windows (`C:\Program Files\LLVM\...`, Windhawk-путь); без Clang вы получите
  понятную ошибку, а не сборку «из воздуха»;
- проверенная на этой машине конфигурация: Windows 11, Python 3.12,
  Clang 20.1.x (`--version` показывает найденный компилятор); Clang 18+ —
  минимальная заявка по синтаксису C++20, но она **не проверялась** на всех
  версиях;
- `-march=native` включён по умолчанию для скорости; для переносимых
  бинарников добавлен `build --portable`.

## Требования

- Windows 10/11 x86_64 (Linux/macOS — не проверялись, см. known-limitations)
- Python 3.10+
- Clang 18+ (проверено только на Clang 20.1.3)

## Быстрый старт

```bash
git clone https://github.com/negg0s/VeloC.git
cd VeloC
python veloc.py --version       # версия и найденный Clang
python veloc.py info            # CPU/тулчейн (если Clang не найден — подскажет)
python veloc.py run examples/hello.vc
```

## Пример (`examples/hello.vc`)

```c
fn main() -> i32 {
    printf("Hello, VeloC!\n");
    return 0;
}
```

```bash
python veloc.py run examples/hello.vc      # compile + run
python veloc.py build examples/hello.vc -o app.exe
python veloc.py build examples/hello.vc --profile=safety   # safety-gate
python veloc.py build examples/hello.vc --portable         # без -march=native
```

## Основные команды CLI

Полная таблица 50+ команд со статусом проверки — в
[docs/commands-status.md](docs/commands-status.md). Основные:

| Команда | Описание | Статус на этой машине |
|---|---|---|
| `veloc.py build <file.vc>` | Компиляция .vc → exe | работает |
| `veloc.py run <file.vc>` | Compile + запуск | работает |
| `veloc.py test` | Golden регресс-тесты | 3/3 PASS |
| `veloc.py ci` | Полный набор проверок компилятора | 26/26 PASS (26.0) |
| `veloc.py info` / `hwinfo` | Сведения о тулчейне и железе | работает |
| `veloc.py explain E0001` | Расшифровка кода ошибки | работает |
| `veloc.py health` | Отчёт о здоровье репозитория | работает |
| `veloc.py clean [--all]` | Очистка .cache/build | работает |
| `veloc.py repl`,`playground`,`daemon`,`lsp`,`mcp` … | Сервисы и утилиты | не проверены на этой машине |

## Документы, которые надо читать под фильтром

Историческая документация (CHANGELOG, DECISIONS, PROGRESS, QUEUE,
AUDIT, GOVERNANCE) написана по ходу разработки и содержала утверждения,
которые не подтверждаются проверками ("GA", "100% GREEN", SLSA, крипто).
Незакреплённые утверждения разобраны в `docs/audit/claims-audit.md`;
оригиналы перенесены в `docs/history/` и `docs/dev/` с сохранением текста.

## Структура репозитория

```text
VeloC/
├── src/          # лексер, парсер, кодоген, слои OC/бэкендов (66 модулей)
├── include/      # заголовки времени выполнения (veloc.h, veloc_core.h)
├── examples/     # примеры возможностей языка (используются CI)
├── tests/        # golden тесты, conformance, fuzzing
├── benchmarks/   # скрипты измерений (числа — самозамеры, см. claims-audit)
├── apps/         # приложения (veloc-db, veloc-render, veloc-llm …)
├── docs/         # документация, отчёты аудита, история
├── veloc.py      # CLI-драйвер (единая точка входа)
└── VERSION       # единственный источник версии
```

## Лицензия

Проект распространяется по лицензии MIT. Подробности в файле [LICENSE](LICENSE).
