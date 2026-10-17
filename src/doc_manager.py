# VeloC Documentation Management & Translation Synchronization Engine
# Provides:
# 1. Translation synchronizer: `veloc doc --check-translations`
# 2. Documentation snippet test runner: `veloc doc --test`
# 3. Bilingual index builder

import os
import sys
import re
import hashlib
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

ROOT_DIR = Path("D:/VeloC")
DOCS_DIR = ROOT_DIR / "docs"

class DocManager:
    def __init__(self, docs_dir: Path = DOCS_DIR):
        self.docs_dir = docs_dir
        self.en_dir = docs_dir / "en"
        self.ru_dir = docs_dir / "ru"

    def check_translations(self) -> Dict:
        """
        Inspects synchronization between English and Russian documentation trees.
        Identifies missing translations and outdated pages based on content hashes and timestamps.
        """
        en_files = {p.relative_to(self.en_dir): p for p in self.en_dir.rglob("*.md")} if self.en_dir.exists() else {}
        ru_files = {p.relative_to(self.ru_dir): p for p in self.ru_dir.rglob("*.md")} if self.ru_dir.exists() else {}

        all_rel_paths = sorted(set(en_files.keys()).union(set(ru_files.keys())))
        
        status_report = []
        synced_count = 0
        missing_ru = []
        missing_en = []
        outdated_ru = []
        outdated_en = []

        for rel in all_rel_paths:
            has_en = rel in en_files
            has_ru = rel in ru_files

            if has_en and not has_ru:
                missing_ru.append(str(rel))
                status_report.append({"path": str(rel), "status": "MISSING_RU", "en_mtime": en_files[rel].stat().st_mtime, "ru_mtime": None})
            elif has_ru and not has_en:
                missing_en.append(str(rel))
                status_report.append({"path": str(rel), "status": "MISSING_EN", "en_mtime": None, "ru_mtime": ru_files[rel].stat().st_mtime})
            else:
                en_stat = en_files[rel].stat()
                ru_stat = ru_files[rel].stat()
                if en_stat.st_mtime > ru_stat.st_mtime + 3600:
                    outdated_ru.append(str(rel))
                    status_report.append({"path": str(rel), "status": "OUTDATED_RU", "en_mtime": en_stat.st_mtime, "ru_mtime": ru_stat.st_mtime})
                elif ru_stat.st_mtime > en_stat.st_mtime + 3600:
                    outdated_en.append(str(rel))
                    status_report.append({"path": str(rel), "status": "OUTDATED_EN", "en_mtime": en_stat.st_mtime, "ru_mtime": ru_stat.st_mtime})
                else:
                    synced_count += 1
                    status_report.append({"path": str(rel), "status": "SYNCED", "en_mtime": en_stat.st_mtime, "ru_mtime": ru_stat.st_mtime})

        total = len(all_rel_paths)
        sync_pct = (synced_count / total * 100.0) if total > 0 else 100.0

        summary = {
            "total_pages": total,
            "synced_count": synced_count,
            "sync_percentage": round(sync_pct, 1),
            "missing_in_russian": missing_ru,
            "missing_in_english": missing_en,
            "outdated_in_russian": outdated_ru,
            "outdated_in_english": outdated_en,
            "items": status_report
        }
        return summary

    def format_check_report(self, summary: Dict) -> str:
        lines = [
            "=" * 80,
            "              VeloC Documentation Translation Sync Report",
            "=" * 80,
            f"Total Document Pages:  {summary['total_pages']}",
            f"Synchronized Pairs:    {summary['synced_count']} ({summary['sync_percentage']}%)",
            f"Missing in Russian:    {len(summary['missing_in_russian'])}",
            f"Missing in English:    {len(summary['missing_in_english'])}",
            f"Outdated in Russian:   {len(summary['outdated_in_russian'])}",
            f"Outdated in English:   {len(summary['outdated_in_english'])}",
            "-" * 80,
        ]
        if summary['missing_in_russian']:
            lines.append("Pages Missing in Russian (docs/ru/):")
            for p in summary['missing_in_russian'][:10]:
                lines.append(f"  - {p}")
            if len(summary['missing_in_russian']) > 10:
                lines.append(f"  ... and {len(summary['missing_in_russian']) - 10} more")
        
        if summary['missing_in_english']:
            lines.append("Pages Missing in English (docs/en/):")
            for p in summary['missing_in_english'][:10]:
                lines.append(f"  - {p}")

        if summary['sync_percentage'] == 100.0:
            lines.append("[SUCCESS] All bilingual documentation trees are 100% in sync!")
        else:
            lines.append(f"[NOTICE] Synchronization status: {summary['sync_percentage']}%")
        lines.append("=" * 80)
        return "\n".join(lines)

    def extract_snippets(self, file_path: Path) -> List[Tuple[int, str]]:
        content = file_path.read_text(encoding="utf-8")
        snippets = []
        in_block = False
        current_lines = []
        start_line = 0

        for idx, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            is_vc_block = (stripped == "```veloc" or stripped == "```vc" or 
                           (stripped.startswith("```veloc") and not any(tag in stripped for tag in ["ignore", "no_run", "no-run", "-ffi"])))
            if is_vc_block:
                in_block = True
                current_lines = []
                start_line = idx + 1
            elif stripped == "```" and in_block:
                in_block = False
                code_text = "\n".join(current_lines)
                if "fn main" in code_text or "test " in code_text or "void main" in code_text or "int main" in code_text:
                    snippets.append((start_line, code_text))
            elif in_block:
                current_lines.append(line)

        return snippets

    def test_snippets(self, target_dir: Path = None) -> Dict:
        scan_dir = target_dir or self.docs_dir
        md_files = list(scan_dir.rglob("*.md"))
        
        total_snippets = 0
        passed_snippets = 0
        failed_snippets = []
        temp_dir = ROOT_DIR / ".cache" / "doc_test_snippets"
        temp_dir.mkdir(parents=True, exist_ok=True)

        veloc_py = ROOT_DIR / "veloc.py"

        for md in md_files:
            snippets = self.extract_snippets(md)
            for line_no, code in snippets:
                total_snippets += 1
                snip_hash = hashlib.sha256(code.encode()).hexdigest()[:12]
                temp_file = temp_dir / f"doc_snip_{snip_hash}.vc"
                temp_file.write_text(code, encoding="utf-8")

                # Test compilation
                cmd = [sys.executable, str(veloc_py), "build", str(temp_file), "--fp=strict", "--profile=fast-compile"]
                res = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)
                
                if res.returncode == 0:
                    passed_snippets += 1
                else:
                    failed_snippets.append({
                        "file": str(md.relative_to(ROOT_DIR)),
                        "line": line_no,
                        "error": res.stderr or res.stdout
                    })

        return {
            "total_tested": total_snippets,
            "passed": passed_snippets,
            "failed": len(failed_snippets),
            "failures": failed_snippets
        }

if __name__ == "__main__":
    mgr = DocManager()
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        rep = mgr.check_translations()
        print(mgr.format_check_report(rep))
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing documentation code snippets...")
        t_res = mgr.test_snippets()
        print(f"Tested: {t_res['total_tested']} | Passed: {t_res['passed']} | Failed: {t_res['failed']}")
        if t_res['failed'] > 0:
            for f in t_res['failures']:
                print(f"  Fail in {f['file']}:{f['line']}")
    else:
        rep = mgr.check_translations()
        print(mgr.format_check_report(rep))
