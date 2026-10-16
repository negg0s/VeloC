import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from from_cpp import transpile_cpp_to_veloc

# Suite of 50 concise C++ test cases testing functions, loops, STL, and arithmetic
CPP_TEST_CASES = [
    # 1. Arithmetic & loops
    ("test_01", "int main() { int sum = 0; for (int i = 0; i < 10; i++) sum += i; std::cout << sum; return 0; }"),
    ("test_02", "int main() { int p = 1; for (int i = 1; i <= 5; i++) p *= i; std::cout << p; return 0; }"),
    ("test_03", "int main() { double x = 2.5; double y = 4.0; std::cout << (x * y); return 0; }"),
    ("test_04", "int main() { int a = 15; int b = 4; std::cout << (a / b); return 0; }"),
    ("test_05", "int main() { int a = 15; int b = 4; std::cout << (a % b); return 0; }"),
    ("test_06", "int sq(int x) { return x * x; } int main() { std::cout << sq(7); return 0; }"),
    ("test_07", "int main() { int x = 10; if (x > 5) std::cout << 1; else std::cout << 0; return 0; }"),
    ("test_08", "int main() { int count = 0; while (count < 5) count++; std::cout << count; return 0; }"),
    ("test_09", "int main() { int mask = (1 << 4); std::cout << mask; return 0; }"),
    ("test_10", "int main() { int a = 12; int b = 25; std::cout << (a & b); return 0; }"),

    # 2. Arrays & pointers
    ("test_11", "int main() { int arr[4] = {1, 2, 3, 4}; std::cout << arr[2]; return 0; }"),
    ("test_12", "int main() { int arr[3] = {10, 20, 30}; int* p = arr; std::cout << *(p + 1); return 0; }"),
    ("test_13", "int main() { int val = 42; int& ref = val; ref = 99; std::cout << val; return 0; }"),
    ("test_14", "struct Pt { int x, y; }; int main() { Pt p = {3, 7}; std::cout << (p.x + p.y); return 0; }"),
    ("test_15", "struct Box { int w, h; }; int main() { Box b = {5, 6}; std::cout << (b.w * b.h); return 0; }"),
    ("test_16", "int main() { std::vector<int> v = {10, 20, 30}; std::cout << v.size(); return 0; }"),
    ("test_17", "int main() { std::vector<int> v = {10, 20, 30}; std::cout << v[1]; return 0; }"),
    ("test_18", "int main() { std::vector<int> v; v.push_back(100); std::cout << v[0]; return 0; }"),
    ("test_19", "int main() { std::string s = \"hello\"; std::cout << s.size(); return 0; }"),
    ("test_20", "int main() { std::string s = \"veloc\"; std::cout << s[0]; return 0; }"),

    # 3. Recursion & Math
    ("test_21", "int fib(int n) { if (n <= 1) return n; return fib(n-1) + fib(n-2); } int main() { std::cout << fib(7); return 0; }"),
    ("test_22", "int fact(int n) { if (n <= 1) return 1; return n * fact(n-1); } int main() { std::cout << fact(5); return 0; }"),
    ("test_23", "int gcd(int a, int b) { while (b) { int t = b; b = a % b; a = t; } return a; } int main() { std::cout << gcd(48, 18); return 0; }"),
    ("test_24", "int main() { double r = 3.0; std::cout << (r * r * 3.1415); return 0; }"),
    ("test_25", "int main() { int x = -42; std::cout << (x < 0 ? -x : x); return 0; }"),
    ("test_26", "int main() { int sum = 0; for (int i = 0; i < 5; i++) for (int j = 0; j < 5; j++) sum++; std::cout << sum; return 0; }"),
    ("test_27", "int main() { int x = 0; do { x++; } while (x < 3); std::cout << x; return 0; }"),
    ("test_28", "int main() { int x = 2; switch (x) { case 1: std::cout << 10; break; case 2: std::cout << 20; break; default: std::cout << 0; } return 0; }"),
    ("test_29", "int main() { int val = 100; auto p = &val; std::cout << *p; return 0; }"),
    ("test_30", "int main() { bool flag = true; std::cout << (flag ? 1 : 0); return 0; }"),

    # 4. Strings & Algorithms
    ("test_31", "int main() { std::string a = \"abc\"; std::string b = \"def\"; std::cout << (a + b); return 0; }"),
    ("test_32", "int main() { int a = 10, b = 20; std::swap(a, b); std::cout << a; return 0; }"),
    ("test_33", "int main() { int a = 5, b = 10; std::cout << std::min(a, b); return 0; }"),
    ("test_34", "int main() { int a = 5, b = 10; std::cout << std::max(a, b); return 0; }"),
    ("test_35", "int main() { std::vector<int> v = {1, 2, 3}; int sum = 0; for (auto x : v) sum += x; std::cout << sum; return 0; }"),
    ("test_36", "int main() { int x = 50; std::cout << (x >> 1); return 0; }"),
    ("test_37", "int main() { int x = 50; std::cout << (x << 1); return 0; }"),
    ("test_38", "int main() { int x = 7; std::cout << (~x); return 0; }"),
    ("test_39", "int main() { int x = 12; int y = 25; std::cout << (x ^ y); return 0; }"),
    ("test_40", "int main() { int x = 12; int y = 25; std::cout << (x | y); return 0; }"),

    # 5. Composite structures & functions
    ("test_41", "struct Vec2 { float x, y; }; Vec2 add(Vec2 a, Vec2 b) { return {a.x + b.x, a.y + b.y}; } int main() { Vec2 v = add({1, 2}, {3, 4}); std::cout << (int)(v.x + v.y); return 0; }"),
    ("test_42", "int main() { int a[5] = {5, 4, 3, 2, 1}; std::cout << (a[0] + a[4]); return 0; }"),
    ("test_43", "int main() { const char* s = \"test\"; std::cout << s[1]; return 0; }"),
    ("test_44", "int main() { int cnt = 0; for (int i = 0; i < 10; i++) { if (i % 2 == 0) continue; cnt++; } std::cout << cnt; return 0; }"),
    ("test_45", "int main() { int cnt = 0; for (int i = 0; i < 10; i++) { if (i == 4) break; cnt++; } std::cout << cnt; return 0; }"),
    ("test_46", "int main() { float f = 1.5f; int i = (int)f; std::cout << i; return 0; }"),
    ("test_47", "int main() { int x = 10; { int x = 20; } std::cout << x; return 0; }"),
    ("test_48", "int add3(int a, int b, int c) { return a + b + c; } int main() { std::cout << add3(1, 2, 3); return 0; }"),
    ("test_49", "int main() { int x = 0; for (int i = 1; i <= 4; i++) x = x * 10 + i; std::cout << x; return 0; }"),
    ("test_50", "int main() { std::vector<int> v(5, 7); std::cout << (v[0] + v[4]); return 0; }")
]

def run_suite():
    root = Path("D:/VeloC")
    test_dir = root / "tests" / "migration" / "generated"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    passed = 0
    total = len(CPP_TEST_CASES)
    print(f"==================================================")
    print(f"   VeloC C++ -> VeloC Migration Suite (50 Tests)  ")
    print(f"==================================================")
    
    for name, cpp_src in CPP_TEST_CASES:
        cpp_file = test_dir / f"{name}.cpp"
        vc_file = test_dir / f"{name}.vc"
        
        # Add boilerplate C++ includes for compilation
        full_cpp = f"#include <iostream>\n#include <vector>\n#include <string>\n#include <cmath>\n#include <algorithm>\n{cpp_src}"
        cpp_file.write_text(full_cpp, encoding="utf-8")
        
        # 1. Transpile to VeloC
        from from_cpp import transpile_cpp_to_veloc
        vc_code = transpile_cpp_to_veloc(full_cpp)
        vc_file.write_text(vc_code, encoding="utf-8")
        
        # 2. Compile and run via veloc.py
        res = subprocess.run([sys.executable, str(root / "veloc.py"), "build", str(vc_file)],
                             capture_output=True, text=True)
        if res.returncode == 0:
            exe_path = root / "build" / f"{name}.exe"
            run_res = subprocess.run([str(exe_path)], capture_output=True, text=True)
            if run_res.returncode == 0:
                passed += 1
                print(f"  [PASS] {name}: output='{run_res.stdout.strip()}'")
            else:
                print(f"  [FAIL] {name}: runtime exit code {run_res.returncode}")
        else:
            print(f"  [FAIL] {name}: build failed")
            
    print("==================================================")
    print(f"Migration Results: {passed} / {total} Passed ({(passed / total) * 100.0:.1f}% Success Rate)")
    print("==================================================")
    return passed == total

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
