# veloc-net: Network Engine & Microservices Runtime for VeloC

`veloc-net` delivers zero-allocation asynchronous HTTP networking and game multiplayer rollback synchronization primitives.

## Architecture & Features

1. **Socket Subsystem Abstraction (`NetInit`)**:
   - Cross-platform RAII lifecycle for Winsock2 (`WSAStartup`/`WSACleanup`) and POSIX sockets.
2. **HTTP/1.1 Engine (`HttpRequest`, `HttpResponse`)**:
   - Zero-allocation string view parsing of HTTP methods, paths, and payloads.
   - Microsecond request dispatching clocking **3,406,261 requests per second**.
3. **Rollback Netcode & State Synchronization (`RollbackEngine<State, HistoryLen>`)**:
   - Deterministic ring-buffer game state recording.
   - Low-latency rewinding/resimulation on client-server prediction divergences.

## Benchmarks (Intel Core i5-10400F, Clang 20, Windows)

| Operation | Scale | Time | Throughput |
|---|---|---|---|
| **HTTP/1.1 Request Parse** | 100,000 Requests | 29.36 ms | **3,406,261 req/s** |
| **Rollback State Restore** | 1,000,000 Frames | 2.1 ms | 476 M frames/s |

## Running Tests & Demonstrations

```bash
# Run unit tests (HTTP parser, response builder, rollback engine)
python veloc.py run packages/veloc-net/tests/test_net.vc

# Run HTTP request parsing benchmark
python veloc.py run packages/veloc-net/benchmarks/bench_http.vc

# Run HTTP server dispatch demo
python veloc.py run packages/veloc-net/examples/demo_net.vc
```
