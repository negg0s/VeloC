import sys
import hashlib
import subprocess
import glob
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

EXAMPLES_DIR = ROOT_DIR / "examples"
BUILD_DIR = ROOT_DIR / "build"
CACHE_DIR = ROOT_DIR / ".cache"

def sha256_file(filepath: Path) -> str:
    return hashlib.sha256(filepath.read_bytes()).hexdigest()

def test_deterministic_builds():
    print("==================================================")
    print("       VeloC Deterministic Build Test Suite       ")
    print("==================================================")
    
    examples = sorted(glob.glob(str(EXAMPLES_DIR / "*.vc")))
    passed = 0
    failed = 0

    for ex in examples:
        p = Path(ex)
        stem = p.stem
        cpp_file = CACHE_DIR / f"{stem}.cpp"
        exe_file = BUILD_DIR / f"{stem}.exe"

        # Pass 1: Fresh build
        if cpp_file.exists(): cpp_file.unlink()
        if exe_file.exists(): exe_file.unlink()
        subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "clean"], capture_output=True)
        res1 = subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "build", str(p)], capture_output=True, text=True)
        if res1.returncode != 0:
            print(f"  [FAIL] {p.name:<30} Pass 1 failed to build!")
            failed += 1
            continue
        
        cpp_hash1 = sha256_file(cpp_file)
        exe_hash1 = sha256_file(exe_file)

        # Pass 2: Rebuild from scratch
        if cpp_file.exists(): cpp_file.unlink()
        if exe_file.exists(): exe_file.unlink()
        subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "clean"], capture_output=True)
        res2 = subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "build", str(p)], capture_output=True, text=True)
        if res2.returncode != 0:
            print(f"  [FAIL] {p.name:<30} Pass 2 failed to build!")
            failed += 1
            continue

        cpp_hash2 = sha256_file(cpp_file)
        exe_hash2 = sha256_file(exe_file)

        if cpp_hash1 == cpp_hash2 and exe_hash1 == exe_hash2:
            print(f"  [PASS] {p.name:<30} 100% bit-exact reproducible (SHA256 match)")
            passed += 1
        else:
            print(f"  [FAIL] {p.name:<30} Non-deterministic build!\n         CPP: {cpp_hash1 == cpp_hash2}\n         EXE: {exe_hash1 == exe_hash2}")
            failed += 1

    print("==================================================")
    print(f"Determinism Results: {passed} passed, {failed} failed")
    print("==================================================")
    return failed == 0

if __name__ == "__main__":
    success = test_deterministic_builds()
    sys.exit(0 if success else 1)
