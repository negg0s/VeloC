"""
VeloC Floating-Point Policy, Precision Contracts, and FP-Linter Engine
Implements IEEE-754 strict mode by default, relaxed/fast/reproducible modes,
function-level attributes (#[fp(...)], #[assoc_reduce], #[accuracy(...)]),
and static diagnostics against unsafe floating-point practices.
"""

import re
from typing import List, Dict, Any, Tuple
from pathlib import Path

class FloatingPointPolicy:
    """Manages compiler flags and code transformations for floating-point semantics."""

    VALID_MODES = ["strict", "relaxed", "fast", "reproducible"]

    def __init__(self, mode: str = "strict", enable_ftz: bool = False):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Unknown floating-point mode '{mode}'. Allowed: {self.VALID_MODES}")
        self.mode = mode
        self.enable_ftz = enable_ftz

    def get_compiler_flags(self) -> List[str]:
        flags = []
        if self.mode == "strict":
            # IEEE-754 Strict conformance by default!
            flags.extend([
                "-fno-fast-math",
                "-frounding-math",
                "-fno-associative-math",
                "-fno-reciprocal-math",
                "-fdenormal-fp-math=ieee",
                "-ffp-contract=off"
            ])
        elif self.mode == "relaxed":
            # Preserves NaNs/Infs/signed zeros, but allows FMA contraction
            flags.extend([
                "-fno-fast-math",
                "-frounding-math",
                "-fdenormal-fp-math=ieee",
                "-ffp-contract=fast"
            ])
        elif self.mode == "fast":
            # Explicit opt-in fast math
            flags.extend([
                "-ffast-math"
            ])
        elif self.mode == "reproducible":
            # Deterministic results across any threads / vector architectures
            flags.extend([
                "-fno-fast-math",
                "-frounding-math",
                "-ffp-contract=off",
                "-fno-associative-math"
            ])

        if self.enable_ftz:
            flags.append("-fdenormal-fp-math=preserve-sign")

        return flags

class FloatingPointLinter:
    """Scans VeloC source code for dangerous or inaccurate floating-point patterns."""

    def __init__(self, source_code: str, filename: str = "<source>", global_mode: str = "strict"):
        self.source = source_code
        self.filename = filename
        self.global_mode = global_mode

    def lint(self) -> List[Dict[str, Any]]:
        findings = []
        lines = self.source.splitlines()

        is_fast_scope = (self.global_mode == "fast")
        float_vars = set()

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*"):
                continue

            # Scope tracking
            if "#[fp(fast)]" in stripped:
                is_fast_scope = True
            elif "#[fp(strict)]" in stripped or "#[fp(reproducible)]" in stripped:
                is_fast_scope = False

            # Track float parameters and variables
            for p_match in re.findall(r'([a-zA-Z0-9_]+)\s*:\s*(?:f32|f64|float|double)', stripped):
                float_vars.add(p_match)
            for v_match in re.findall(r'(?:let|var)\s+([a-zA-Z0-9_]+)', stripped):
                if any(x in stripped for x in ["f32", "f64", "float", "."]):
                    float_vars.add(v_match)

            # Rule FP-001: Direct float equality comparison (x == y or x != y)
            float_eq_match = re.search(r'([a-zA-Z0-9_]+)\s*(==|!=)\s*([0-9]+\.[0-9]+f?|[a-zA-Z0-9_]+)', stripped)
            if float_eq_match and ("float" in stripped or "f32" in stripped or "f64" in stripped or "." in float_eq_match.group(3) or float_eq_match.group(1) in float_vars or float_eq_match.group(3) in float_vars):
                op = float_eq_match.group(2)
                findings.append({
                    "rule": "FP-001",
                    "severity": "warning",
                    "line": idx,
                    "file": self.filename,
                    "message": f"Exact floating-point comparison with '{op}'. Use approx_eq(a, b, ulp) or abs(a - b) <= epsilon to prevent precision bugs.",
                    "snippet": stripped
                })

            # Rule FP-002: Incompatible isnan/isinf check under fast-math
            if is_fast_scope:
                if re.search(r'\b(isnan|isinf|std::isnan|std::isinf)\b', stripped) or re.search(r'([a-zA-Z0-9_]+)\s*!=\s*\1', stripped):
                    findings.append({
                        "rule": "FP-002",
                        "severity": "error",
                        "line": idx,
                        "file": self.filename,
                        "message": "NaN/Inf check is undefined under fast-math mode (-ffast-math assumes no NaNs exist and optimizes checks away). Use #[fp(strict)].",
                        "snippet": stripped
                    })

            # Rule FP-003: Unchecked division by float expression
            div_match = re.search(r'/\s*([a-zA-Z0-9_]+)\b', stripped)
            if div_match and not any(kw in stripped for kw in ["if", "assert", "guard", "sizeof"]):
                denom = div_match.group(1)
                if denom in float_vars or any(k in stripped for k in ["f32", "f64", "float"]):
                    findings.append({
                        "rule": "FP-003",
                        "severity": "info",
                        "line": idx,
                        "file": self.filename,
                        "message": f"Potential division by unchecked float '{denom}'. Consider guarding against division-by-zero or subnormal underflow.",
                        "snippet": stripped
                    })

        return findings

class AttributeTransformer:
    """Transforms VeloC FP attributes into C++ pragmas and function decorations."""

    @staticmethod
    def transform_code(source: str) -> str:
        out_lines = []
        lines = source.splitlines()

        for line in lines:
            stripped = line.strip()

            if stripped == "#[fp(strict)]":
                out_lines.append("#pragma clang fp contract(off)")
                out_lines.append("#pragma clang fp reassociate(off)")
                continue
            elif stripped == "#[fp(relaxed)]":
                out_lines.append("#pragma clang fp contract(fast)")
                out_lines.append("#pragma clang fp reassociate(off)")
                continue
            elif stripped == "#[fp(fast)]" or stripped == "#[assoc_reduce]":
                out_lines.append("#pragma clang fp contract(fast)")
                out_lines.append("#pragma clang fp reassociate(on)")
                continue
            elif stripped == "#[reproducible]":
                out_lines.append("#pragma clang fp contract(off)")
                out_lines.append("#pragma clang fp reassociate(off)")
                continue
            elif stripped.startswith("#[accuracy(") or stripped == "#[ftz]":
                # Statically preserved metadata comment in generated C++
                out_lines.append(f"// {stripped}")
                continue

            out_lines.append(line)

        return "\n".join(out_lines)
