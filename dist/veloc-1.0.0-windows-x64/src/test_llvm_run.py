import time
from pathlib import Path
from llvm_backend import LlvmBackend

backend = LlvmBackend()
source = """
fn main() -> i32 {
    let a: i32 = 42;
    printf("Direct LLVM IR Result: %d\\n", a);
    return 0;
}
"""

ll_code = backend.generate_ll(None, source)
ll_file = Path(".cache/test_direct.ll")
exe_file = Path(".cache/test_direct.exe")
ll_file.write_text(ll_code, encoding="utf-8")

print("Generated LLVM IR:")
print("-" * 50)
print(ll_code)
print("-" * 50)

dur, rc, err = backend.compile_ll(ll_file, exe_file, opt_level="-O3")
print(f"Direct LLVM IR compile time: {dur:.1f} ms (rc={rc})")
if err:
    print("Stderr:", err[:300])

# Execute binary
import subprocess
res = subprocess.run([str(exe_file)], capture_output=True, text=True)
print("Binary execution:", res.stdout.strip(), "Code:", res.returncode)
