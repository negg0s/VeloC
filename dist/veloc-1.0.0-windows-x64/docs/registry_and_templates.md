# Package Registry Specification: VeloC Local & Enterprise Registry

The VeloC Package Registry provides decentralized, hash-authenticated package distribution for projects and libraries.

---

## 1. Registry Architecture
- **Index Repository**: Git-backed or HTTP REST JSON index mapping package names to version metadata.
- **Package Archive**: Tarball / Zip archives identified by content-addressed SHA-256 digests (`.tar.gz` or `.zip`).
- **Semantic Versioning Enforcement**: Registries reject broken versions violating Semver rules (`MAJOR.MINOR.PATCH`).

---

## 2. API Endpoints
- `GET /index/:package`: Returns package releases, dependencies, and SHA-256 hashes.
- `PUT /publish`: Uploads signed package archive accompanied by `veloc.toml`.
- `POST /yank/:package/:version`: Deprecates a compromised or broken release while preserving reproducible lockfiles.

---

## 3. Project Templates (`veloc new --template`)
VeloC includes built-in official project templates for rapid scaffolding:
1. `veloc new my_game --template game`: Configured with `veloc-game` (ECS, 2D grid, fixed timestep).
2. `veloc new my_ai --template ai`: Configured with `veloc-ai` (Tensors, FMA GEMM, Autograd).
3. `veloc new my_service --template web`: Configured with `veloc-net` (Async HTTP/1.1 REST gateway).
4. `veloc new my_firmware --template embedded`: Configured with `veloc-embedded` (No-heap `StaticPool`, Fixed16).
5. `veloc new my_tool --template cli`: Configured with `veloc-cli` (ArgParser, TerminalTable, SIMD search).
