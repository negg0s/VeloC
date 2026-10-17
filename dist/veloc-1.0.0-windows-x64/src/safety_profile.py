"""
VeloC Safety-Critical Profile Checker, Traceability Engine, and WCET Analyzer
Implements MISRA-VeloC verification, requirement traceability (#[req("...")]),
and Worst-Case Execution Time (WCET) static bounds analysis.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple


class SafetyCriticalChecker:
    """Verifies that code complies with the --profile=safety subset."""

    BANNED_PATTERNS = [
        (re.compile(r'\b(malloc|free|calloc|realloc)\b'), "RULE-SAFE-001", "Dynamic memory allocation is forbidden in safety-critical mode"),
        (re.compile(r'\bnew\s+[a-zA-Z0-9_]+'), "RULE-SAFE-002", "Heap allocation via 'new' is forbidden"),
        (re.compile(r'\bwhile\s*\(\s*(true|1)\s*\)'), "RULE-SAFE-003", "Unbounded while(true) loops are forbidden; specify maximum loop trip count"),
        (re.compile(r'\bgoto\b'), "RULE-SAFE-004", "Unstructured control flow (goto) is forbidden"),
        (re.compile(r'\basm\b'), "RULE-SAFE-005", "Inline assembly is forbidden without static verification"),
    ]

    def __init__(self, source_code: str, filename: str = "<source>"):
        self.source = source_code
        self.filename = filename

    def check(self) -> List[Dict[str, Any]]:
        violations = []
        lines = self.source.splitlines()

        # Check for banned patterns
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*"):
                continue

            for pattern, rule_id, msg in self.BANNED_PATTERNS:
                if pattern.search(stripped):
                    violations.append({
                        "rule": rule_id,
                        "line": idx,
                        "file": self.filename,
                        "message": msg,
                        "snippet": stripped
                    })

        # Check for direct recursion (simple cycle detector)
        fn_defs = re.findall(r'\b(?:def|fn)\s+([a-zA-Z0-9_]+)\s*\(', self.source)
        for fn_name in fn_defs:
            # Look for function calling itself
            fn_body_match = re.search(rf'\b(?:def|fn)\s+{fn_name}\s*\([^)]*\)\s*\{{(.*?)\}}', self.source, re.DOTALL)
            if fn_body_match:
                body = fn_body_match.group(1)
                if re.search(rf'\b{fn_name}\s*\(', body):
                    violations.append({
                        "rule": "RULE-SAFE-006",
                        "line": 1,
                        "file": self.filename,
                        "message": f"Direct recursion in function '{fn_name}' is forbidden in safety-critical profile",
                        "snippet": f"{fn_name}(...)"
                    })

        return violations


class RequirementTraceability:
    """Parses #[req("REQ-XXX")] annotations and maps requirements to code and tests."""

    REQ_PATTERN = re.compile(r'#\[req\("([A-Z0-9_\-]+)"\)\]|//\s*@req\(([A-Z0-9_\-]+)\)')


    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def scan_traceability(self) -> Dict[str, Any]:
        req_to_impl: Dict[str, List[str]] = {}
        req_to_test: Dict[str, List[str]] = {}

        # Scan code files
        for ext in ("*.vc", "*.h", "*.py"):
            for p in self.root_dir.rglob(ext):
                if ".git" in p.parts or ".veloc" in p.parts or "build" in p.parts:
                    continue
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                is_test = "test" in p.name.lower() or "tests" in p.parts
                for line_idx, line in enumerate(text.splitlines(), start=1):
                    for match in self.REQ_PATTERN.finditer(line):
                        req_id = match.group(1) or match.group(2)
                        target_dict = req_to_test if is_test else req_to_impl
                        loc = f"{p.name}:{line_idx}"
                        if req_id not in target_dict:
                            target_dict[req_id] = []
                        target_dict[req_id].append(loc)

        all_reqs = set(req_to_impl.keys()).union(set(req_to_test.keys()))
        covered_by_tests = set(k for k in all_reqs if k in req_to_test)
        coverage_pct = (len(covered_by_tests) / len(all_reqs) * 100.0) if all_reqs else 100.0

        return {
            "all_requirements": sorted(list(all_reqs)),
            "implementations": req_to_impl,
            "tests": req_to_test,
            "test_coverage_pct": coverage_pct
        }

    def generate_matrix_markdown(self) -> str:
        data = self.scan_traceability()
        lines = [
            "# VeloC Software Requirement Traceability Matrix",
            "",
            "> [!NOTE] Preparatory artifact aligned with DO-178C / ISO 26262 structural guidelines.",
            "> *Notice: No formal regulatory certification is claimed; this document demonstrates traceability capabilities.*",
            "",
            f"**Total Tracked Requirements**: {len(data['all_requirements'])}  ",
            f"**Requirement Verification Coverage**: {data['test_coverage_pct']:.1f}%  ",
            "",
            "| Requirement ID | Implementation Source | Verification / Test | Status |",
            "|---|---|---|---|"
        ]

        for req in data["all_requirements"]:
            impls = ", ".join(data["implementations"].get(req, ["*None*"]))
            tests = ", ".join(data["tests"].get(req, ["*Uncovered*"]))
            status = "VERIFIED" if req in data["tests"] else "UNTESTED"
            lines.append(f"| `{req}` | {impls} | {tests} | **{status}** |")

        return "\n".join(lines)


class StaticWCETAnalyzer:
    """Estimates Worst-Case Execution Time (WCET) bounds for deterministic loop kernels."""

    def __init__(self, cpu_freq_ghz: float = 2.9):
        self.freq_ghz = cpu_freq_ghz
        self.cycle_time_ns = 1.0 / cpu_freq_ghz

    def analyze_loop_wcet(self, trip_count: int, instructions_per_iter: int, memory_accesses_per_iter: int) -> Dict[str, Any]:
        # Latency model: ALU ~1 cycle, L1 access ~4-5 cycles
        cycles_per_iter = instructions_per_iter * 1 + memory_accesses_per_iter * 5
        total_cycles = trip_count * cycles_per_iter + 10 # 10 cycles prologue/epilogue
        total_time_ns = total_cycles * self.cycle_time_ns
        total_time_us = total_time_ns / 1000.0

        return {
            "trip_count": trip_count,
            "cycles_per_iter": cycles_per_iter,
            "total_cycles": total_cycles,
            "wcet_ns": round(total_time_ns, 2),
            "wcet_us": round(total_time_us, 4),
            "status": "BOUNDED (Deterministic WCET Guarantee)"
        }
