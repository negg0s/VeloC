# Contributing to VeloC

Thank you for your interest in contributing to VeloC!

## Quick Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/veloc-lang/veloc.git
   cd veloc
   ```
2. Set up the development toolchain:
   ```bash
   python veloc.py dev-setup
   ```
3. Run the complete test suite:
   ```bash
   python veloc.py test
   ```

## Pull Request Guidelines
1. **Target Branch**: Submit all pull requests against the `main` branch.
2. **Formatting & Linting**: Ensure your code passes all linters:
   ```bash
   python veloc.py fmt --check
   python veloc.py lint
   ```
3. **Tests Required**: Every bug fix must include a regression test in `tests/`. Every new feature must include unit tests and an integration test.
4. **Benchmark Verification**: Performance-critical additions must include a benchmark in `benchmarks/` showing zero regression against baseline.
5. **Commit Message Format**: Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `perf:`, `refactor:`).
