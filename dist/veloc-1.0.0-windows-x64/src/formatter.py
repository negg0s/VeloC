"""
VeloC Code Formatter (veloc fmt)
Provides deterministic, idempotent source code formatting with configuration support.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

class FormatterConfig:
    def __init__(self, indent_size: int = 4, max_width: int = 100, use_tabs: bool = False):
        self.indent_size = indent_size
        self.max_width = max_width
        self.use_tabs = use_tabs

    @classmethod
    def load_from_toml(cls, root: Path = Path(".")) -> "FormatterConfig":
        config_file = root / "veloc.toml"
        if config_file.exists():
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib
            try:
                data = tomllib.loads(config_file.read_text(encoding="utf-8"))
                fmt_sec = data.get("fmt", {})
                return cls(
                    indent_size=fmt_sec.get("indent", 4),
                    max_width=fmt_sec.get("max_width", 100),
                    use_tabs=fmt_sec.get("use_tabs", False)
                )
            except Exception:
                pass
        return cls()


class VeloCFormatter:
    def __init__(self, config: Optional[FormatterConfig] = None):
        self.config = config or FormatterConfig()

    def format_source(self, code: str) -> str:
        """
        Formats VeloC source code idempotently.
        Guarantees format(format(code)) == format(code).
        """
        raw_lines = code.replace("\r\n", "\n").split("\n")
        formatted_lines: List[str] = []
        indent_level = 0
        indent_str = "\t" if self.config.use_tabs else (" " * self.config.indent_size)
        in_multiline_comment = False

        for raw_line in raw_lines:
            line = raw_line.strip()

            # Handle empty lines
            if not line:
                if formatted_lines and formatted_lines[-1] != "":
                    formatted_lines.append("")
                continue

            # Multiline comment handling
            if in_multiline_comment:
                formatted_lines.append((indent_str * indent_level) + line)
                if "*/" in line:
                    in_multiline_comment = False
                continue

            if line.startswith("/*"):
                formatted_lines.append((indent_str * indent_level) + line)
                if "*/" not in line:
                    in_multiline_comment = True
                continue

            # Adjust indent for closing braces
            close_count = line.count("}") - line.count("{")
            leading_close = line.startswith("}") or line.startswith(")")

            if leading_close:
                indent_level = max(0, indent_level - 1)

            # Clean binary operators spacing
            cleaned = self._normalize_operators(line)

            # Apply indentation
            formatted_lines.append((indent_str * indent_level) + cleaned)

            # Compute indent delta for next lines
            if not leading_close and close_count > 0:
                indent_level = max(0, indent_level - close_count)
            elif line.endswith("{") or line.endswith("("):
                indent_level += 1
            else:
                net_open = line.count("{") - line.count("}")
                if net_open > 0 and not line.endswith("{"):
                    indent_level += net_open

        # Ensure trailing newline
        result = "\n".join(formatted_lines).strip() + "\n"
        return result

    def _normalize_operators(self, line: str) -> str:
        # Don't modify string literals or full-line comments
        if line.startswith("//"):
            return line

        # Normalize spaces around assignments and common binary operators
        # Avoid breaking -> and :: and >= and <= and == and !=
        tokens = []
        # Basic normalization for common punctuation
        line = re.sub(r",\s*", ", ", line)
        line = re.sub(r";\s*", ";", line)
        line = re.sub(r":\s*([a-zA-Z_])", r": \1", line)
        line = re.sub(r"\s*->\s*", " -> ", line)
        line = re.sub(r"\s*=>\s*", " => ", line)
        line = re.sub(r"([a-zA-Z0-9_])\s*=\s*([a-zA-Z0-9_\(\{\[\"])", r"\1 = \2", line)
        line = re.sub(r"([a-zA-Z0-9_])\s*\+\s*([a-zA-Z0-9_\"])", r"\1 + \2", line)
        line = re.sub(r"([a-zA-Z0-9_])\s*-\s*([a-zA-Z0-9_])", r"\1 - \2", line)
        line = re.sub(r"([a-zA-Z0-9_])\s*\*\s*([a-zA-Z0-9_])", r"\1 * \2", line)
        line = re.sub(r"([a-zA-Z0-9_])\s*/\s*([a-zA-Z0-9_])", r"\1 / \2", line)
        return line


def format_file(file_path: Path, check_only: bool = False, config: Optional[FormatterConfig] = None) -> bool:
    """
    Formats a single file.
    If check_only is True, returns True if file is already correctly formatted.
    If check_only is False, formats in-place and returns True.
    """
    orig = file_path.read_text(encoding="utf-8")
    formatter = VeloCFormatter(config)
    formatted = formatter.format_source(orig)

    if check_only:
        return orig == formatted

    if orig != formatted:
        file_path.write_text(formatted, encoding="utf-8")
    return True


def format_directory(root_dir: Path, check_only: bool = False) -> Tuple[int, int]:
    """Formats all .vc files in root_dir."""
    config = FormatterConfig.load_from_toml(root_dir)
    total = 0
    mismatches = 0
    for vc_file in root_dir.rglob("*.vc"):
        total += 1
        ok = format_file(vc_file, check_only=check_only, config=config)
        if not ok:
            mismatches += 1
            if check_only:
                print(f"[fmt:MISMATCH] {vc_file}")
    return total, mismatches
