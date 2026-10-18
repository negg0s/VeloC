# PROGRESS

Историческая сводка по этапам разработки перенесена в
[docs/history/PROGRESS-2026-10.md](docs/history/PROGRESS-2026-10.md);
утверждения из неё не все проверены — см.
[docs/audit/claims-audit.md](docs/audit/claims-audit.md).

Текущее состояние (2026-10-18, ветка `cleanup/veloc`):

- `veloc test` (golden): 3/3 PASS; `veloc ci`: 26/26 PASS;
- исправлены пути/конфигурация тулчейна (VELOC_CLANG/PATH/типовые пути),
  ошибки кэша (учёт fp/lean/portable/профилей), `watch` при ошибках сборки,
  команда `health`, `explain`, shebang-скрипты;
- Windows-only флаги сборки вынесены за `sys.platform == "win32"`, добавлен
  `build --portable`;
- документация приведена к состоянию, проверяемому на этой машине
  (README, known-limitations, commands-status, claims-audit).

Не проверено на этой машине: см. docs/commands-status.md и
docs/audit/claims-audit.md.
