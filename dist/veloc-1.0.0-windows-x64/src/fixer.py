"""
VeloC Automated Compiler Suggestion Fixer (veloc fix)
Applies safe compiler diagnostic suggestions:
- Stripping unused imports
- Demoting unused mutable bindings (let mut -> let)
- Modernizing deprecated syntax patterns
"""

import re
import difflib
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

class VeloCFixer:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def fix_source(self, code: str, filepath: str = "<memory>") -> Tuple[str, List[str]]:
        lines = code.splitlines()
        fixes_applied: List[str] = []
        new_lines: List[str] = []

        # 1. Unused mut detection
        mut_pattern = re.compile(r"(\s*let\s+)mut\s+([a-zA-Z_][a-zA-Z0-9_]*)(.*)")

        # 2. Unused import detection
        import_pattern = re.compile(r"^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;")

        for line_idx, line in enumerate(lines):
            # Check unused mut
            m_mut = mut_pattern.match(line)
            if m_mut:
                prefix, var_name, rest = m_mut.groups()
                # Check if var_name is ever reassigned in remaining lines: var_name = ...
                reassign_pattern = re.compile(rf"\b{re.escape(var_name)}\s*(\+|-|\*|/)?=")
                is_reassigned = any(reassign_pattern.search(l) for l in lines[line_idx+1:])
                if not is_reassigned:
                    line = f"{prefix}{var_name}{rest}"
                    fixes_applied.append(f"Demoted unused 'mut' binding '{var_name}' at line {line_idx+1}")

            # Check unused import
            m_imp = import_pattern.match(line)
            if m_imp:
                mod_name = m_imp.group(1)
                # Check if mod_name is used anywhere else in the file
                is_used = False
                for other_idx, other_line in enumerate(lines):
                    if other_idx == line_idx:
                        continue
                    if re.search(rf"\b{re.escape(mod_name)}\b", other_line):
                        is_used = True
                        break
                if not is_used:
                    fixes_applied.append(f"Removed unused import '{mod_name}' at line {line_idx+1}")
                    continue # Skip this import line

            new_lines.append(line)

        fixed_code = "\n".join(new_lines)
        if code.endswith("\n"):
            fixed_code += "\n"
        return fixed_code, fixes_applied

    def fix_file(self, file_path: Path) -> Tuple[bool, List[str], str]:
        """
        Returns (modified, fixes_applied, diff_text).
        If dry_run is True, the file is not changed on disk.
        """
        original = file_path.read_text(encoding="utf-8")
        fixed, fixes = self.fix_source(original, str(file_path))

        if original == fixed:
            return False, [], ""

        diff = "".join(difflib.unified_diff(
            original.splitlines(keepends=True),
            fixed.splitlines(keepends=True),
            fromfile=str(file_path),
            tofile=str(file_path) + " (fixed)"
        ))

        if not self.dry_run:
            file_path.write_text(fixed, encoding="utf-8")

        return True, fixes, diff


def run_fix(root: Path, dry_run: bool = False) -> Dict[str, Any]:
    fixer = VeloCFixer(dry_run=dry_run)
    total_files = 0
    modified_files = 0
    all_fixes: List[str] = []
    diffs: List[str] = []

    for vc_file in root.rglob("*.vc"):
        total_files += 1
        changed, fixes, diff = fixer.fix_file(vc_file)
        if changed:
            modified_files += 1
            all_fixes.extend(fixes)
            if diff:
                diffs.append(diff)

    return {
        "total_files": total_files,
        "modified_files": modified_files,
        "fixes": all_fixes,
        "diffs": diffs
    }
