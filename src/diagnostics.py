# VeloC Diagnostics and Error Reporting Engine
# Provides Rust/Elm-grade error formatting with exact source line underlining,
# suggestions (Levenshtein distance), and error codes (E0001..)

import enum
from typing import List, Optional

class DiagnosticCode(enum.Enum):
    E0001 = "E0001"
    E0002 = "E0002"
    E0003 = "E0003"
    E0004 = "E0004"
    E0005 = "E0005"
    E0006 = "E0006"
    E0007 = "E0007"
    E0008 = "E0008"
    E0009 = "E0009"
    E0010 = "E0010"

ERROR_CATALOG = {
    "E0001": "Syntax Error: Unexpected token encountered during parsing.",
    "E0002": "Type Error: Incompatible types in assignment or expression.",
    "E0003": "Undeclared Identifier: Symbol could not be resolved in the current scope.",
    "E0004": "Unterminated String or Character Literal.",
    "E0005": "Duplicate Symbol: Identifier has already been declared in this scope.",
    "E0006": "Unwrap / Assertion Panic: Value was None or Err when unwrapped.",
    "E0007": "Invalid Cast: Types cannot be safely converted via `as`.",
    "E0008": "Invalid Module or Import Declaration.",
    "E0009": "Non-exhaustive Match: Not all cases or wildcard `_` are covered.",
    "E0010": "Missing Return: Function must return a value along all control flow paths.",
}

def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev[j + 1] + 1
            deletions = curr[j] + 1
            substitutions = prev[j] + (c1 != c2)
            curr.append(min(insertions, deletions, substitutions))
        prev = curr
    return prev[-1]

def find_closest_match(name: str, candidates: List[str], max_dist: int = 3) -> Optional[str]:
    best_candidate = None
    best_dist = max_dist + 1
    for c in candidates:
        d = levenshtein_distance(name, c)
        if d < best_dist:
            best_dist = d
            best_candidate = c
    return best_candidate

class Diagnostic:
    def __init__(self, code: str, message: str, file: str, line: int, col: int, 
                 span_len: int = 1, suggestion: Optional[str] = None):
        self.code = code
        self.message = message
        self.file = file
        self.line = line
        self.col = col
        self.span_len = max(1, span_len)
        self.suggestion = suggestion

    def format_with_source(self, source_code: str) -> str:
        lines = source_code.splitlines()
        source_line = ""
        if 1 <= self.line <= len(lines):
            source_line = lines[self.line - 1]

        gutter = f" {self.line} | "
        indent = " " * len(gutter)
        col_offset = " " * (self.col - 1)
        underline = "^" * self.span_len

        header = f"\033[1;31merror[{self.code}]\033[0m\033[1m: {self.message}\033[0m"
        loc = f"  --> {self.file}:{self.line}:{self.col}"
        
        result = [
            header,
            loc,
            f"{indent}|",
            f"{gutter}{source_line}",
            f"{indent}|{col_offset}\033[1;31m{underline}\033[0m",
        ]
        if self.suggestion:
            result.append(f"{indent}\033[1;36m= help: {self.suggestion}\033[0m")
        result.append(f"{indent}|")
        return "\n".join(result)

def explain_error_code(code: str) -> str:
    explanation = ERROR_CATALOG.get(code.upper())
    if explanation:
        return f"\033[1;33m[{code.upper()}]\033[0m: {explanation}"
    return f"Unknown error code: {code}"

class DiagnosticReporter:
    def __init__(self, source_code: str = "", filename: str = "<stdin>"):
        self.source_code = source_code
        self.filename = filename
        self.diagnostics: List[Diagnostic] = []

    def error(self, code: DiagnosticCode, message: str, line: int, col: int, span_len: int = 1, suggestion: Optional[str] = None):
        diag = Diagnostic(code.value, message, self.filename, line, col, span_len, suggestion)
        self.diagnostics.append(diag)
        return diag

    def render(self) -> str:
        return "\n\n".join(d.format_with_source(self.source_code) for d in self.diagnostics)

    def print_all(self):
        if self.diagnostics:
            print(self.render())

