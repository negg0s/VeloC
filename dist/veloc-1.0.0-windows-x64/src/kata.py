# VeloC Katas and Problem Set Engine (150 Tasks)
# Provides `veloc kata` CLI for training, testing, and tracking algorithmic mastery.

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

ROOT_DIR = Path("D:/VeloC")
CATALOG_FILE = ROOT_DIR / "docs" / "learn" / "katas" / "catalog.json"
PROGRESS_FILE = ROOT_DIR / ".veloc" / "kata_progress.json"

class KataManager:
    def __init__(self, root_dir: Path = ROOT_DIR):
        self.root_dir = root_dir
        self.catalog = self._load_catalog()
        self.progress_file = PROGRESS_FILE

    def _load_catalog(self) -> List[Dict]:
        if CATALOG_FILE.exists():
            return json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        return []

    def load_progress(self) -> Dict:
        if self.progress_file.exists():
            try:
                return json.loads(self.progress_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"solved": []}

    def save_progress(self, prog: Dict):
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.progress_file.write_text(json.dumps(prog, indent=2), encoding="utf-8")

    def get_kata(self, kata_id: int) -> Optional[Dict]:
        for k in self.catalog:
            if k["id"] == kata_id:
                return k
        return None

    def list_katas(self, difficulty: str = None) -> List[Dict]:
        prog = self.load_progress()
        solved_ids = set(prog.get("solved", []))
        results = []
        for k in self.catalog:
            if difficulty and k["difficulty"].lower() != difficulty.lower():
                continue
            is_solved = k["id"] in solved_ids
            results.append({
                "id": k["id"],
                "title": k["title"],
                "difficulty": k["difficulty"],
                "solved": is_solved
            })
        return results

    def run_kata_test(self, kata_id: int, user_code: str = None) -> Dict:
        kata = self.get_kata(kata_id)
        if not kata:
            return {"status": "error", "message": f"Kata #{kata_id} not found."}

        # If user code not provided, use reference solution
        code_to_test = user_code
        if not code_to_test:
            code_to_test = f"{kata['signature']} {{\n    {kata['body']}\n}}\n"

        test_harness = f"""#include "veloc.h"

{code_to_test}

int main() {{
    bool ok = {kata['test_assert']};
    if (ok) {{
        printf("[KATA_PASS] Kata #{kata['id']} assertion passed.\\n");
        return 0;
    }} else {{
        printf("[KATA_FAIL] Assertion failed: {kata['test_assert']}\\n");
        return 1;
    }}
}}
"""
        temp_dir = self.root_dir / ".cache" / "kata_runs"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file = temp_dir / f"run_kata_{kata_id:03d}.vc"
        temp_file.write_text(test_harness, encoding="utf-8")

        veloc_py = self.root_dir / "veloc.py"
        cmd = [sys.executable, str(veloc_py), "run", str(temp_file)]
        res = subprocess.run(cmd, cwd=str(self.root_dir), capture_output=True, text=True)

        passed = (res.returncode == 0) and ("[KATA_PASS]" in res.stdout)
        if passed:
            prog = self.load_progress()
            if kata_id not in prog["solved"]:
                prog["solved"].append(kata_id)
                prog["solved"].sort()
                self.save_progress(prog)
            return {
                "status": "passed",
                "kata_id": kata_id,
                "title": kata["title"],
                "message": f"[SUCCESS] Kata #{kata_id} ('{kata['title']}') passed all test cases!"
            }
        else:
            return {
                "status": "failed",
                "kata_id": kata_id,
                "title": kata["title"],
                "message": f"[FAILED] Kata #{kata_id} failed assertion.",
                "stdout": res.stdout,
                "stderr": res.stderr
            }

    def get_stats(self) -> Dict:
        prog = self.load_progress()
        solved_ids = set(prog.get("solved", []))
        total = len(self.catalog)
        solved = len(solved_ids)

        diff_counts = {"easy": 0, "medium": 0, "hard": 0, "expert": 0}
        diff_solved = {"easy": 0, "medium": 0, "hard": 0, "expert": 0}

        for k in self.catalog:
            d = k["difficulty"].lower()
            if d in diff_counts:
                diff_counts[d] += 1
                if k["id"] in solved_ids:
                    diff_solved[d] += 1

        return {
            "total_katas": total,
            "total_solved": solved,
            "overall_pct": round(solved / total * 100.0, 1) if total > 0 else 0.0,
            "by_difficulty": {
                d: {"solved": diff_solved[d], "total": diff_counts[d], "pct": round(diff_solved[d] / diff_counts[d] * 100.0, 1) if diff_counts[d] > 0 else 0.0}
                for d in diff_counts
            }
        }

    def test_all_reference_solutions(self) -> Dict:
        """Batch-verifies all 150 Katas reference solutions."""
        passed = 0
        failed = 0
        failures = []

        for k in self.catalog:
            kid = k["id"]
            res = self.run_kata_test(kid)
            if res["status"] == "passed":
                passed += 1
            else:
                failed += 1
                failures.append({"id": kid, "title": k["title"], "error": res.get("stdout") or res.get("stderr")})

        return {
            "total": len(self.catalog),
            "passed": passed,
            "failed": failed,
            "failures": failures
        }

if __name__ == "__main__":
    km = KataManager()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            diff = sys.argv[2] if len(sys.argv) > 2 else None
            katas = km.list_katas(diff)
            print(f"Total Katas ({diff or 'all'}): {len(katas)}")
            for k in katas[:25]:
                mark = "[X]" if k["solved"] else "[ ]"
                print(f"  {mark} #{k['id']:03d} [{k['difficulty'].upper():<6}] {k['title']}")
            if len(katas) > 25:
                print(f"  ... and {len(katas) - 25} more")
        elif cmd == "stats":
            st = km.get_stats()
            print("=" * 60)
            print("                 VeloC Katas Mastery Stats                 ")
            print("=" * 60)
            print(f"Total Solved: {st['total_solved']} / {st['total_katas']} ({st['overall_pct']}%)")
            for d, data in st["by_difficulty"].items():
                print(f"  - {d.capitalize():<8}: {data['solved']:>3} / {data['total']:>3} ({data['pct']}%)")
            print("=" * 60)
        elif cmd == "test":
            kid = int(sys.argv[2])
            res = km.run_kata_test(kid)
            print(res["message"])
        elif cmd == "test-all":
            print(f"Running automated verification across all {len(km.catalog)} Katas...")
            res = km.test_all_reference_solutions()
            print(f"Results: {res['passed']} / {res['total']} passed ({res['failed']} failed)")
            if res['failed'] > 0:
                for f in res['failures'][:5]:
                    print(f"  Kata #{f['id']} failed: {f['title']}")
    else:
        print("Usage: python src/kata.py {list|stats|test <id>|test-all}")
