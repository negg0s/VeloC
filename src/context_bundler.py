"""
VeloC Context Bundler (`veloc context`)
Gathers a compact, prioritized overview of the project (modules, public APIs,
dependencies, recent git diffs, failing tests) for feeding to LLMs within a strict token budget.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any


class ContextBundler:
    """Extracts prioritized project context under a configurable token limit."""

    def __init__(self, root_dir: str, max_tokens: int = 4000):
        self.root_dir = Path(root_dir)
        self.max_tokens = max_tokens
        self.char_limit = max_tokens * 4 # ~4 chars per token rule of thumb

    def gather_project_overview(self) -> str:
        packages = []
        pkgs_dir = self.root_dir / "packages"
        if pkgs_dir.exists():
            for p in pkgs_dir.iterdir():
                if p.is_dir():
                    packages.append(p.name)

        overview = [
            "# Project Context: VeloC Compiler & Runtime",
            f"- Root Directory: {self.root_dir}",
            f"- Architecture: x86_64 / i686 (AVX2 + FMA3, Clang 20)",
            f"- Active Vertical Packages: {', '.join(packages)}",
            ""
        ]
        return "\n".join(overview)

    def extract_public_api(self) -> str:
        lines = ["## Public Standard Library & Kernel Symbols"]
        headers = [
            self.root_dir / "include" / "veloc_stage6.h",
            self.root_dir / "include" / "veloc_security.h"
        ]
        for h in headers:
            if h.exists():
                lines.append(f"### {h.name}")
                content = h.read_text(encoding="utf-8", errors="ignore")
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("class ") or stripped.startswith("struct ") or (stripped.startswith("void ") and "(" in stripped):
                        if not stripped.startswith("//"):
                            lines.append(f"- `{stripped[:70]}`")
        lines.append("")
        return "\n".join(lines)

    def gather_git_summary(self) -> str:
        try:
            res = subprocess.run(["git", "log", "-n", "3", "--oneline"], cwd=str(self.root_dir), capture_output=True, text=True)
            commits = res.stdout.strip()
        except Exception:
            commits = "Git repository not available."

        return f"## Recent Git Commits\n```\n{commits}\n```\n"

    def bundle(self) -> str:
        parts = [
            self.gather_project_overview(),
            self.extract_public_api(),
            self.gather_git_summary()
        ]
        full_text = "\n".join(parts)
        if len(full_text) > self.char_limit:
            full_text = full_text[:self.char_limit] + "\n\n... [Context truncated to fit token budget] ...\n"
        return full_text
