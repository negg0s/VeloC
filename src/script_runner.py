# VeloC Script Runner Engine
# Provides instant execution for small .vc scripts with shebang support:
# #!/usr/bin/env veloc script

import os
import sys
import time
import subprocess
import hashlib
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
CACHE_DIR = ROOT_DIR / ".cache" / "scripts"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class ScriptRunner:
    def __init__(self, root_dir: Path = ROOT_DIR):
        self.root_dir = root_dir
        self.veloc_py = root_dir / "veloc.py"

    def run_script(self, script_path: Path, script_args: list = None) -> int:
        if not script_path.exists():
            print(f"[Error] Script file not found: {script_path}")
            return 1

        t0 = time.perf_counter()
        raw_text = script_path.read_text(encoding="utf-8")
        lines = raw_text.splitlines()

        # Handle Shebang #!
        has_shebang = False
        if lines and lines[0].startswith("#!"):
            has_shebang = True
            lines = lines[1:]

        cleaned_code = "\n".join(lines)

        # Hash script content to verify instant cache hit
        script_hash = hashlib.sha256(cleaned_code.encode("utf-8")).hexdigest()[:16]
        cached_vc = CACHE_DIR / f"script_{script_hash}.vc"
        cached_exe = CACHE_DIR / f"script_{script_hash}.exe"

        # Check if already compiled and executable exists
        is_warm = cached_exe.exists() and cached_vc.exists() and cached_vc.read_text(encoding="utf-8") == cleaned_code

        if not is_warm:
            cached_vc.write_text(cleaned_code, encoding="utf-8")
            # Compile with PCH for sub-second build
            build_cmd = [
                sys.executable, str(self.veloc_py), "build", str(cached_vc),
                "-o", str(cached_exe), "--profile=fast-compile", "--fp=strict"
            ]
            res = subprocess.run(build_cmd, cwd=str(self.root_dir), capture_output=True, text=True)
            if res.returncode != 0:
                print(f"[VeloC Script Compilation Error]:\n{res.stderr or res.stdout}")
                return res.returncode

        t_compile = (time.perf_counter() - t0) * 1000.0

        # Execute script binary
        t_exec_start = time.perf_counter()
        run_cmd = [str(cached_exe)] + (script_args or [])
        proc = subprocess.run(run_cmd, cwd=str(self.root_dir))
        t_exec = (time.perf_counter() - t_exec_start) * 1000.0

        t_total = (time.perf_counter() - t0) * 1000.0
        mode = "Warm Cache" if is_warm else "Cold Compile"
        # Print subtle timing banner on debug or script completion
        if os.environ.get("VELOC_SCRIPT_TIMING", "0") == "1":
            print(f"\n[Script Metrics ({mode})]: Build/Cache: {t_compile:.1f}ms, Run: {t_exec:.1f}ms, Total: {t_total:.1f}ms")

        return proc.returncode

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: veloc script <file.vc> [args...]")
        sys.exit(1)

    runner = ScriptRunner()
    ret = runner.run_script(Path(sys.argv[1]), sys.argv[2:])
    sys.exit(ret)
