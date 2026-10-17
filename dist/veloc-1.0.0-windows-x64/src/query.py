# VeloC Query-Based Incremental Engine (inspired by Salsa / rustc)
# Manages fine-grained query dependencies, memoization, and content-addressed caching.

import time
import hashlib
from typing import Dict, Any, Callable, Optional, List, Tuple
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class QueryRecord:
    name: str
    key: str
    duration_ms: float
    hit: bool
    dependencies: List[str] = field(default_factory=list)

class QueryEngine:
    def __init__(self, cas_dir: Optional[Path] = None):
        self.cas_dir = cas_dir
        if self.cas_dir:
            self.cas_dir.mkdir(parents=True, exist_ok=True)
        self.memo: Dict[str, Any] = {}
        self.trace: List[QueryRecord] = []
        self._current_query_stack: List[str] = []

    def clear(self):
        self.memo.clear()
        self.trace.clear()
        self._current_query_stack.clear()

    def query(self, name: str, key: str, compute_fn: Callable[[], Any]) -> Any:
        full_key = f"{name}:{key}"
        if self._current_query_stack:
            parent = self._current_query_stack[-1]
            # Track dependency
            for rec in reversed(self.trace):
                if rec.key == parent:
                    rec.dependencies.append(full_key)
                    break

        # Check memory cache
        if full_key in self.memo:
            self.trace.append(QueryRecord(name, full_key, 0.05, hit=True))
            return self.memo[full_key]

        # Check on-disk CAS
        if self.cas_dir:
            cas_file = self.cas_dir / f"{hashlib.sha256(full_key.encode()).hexdigest()}.cas"
            if cas_file.exists():
                try:
                    import pickle
                    val = pickle.loads(cas_file.read_bytes())
                    self.memo[full_key] = val
                    self.trace.append(QueryRecord(name, full_key, 0.2, hit=True))
                    return val
                except Exception:
                    pass

        # Compute query
        self._current_query_stack.append(full_key)
        t0 = time.perf_counter()
        result = compute_fn()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self._current_query_stack.pop()

        self.memo[full_key] = result
        self.trace.append(QueryRecord(name, full_key, elapsed_ms, hit=False))

        # Store in CAS
        if self.cas_dir:
            try:
                import pickle
                cas_file = self.cas_dir / f"{hashlib.sha256(full_key.encode()).hexdigest()}.cas"
                cas_file.write_bytes(pickle.dumps(result))
            except Exception:
                pass

        return result

    def print_trace(self):
        print("==================================================")
        print("          VeloC Query Execution Trace             ")
        print("==================================================")
        total_time = sum(r.duration_ms for r in self.trace)
        hits = sum(1 for r in self.trace if r.hit)
        misses = len(self.trace) - hits
        print(f"Total Queries: {len(self.trace)} (Hits: {hits}, Misses: {misses}, Total: {total_time:.2f}ms)\n")
        print(f"{'Status':<8} {'Time (ms)':<10} {'Query Key'}")
        print("-" * 65)
        for r in self.trace:
            status = "[HIT]" if r.hit else "[MISS]"
            print(f"{status:<8} {r.duration_ms:<10.2f} {r.key[:55]}")
        print("==================================================")
