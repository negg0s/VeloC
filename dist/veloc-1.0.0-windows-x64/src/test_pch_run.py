import subprocess
import time
from pathlib import Path
from pch_manager import PchManager, LLD_PATH

pm = PchManager()
pch = pm.ensure_pch('veloc.h', '-O3', profile="max-perf", verbose=True)

src = Path('.cache/test_pch_include.cpp')
src.write_text("""#include <veloc.h>
int main() {
    veloc::println("PCH static execution verified!");
    return 0;
}
""", encoding="utf-8")

flags = pm.get_pch_flags("-O3", "max-perf")
cmd = [
    'C:/Program Files/Windhawk/Compiler/bin/clang++.exe',
    *flags,
    '-include-pch', str(pch),
    '-fuse-ld=lld',
    str(src),
    '-o', '.cache/test_pch_include.exe'
]

t0 = time.perf_counter()
res = subprocess.run(cmd, capture_output=True, text=True)
dur = (time.perf_counter() - t0) * 1000

print(f"Compilation time: {dur:.1f} ms, RC: {res.returncode}")
if res.stderr:
    print("Stderr:", res.stderr[:300])

# Run binary to verify
run_res = subprocess.run(['.cache/test_pch_include.exe'], capture_output=True, text=True)
print("Binary Output:", run_res.stdout.strip(), "Code:", run_res.returncode)
