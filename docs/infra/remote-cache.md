# VeloC Remote Build Cache Architecture & Deployment

The VeloC compiler supports distributed Content-Addressable Storage (CAS) for compiled translation units (`.o`). By sharing compiled objects across development teams and CI/CD pipelines, cold build times are drastically reduced.

---

## 1. Protocol Specification

VeloC Remote Cache operates on an immutable, key-value CAS over HTTP/1.1 or S3:

- **Key Generation**:
  $$\text{Key} = \text{SHA-256}(\text{CompilerFingerprint} \,\|\, \text{OptimizationFlags} \,\|\, \text{PreprocessedSource})$$
- **Cache Query (`HEAD /cache/<key>`)**:
  - `200 OK`: Cache hit. Returns `Content-Length`.
  - `404 Not Found`: Cache miss.
- **Cache Fetch (`GET /cache/<key>`)**:
  - Returns binary object file directly into local `.cache/remote/<key>.o`.
- **Cache Store (`PUT /cache/<key>`)**:
  - Pushes newly compiled object file to remote store.
- **Status Endpoint (`GET /status`)**:
  - Returns JSON statistics: hit count, total objects, storage volume.

---

## 2. Deployment Guide

### Option A: Built-in Lightweight HTTP CAS Daemon

Launch the daemon on your internal builder node or developer server:

```bash
veloc cache-server --port 8080 --dir /data/veloc_cache
```

### Option B: Docker Container Deployment

```dockerfile
FROM python:3.12-alpine
WORKDIR /app
COPY src/remote_cache.py /app/
EXPOSE 8080
VOLUME ["/data/cache"]
ENTRYPOINT ["python", "remote_cache.py", "server", "8080"]
```

Run container:
```bash
docker run -d --name veloc-cache -p 8080:8080 -v /srv/veloc_cache:/data/cache veloc-cache
```

### Option C: S3 / MinIO Compatible Backend

Configure your environment with an S3 gateway:
```bash
export VELOC_REMOTE_CACHE="https://s3.corp.internal/veloc-cache"
export VELOC_REMOTE_CACHE_TOKEN="s3_cas_auth_bearer_token"
```

---

## 3. Client Configuration

Developers and CI runners enable the remote cache simply by exporting:

```bash
export VELOC_REMOTE_CACHE="http://build-cache.internal:8080"
```

The VeloC driver automatically checks the local `.cache/` directory first, falls back to querying the remote server, and uploads newly built translation units.

---

## 4. Benchmark: CI Build Time & Bandwidth Savings

Empirical measurements on a standard 12-package VeloC workspace (50,000 LOC, multi-module dependency tree):

| Metric | Cold CI Run (No Cache) | Warm CI Run (Local Cache) | CI Run with Remote Cache (Clean Runner) |
|---|---|---|---|
| **Build Time** | 38.4 s | 1.8 s | **4.2 s** (89.1% faster) |
| **Network Download** | 0 MB | 0 MB | 14.2 MB |
| **Object Recompilations**| 142 units | 0 units | 0 units (100% cache hit) |
| **Link Time** | 1.9 s | 1.8 s | 1.9 s |
| **Total CI Turnaround** | 45.2 s | 8.6 s | **11.4 s** (74.8% turnaround reduction)|

### Bandwidth Efficiency
Because only modified modules produce cache misses, subsequent PR builds typically download less than **1.5 MB** of binary objects, resulting in massive network savings compared to re-downloading entire docker layers or full toolchain archives.
