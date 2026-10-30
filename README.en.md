# VeloC

VeloC is an experimental C++ dialect and source-to-source compiler written in Python. It translates `.vc` files to C++ and builds them with the local Clang. The current implementation is Windows-first.

Status: research prototype, not production. See [docs/known-limitations.md](docs/known-limitations.md) and [docs/audit/claims-audit.md](docs/audit/claims-audit.md).

## What works on the reference machine

- Windows 10/11 x86_64
- Python 3.10+
- Clang 18+ (tested with Clang 20.1.3)
- `veloc.py build` and `veloc.py run`
- Golden tests and the CI health check
- `info`, `hwinfo`, `explain`, and `clean`

## Quick start

```bash
git clone https://github.com/negg0s/VeloC.git
cd VeloC
python veloc.py --version
python veloc.py info
python veloc.py run examples/hello.vc
```

## Example

```c
fn main() -> i32 {
    printf("Hello, VeloC!\n");
    return 0;
}
```

```bash
python veloc.py run examples/hello.vc
python veloc.py build examples/hello.vc -o app.exe
python veloc.py build examples/hello.vc --profile=safety
python veloc.py build examples/hello.vc --portable
```

## Status

The README and the audit files in `docs/` separate verified behavior from planned work. Commands that are not verified on the reference machine are marked as such in [docs/commands-status.md](docs/commands-status.md).

## License

MIT. See [LICENSE](LICENSE).
