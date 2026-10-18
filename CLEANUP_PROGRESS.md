# Cleanup progress: VeloC
Base commit: b5aae33 (main) | Branch: cleanup/veloc | Started: 2026-10-18

## Environment
- Windows 11 build 26200; Python 3.12.8 (системный — используется проектом).
- Clang: найден автоматически через цепочку `VELOC_CLANG` → PATH → типовые пути Windows; фактически резолвится в `C:\Program Files\Windhawk\Compiler\bin\clang++.exe` (clang 20.1.3). Установка нового Clang не выполнялась.
- GitHub remote существует (https://github.com/NEGG0/VeloC.git), push НЕ выполнялся (правило A5).
- Сторонние (игнорируемые) артефакты на диске: test_tmp.exe, wal.log, game_frame_trace.json, bin/, build/, .cache/, .veloc/ — оставлены как есть (правило: не удалять авторские артефакты, только перечислить).

## Disk
- Before: C free 180.5 GB / D free 1180.29 GB
- After: <см. финальный отчёт>

## Tasks
| ID | Что сделано | Где | Проверка |
|---|---|---|---|
| VC-01 | ROOT_DIR из __file__; CLANG/LLD через src/toolchain.py (env → which → типовые пути); pch_manager и llvm_backend больше не хардкодят D:/C:; cache-server --dir от ROOT_DIR; init печатает относительные пути | veloc.py, src/toolchain.py, src/pch_manager.py, src/llvm_backend.py | veloc.py run/build/info работают после правок |
| VC-02 | hwinfo честный: CIM → /proc/cpuinfo → «unknown»; убраны хардкод-ядро i5-10400F, кэши, SIMD-таблица; GPU без Vulkan-заявлений; render_report обрабатывает unknown | src/hwinfo.py | veloc.py info/hwinfo на этой машине |
| VC-03 | «Быстрый прогон»: --version/info/build/run/test/ci/health/explain/hwinfo | veloc.py | выполнены, результаты в docs/commands-status.md |
| VC-04 | Windows-only флаги (-static, -lws2_32, -Wl,--dynamicbase/--nxcompat/--no-insert-timestamp) за sys.platform; README/known-limitations отражают Windows-only | veloc.py, docs | veloc ci 26/26 |
| VC-05 | --portable (без -march=native); PCH-флаги согласованы с портативностью; предупреждение в README о max-perf/native | veloc.py, src/pch_manager.py | veloc.py build examples/hello.vc (native) OK |
| VC-06 | VERSION файл = 1.0.0; --version, info, dev-setup, package default берут из него; README: «проверено только на Clang 20.1.3» | VERSION, veloc.py | veloc.py --version |
| VC-10 | Safety-профиль: проверки запускаются и на cache-hit | veloc.py | код + ci |
| VC-11 | Кэш-ключ: + fp_mode, lean, enable_ftz, profile, portable + отпечаток всех include/*.h | veloc.py | код |
| VC-12 | BuildError вместо sys.exit в build_veloc; sys.exit только в main/__main__; watch больше не умирает от ошибок сборки | veloc.py | пример: build несуществующего/битого файла → "[VeloC Build Error]"; watch-логика |
| VC-13 | health регистрируется в subparsers (раньше падал "invalid choice") | veloc.py | veloc.py health → отчёт |
| VC-14 | explain: честный вызов diagnostics.explain_error_code; если модуля нет — сообщение вместо NameError | veloc.py | veloc.py explain E0001 |
| VC-15 | try/except Exception: pass в критическом пути заменены на печатные предупреждения (build: нет); прочие swallowedExceptions вне критического пути не тронуты (перечислены?) — частично, критический пайплайн исправлен | veloc.py | diff |
| VC-16 | docs/commands-status.md: таблица с работающими/непроверенными командами | docs/commands-status.md | — |
| VC-20 | В README/claims-audit убраны физически некорректные числа; roofline-цифры помечены «самозамер, не кросс-проверен» с расчётом теоретического потолка; вычисления не переписывались | README, docs/audit/claims-audit.md | — |
| VC-21 | Все неподтверждённые заявления перечислены в docs/audit/claims-audit.md (GA, 100% GREEN, SLSA3, DirectX/Vulkan/Metal, LLM 6238 tok/s, Raft, крипто и т.д.) | docs/audit/claims-audit.md | — |
| VC-22 | known-limitations.md исправлен (2.0-планы убраны; llvm-бэкенд упомянут честно; Linux/macOS — не проверены; Clang 20.1.3 verified) | docs/known-limitations.md | — |
| VC-23 | PROGRESS.md заменён на актуальную страницу; история в docs/history/PROGRESS-2026-10.md | PROGRESS.md, docs/history | — |
| VC-24 | Крипто-заявления (AEAD/Ed25519/X25519/HKDF/SHA-256) помечены в claims-audit: «реализация есть, не для продакшена, NIST/RFC тесты не приложены» | docs/audit/claims-audit.md | — |
| VC-25 | dist/ в .gitignore; ссылок на dist/ в README/CHANGELOG нет (проверено grep) | README, CHANGELOG | grep |
| VC-30 | Служебные файлы перенесены: docs/dev/{AGENTS,AUTOPILOT,QUEUE,AUDIT,AUDIT_FINAL,BENCH_RULES,llms.txt,GOVERNANCE,CODE_OF_CONDUCT,ROADMAP}.md | docs/dev/ | git mv |
| VC-31 | .github/workflows/ci.yml (windows-latest: choco llvm, dev-setup, test, ci); .gitlab-ci.yml и azure-pipelines.yml перенесены в docs/dev/ci-unverified/ | .github/workflows/ci.yml | статически |
| VC-32 | veloc test (3/3) и veloc ci (26/26) пройдены после всех правок | — | вывод |
| VC-33 | git count-objects: 1147 objects, 14.59 MiB (до упаковки 0) — норма | — | вывод |
| VC-README | README переписан (не экспериментальный, Windows-only, таблица команд, ссылки на audit) | README.md | — |

## needs-author
1. Push ветки `cleanup/veloc` на GitHub (правила не дают пушить самостоятельно).
2. Подтвердить/удалить неподтверждённые заявления из docs/audit/claims-audit.md.
3. Rooffine-числа: если цифры 217.94/1307.62 GFLOPS считать правильными — приложить методику (скрипт бенчмарка + условия), иначе исправить.
4. Реестр/SLSA/подписи: опубликовать артефакты или убрать заявления.
5. `docs/health/health_report.json`/`index.html` обновляются командой `veloc health` — возможно стоит gitignore.
6. LICENSE присутствует (MIT) — в отличие от chess-ai, здесь ok.

## Verification summary
- python veloc.py --version → "VeloC 1.0.0"
- python veloc.py info → честные данные (CPU через CIM)
- python veloc.py build/run examples/hello.vc → OK
- python veloc.py test → 3/3 PASS
- python veloc.py ci → 26/26 PASS
- скорость сборки hello.vc: transpile 88 ms + clang 974 ms (базовое «0.3 ms incremental» недоступно: был cache-hit после сброса кэша).
