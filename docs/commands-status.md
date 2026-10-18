# Команды veloc.py — статус проверки (на этой машине)

Машина: Windows 11 build 26200, Python 3.12.8, Clang 20.1.3 (Windhawk Compiler
path найден автоматически), CPU 6C/12T. Дата: 2026-10-18.

Критерий «работает»: команда завершилась без трейсбека, с осмысленным
выводом/ошибкой. «Не проверено»: на машине не запускались (нет
инфраструктуры/серверов), но аргумент `--help` у них есть и import-ошибок
при загрузке CLI не обнаружено.

## Ядро компилятора — проверено

| Команда | Статус | Комментарий |
|---|---|---|
| `--version` | работает | печатает VERSION (1.0.0) |
| `build <file.vc>` | работает | hello.vc → exe (Transpile 88 ms + Clang 974 ms) |
| `build --profile=safety` | работает | safety-gate запускается, в т.ч. на кэш-ху (VC-10) |
| `build --backend=llvm` | работает (одинаковый таблицей) | RR через textual LLVM IR; проверен в `veloc ci` |
| `run <file.vc>` | работает | hello.exe запускается, exit 0 |
| `test [file]` | работает | без аргумента — golden 3/3; с файлом — тест-блоки |
| `ci` | работает | 26/26 PASS |
| `clean [--all]` | работает | чистит .cache/build |
| `info` | работает | CPU/Clang/версия (из hwinfo, без фейков) |
| `hwinfo` | работает | отчёт железа; на Windows SIMD-флаги «unknown» (нет CPUID-парсера) |
| `explain <code>` | работает | дешифровка E0001/E0004 и т.п. (src/diagnostics.py) |
| `health` | работает | отчёт репозитория (ранее команда была без парсера — исправлено) |
| `check <file>`, `ir <file>`, `expand`, `from-cpp`, `semver-check`, `query-trace`, `fmt`, `fix` | не проверены на этой машине | есть парсер/`--help`; import-проверок не выполнял |
| `watch <file>` [v] + BuildError | не проверено в live-режиме | исправлено: ошибки сборки больше не убивают watch (VC-12) |

## Сервисы/инфраструктура — не проверены на этой машине

`repl`, `playground`, `daemon`, `lsp`, `mcp`, `tune`, `bench`, `eval`,
`crater`, `diff-test`, `fuzz`, `spec-coverage`, `package`, `registry`,
`bindgen`, `exam`, `wasm`, `pyext`, `script`, `doc`, `kata`, `learn`,
`harden-check`, `audit`, `licenses`, `sbom`, `provenance`, `verify-repro`,
`trace-reqs`, `ai-check`, `context`, `size`, `build-bisect`, `triage`,
`dev-setup`, `perf-diff`, `autopilot`, `cache-server`.

Их наличие проверено только статически (парсер и обработчик определены;
конфигурация CLI загружается без ошибок, что видно по `veloc.py --version`),
но import/запуск каждой из них не выполнялся. CI запускает только
`veloc test` и `veloc ci` — см. .github/workflows/ci.yml.
