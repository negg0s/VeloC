"""
VeloC Issue Triage & Good First Issues Generator
Scans repository for TODOs, FIXMEs, and beginner-friendly improvement opportunities.
"""

import os
import re

CURATED_GOOD_FIRST_ISSUES = [
    {
        "id": "GFI-001",
        "title": "Add stdlib documentation examples for `std::vector` and `std::string` wrappers",
        "difficulty": "Easy",
        "tags": ["documentation", "stdlib", "good-first-issue"],
        "file": "include/veloc.h",
        "description": "Add triple-slash `///` doc comments with executable usage examples for standard utility helpers."
    },
    {
        "id": "GFI-002",
        "title": "Implement compound bitwise assignment operators in lexer/parser",
        "difficulty": "Medium",
        "tags": ["compiler", "lexer", "parser"],
        "file": "src/lexer.py",
        "description": "Add tokenization and AST mapping for `^=`, `&=`, `|=`, `<<=`, `>>=` to avoid manual expansion."
    },
    {
        "id": "GFI-003",
        "title": "Coalesce consecutive `#line` pragmas between `else` and `if`",
        "difficulty": "Medium",
        "tags": ["compiler", "codegen", "source-maps"],
        "file": "src/transpiler.py",
        "description": "Ensure `else if` tokens do not have an intermediate `#line` pragma injected by the source map generator."
    },
    {
        "id": "GFI-004",
        "title": "Add colorized console output to `veloc test` summary",
        "difficulty": "Easy",
        "tags": ["cli", "ux", "good-first-issue"],
        "file": "src/test_runner.py",
        "description": "Enhance test summary table with ANSI green/red status tags when interactive TTY is detected."
    },
    {
        "id": "GFI-005",
        "title": "Implement ARM NEON vector fallback in `include/veloc.h`",
        "difficulty": "Medium",
        "tags": ["simd", "arm", "portability"],
        "file": "include/veloc.h",
        "description": "Provide `vaddq_f32` and `vmulq_f32` implementations when compiling on ARM64 platforms."
    }
]

def scan_todos():
    todos = []
    for root, _, files in os.walk("."):
        if any(ignored in root for ignored in [".git", ".cache", "build", "__pycache__"]):
            continue
        for file in files:
            if file.endswith((".py", ".vc", ".h", ".cpp", ".md")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for idx, line in enumerate(f, 1):
                            m = re.search(r"(TODO|FIXME|NOTE|HACK):\s*(.*)", line, re.IGNORECASE)
                            if m:
                                todos.append({
                                    "kind": m.group(1).upper(),
                                    "file": path,
                                    "line": idx,
                                    "text": m.group(2).strip()
                                })
                except Exception:
                    pass
    return todos

def run_triage():
    print("=" * 80)
    print("                 VeloC Contributor Triage & Good First Issues                   ")
    print("=" * 80)
    print("\n[Curated Good First Issues for New Contributors]")
    for issue in CURATED_GOOD_FIRST_ISSUES:
        print(f"  * [{issue['id']}] {issue['title']} ({issue['difficulty']})")
        print(f"      Location: {issue['file']}")
        print(f"      Tags: {', '.join(issue['tags'])}")
        print(f"      Detail: {issue['description']}\n")

    todos = scan_todos()
    print(f"[Scanned Codebase Indicators]: Found {len(todos)} inline notes/todos")
    for t in todos[:5]:
        print(f"  - {t['kind']} in {t['file']}:{t['line']} -> {t['text']}")
    if len(todos) > 5:
        print(f"  ... and {len(todos) - 5} more items.")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    run_triage()
