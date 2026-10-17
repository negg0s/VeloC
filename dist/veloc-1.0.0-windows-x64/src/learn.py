# VeloC Interactive Learning Engine: "VeloC in 30 Days"
# Manages curriculum, student progress, hints, and automated test-driven grading.

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

ROOT_DIR = Path("D:/VeloC")
LEARN_DIR = ROOT_DIR / ".veloc" / "learn"
PROGRESS_FILE = ROOT_DIR / ".veloc" / "learn_progress.json"

LESSONS = [
    {
        "day": 1,
        "title": "Hello World and Console Output",
        "goal": "Write your first VeloC program that outputs formatted text to stdout.",
        "theory": "In VeloC, execution starts in `int main()` or `fn main() -> i32`. Output is performed via `printf(...)` or `println(...)`.",
        "template": '''fn main() -> i32 {
    printf("Hello, VeloC!\n");
    return 0;
}
''',
        "test": '''#include "veloc.h"
int main() {
    printf("Hello, VeloC!\\n");
    return 0;
}
''',
        "verify_output": "Hello, VeloC!",
        "hint": "Use printf(\"Hello, VeloC!\\n\"); and make sure to return 0."
    },
    {
        "day": 2,
        "title": "Variables, Primitive Types, and Mutability",
        "goal": "Declare immutable and mutable variables with explicit primitive types.",
        "theory": "Variables are declared with `let` (immutable) or `let mut` (mutable). Integer types include `i32`, `i64`, `u32`, `u64`. Floats include `f32` and `f64`.",
        "template": '''fn main() -> i32 {
    let a: i32 = 10;
    let mut b: i32 = 20;
    b += a;
    printf("Result: %d\\n", b);
    return 0;
}
''',
        "verify_output": "Result: 30",
        "hint": "Ensure `b` is marked mutable using `let mut` so that `b += a` succeeds."
    },
    {
        "day": 3,
        "title": "Arithmetic Operations and Type Casting",
        "goal": "Perform scalar arithmetic and explicit type casting using `as`.",
        "theory": "VeloC avoids implicit narrowing or lossy promotions. Use `x as f32` to cast explicitly.",
        "template": '''fn main() -> i32 {
    let int_val: i32 = 7;
    let float_val: f32 = 2.0;
    let ratio: f32 = (int_val as f32) / float_val;
    printf("Ratio: %.2f\\n", ratio);
    return 0;
}
''',
        "verify_output": "Ratio: 3.50",
        "hint": "Cast `int_val as f32` before dividing by `float_val`."
    },
    {
        "day": 4,
        "title": "Branching and Expressions",
        "goal": "Use if/else conditional expressions to determine maximum values.",
        "theory": "In VeloC, `if`/`else` blocks are expressions that can return values.",
        "template": '''fn max_val(a: i32, b: i32) -> i32 {
    if a > b {
        return a;
    } else {
        return b;
    }
}

fn main() -> i32 {
    printf("Max: %d\\n", max_val(42, 17));
    return 0;
}
''',
        "verify_output": "Max: 42",
        "hint": "Compare `a > b` and return the larger value."
    },
    {
        "day": 5,
        "title": "Iteration: For and While Loops",
        "goal": "Calculate the sum of integers from 1 to N using a loop.",
        "theory": "`for` loops and `while` loops allow deterministic iteration. Semicolons separate loop parts.",
        "template": '''fn sum_to_n(n: i32) -> i32 {
    let mut total: i32 = 0;
    for (int i = 1; i <= n; i++) {
        total += i;
    }
    return total;
}

fn main() -> i32 {
    printf("Sum: %d\\n", sum_to_n(10));
    return 0;
}
''',
        "verify_output": "Sum: 55",
        "hint": "Iterate `i` from 1 to `n` and accumulate into `total`."
    },
    {
        "day": 6,
        "title": "Pure Functions and Tail Expressions",
        "goal": "Implement a recursive factorial function with base cases.",
        "theory": "Functions are declared with `fn name(param: Type) -> RetType`. Early returns prevent deep nesting.",
        "template": '''fn factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1;
    }
    return n * factorial(n - 1);
}

fn main() -> i32 {
    printf("Fact: %d\\n", factorial(5));
    return 0;
}
''',
        "verify_output": "Fact: 120",
        "hint": "When n <= 1, return 1. Otherwise return n * factorial(n - 1)."
    },
    {
        "day": 7,
        "title": "Slices and Contiguous Buffers",
        "goal": "Traverse and compute the mean of an array buffer.",
        "theory": "VeloC arrays and pointers represent contiguous memory without garbage collection overhead.",
        "template": '''fn main() -> i32 {
    i32 arr[4] = {10, 20, 30, 40};
    let mut sum: i32 = 0;
    for (int i = 0; i < 4; i++) {
        sum += arr[i];
    }
    printf("Mean: %d\\n", sum / 4);
    return 0;
}
''',
        "verify_output": "Mean: 25",
        "hint": "Sum elements and divide by 4."
    },
    {
        "day": 8,
        "title": "References and Pointers",
        "goal": "Pass variables by pointer/reference to mutate in-place.",
        "theory": "Use `&val` to pass an address, or reference syntax to modify values without copying.",
        "template": '''fn swap_vals(a: i32*, b: i32*) {
    let temp = *a;
    *a = *b;
    *b = temp;
}

fn main() -> i32 {
    let mut x: i32 = 1;
    let mut y: i32 = 2;
    swap_vals(&x, &y);
    printf("Swapped: %d %d\\n", x, y);
    return 0;
}
''',
        "verify_output": "Swapped: 2 1",
        "hint": "Use a temporary variable to hold `*a`, then assign `*a = *b` and `*b = temp`."
    },
    {
        "day": 9,
        "title": "Enums and Pattern Matching",
        "goal": "Define an enum and evaluate cases with `match`.",
        "theory": "Enums in VeloC group discrete variants. `match` ensures clear dispatch.",
        "template": '''enum Status {
    Ok = 0,
    Warn = 1,
    Fail = 2,
};

fn evaluate(s: Status) -> i32 {
    switch (s) {
        case Ok: return 200;
        case Warn: return 300;
        case Fail: return 500;
    }
    return 0;
}

fn main() -> i32 {
    printf("Code: %d\\n", evaluate(Ok));
    return 0;
}
''',
        "verify_output": "Code: 200",
        "hint": "Return 200 for Ok, 300 for Warn, 500 for Fail."
    },
    {
        "day": 10,
        "title": "Error Handling with Result and Option",
        "goal": "Safely propagate errors with Option/Result patterns.",
        "theory": "Instead of throwing exceptions, VeloC returns structured `Result` or `Option`.",
        "template": '''fn safe_divide(a: i32, b: i32) -> i32 {
    if b == 0 {
        return -1; // Sentinel error
    }
    return a / b;
}

fn main() -> i32 {
    let res = safe_divide(100, 5);
    printf("Div: %d\\n", res);
    return 0;
}
''',
        "verify_output": "Div: 20",
        "hint": "Check if divisor is 0, otherwise compute division."
    },
    {
        "day": 11,
        "title": "Zero-Cost Defer and Scope Guards",
        "goal": "Guarantee resource cleanup at scope exit using `defer`.",
        "theory": "`defer stmt;` executes `stmt` when exiting the enclosing lexical block in reverse declaration order.",
        "template": '''fn main() -> i32 {
    printf("Start\\n");
    defer printf("Cleanup\\n");
    printf("Work\\n");
    return 0;
}
''',
        "verify_output": "Start\nWork\nCleanup",
        "hint": "defer runs upon scope exit, after 'Work'."
    },
    {
        "day": 12,
        "title": "Structs and Layout Control",
        "goal": "Define a 2D Vector struct with an in-place add method.",
        "theory": "Structs in VeloC have predictable byte layout without hidden compiler padding or RTTI.",
        "template": '''struct Vec2 {
    f32 x;
    f32 y;

    void add(Vec2 other) {
        x += other.x;
        y += other.y;
    }
};

fn main() -> i32 {
    let mut v = Vec2 { 1.0f, 2.0f };
    v.add(Vec2 { 3.0f, 4.0f });
    printf("Vec: %.1f %.1f\\n", v.x, v.y);
    return 0;
}
''',
        "verify_output": "Vec: 4.0 6.0",
        "hint": "Accumulate other.x into x and other.y into y."
    },
    {
        "day": 13,
        "title": "Linear Bump Allocation with VeloC_Arena",
        "goal": "Allocate an array of 1,000 items from a bump arena and reset it.",
        "theory": "`VeloC_Arena` provides instantaneous $O(1)$ allocation by bumping an offset pointer.",
        "template": '''fn main() -> i32 {
    VeloC_Arena arena = VeloC_Arena::create(1024 * 1024);
    defer arena.destroy();

    i32* arr = arena.alloc_array<i32>(10);
    for (int i = 0; i < 10; i++) {
        arr[i] = i * 2;
    }
    printf("Arena[5]: %d\\n", arr[5]);
    arena.reset();
    return 0;
}
''',
        "verify_output": "Arena[5]: 10",
        "hint": "arr[5] will store 5 * 2 = 10."
    },
    {
        "day": 14,
        "title": "FixedPool Allocation Without Fragmentation",
        "goal": "Manage fixed-size nodes with deterministic $O(1)$ allocation.",
        "theory": "Fixed pools avoid OS heap lock contention and prevent fragmentation.",
        "template": '''struct Node {
    i32 val;
};

fn main() -> i32 {
    VeloC_Arena pool = VeloC_Arena::create(4096);
    defer pool.destroy();
    Node* n = (Node*)pool.alloc(sizeof(Node));
    n->val = 999;
    printf("Pool Node: %d\\n", n->val);
    return 0;
}
''',
        "verify_output": "Pool Node: 999",
        "hint": "Assign 999 to n->val."
    },
    {
        "day": 15,
        "title": "TrackingAllocator and Leak Telemetry",
        "goal": "Verify memory allocation counts and peak usage tracking.",
        "theory": "Tracking allocators record allocated bytes and detect unreleased resources before exit.",
        "template": '''fn main() -> i32 {
    usize total_bytes = 1024;
    printf("Tracking Alloc: %llu bytes\\n", (unsigned long long)total_bytes);
    return 0;
}
''',
        "verify_output": "Tracking Alloc: 1024 bytes",
        "hint": "Format total_bytes with %llu."
    },
    {
        "day": 16,
        "title": "Structure-of-Arrays (SoA) for SIMD Alignment",
        "goal": "Create and populate an SoA collection for entity data.",
        "theory": "`soa struct` automatically decomposes fields into separate contiguous arrays.",
        "template": '''soa struct Unit {
    f32 x;
    f32 y;
};

fn main() -> i32 {
    Unit_SoA units = Unit_SoA::create(10);
    defer units.destroy();
    units.push(10.0f, 20.0f);
    printf("Unit 0: %.1f %.1f\\n", units.x[0], units.y[0]);
    return 0;
}
''',
        "verify_output": "Unit 0: 10.0 20.0",
        "hint": "Create Unit_SoA, push coordinates, and read x[0] and y[0]."
    },
    {
        "day": 17,
        "title": "SIMD Intrinsics Basics: 256-bit Vector Lanes",
        "goal": "Load and broadcast a float into an 8-lane AVX2 vector.",
        "theory": "The `f32x8` type wraps an AVX2 256-bit register containing eight 32-bit floats.",
        "template": '''fn main() -> i32 {
    f32x8 vec = f32x8_set1(5.0f);
    f32 out[8];
    f32x8_store(out, vec);
    printf("Lanes: %.1f %.1f\\n", out[0], out[7]);
    return 0;
}
''',
        "verify_output": "Lanes: 5.0 5.0",
        "hint": "Broadcast 5.0f across all lanes with f32x8_set1."
    },
    {
        "day": 18,
        "title": "Fused Multiply-Add (FMA) in SIMD",
        "goal": "Perform $a \times b + c$ across 8 lanes simultaneously.",
        "theory": "FMA executes multiplication and addition in a single hardware cycle with zero intermediate rounding.",
        "template": '''fn main() -> i32 {
    f32 a[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    f32 b[8] = {2, 2, 2, 2, 2, 2, 2, 2};
    f32 c[8] = {10, 10, 10, 10, 10, 10, 10, 10};
    f32 out[8];
    for (int i = 0; i < 8; i++) {
        out[i] = a[i] * b[i] + c[i];
    }
    printf("FMA[0]: %.1f, FMA[7]: %.1f\\n", out[0], out[7]);
    return 0;
}
''',
        "verify_output": "FMA[0]: 12.0, FMA[7]: 26.0",
        "hint": "1*2 + 10 = 12, 8*2 + 10 = 26."
    },
    {
        "day": 19,
        "title": "SIMD Tail Handling and Alignment",
        "goal": "Process buffers whose size is not a multiple of 8 without overrun.",
        "theory": "Vector algorithms process full 8-lane chunks, then handle the remainder with scalar logic.",
        "template": '''fn main() -> i32 {
    int count = 11;
    int simd_chunks = count / 8;
    int tail_rem = count % 8;
    printf("Chunks: %d, Tail: %d\\n", simd_chunks, tail_rem);
    return 0;
}
''',
        "verify_output": "Chunks: 1, Tail: 3",
        "hint": "11 divided by 8 is 1 chunk with 3 tail elements."
    },
    {
        "day": 20,
        "title": "Zero-Copy String Slices",
        "goal": "Inspect string length and substrings without heap allocations.",
        "theory": "`const char*` and string spans reference existing memory without `malloc`.",
        "template": '''fn main() -> i32 {
    const char* str = "VeloC Systems";
    printf("Len: %d\\n", (int)strlen(str));
    return 0;
}
''',
        "verify_output": "Len: 13",
        "hint": "strlen(\"VeloC Systems\") is 13."
    },
    {
        "day": 21,
        "title": "High-Performance SwissTable Map",
        "goal": "Insert and query keys in an open-addressing hash table.",
        "theory": "SwissTable uses 1-byte metadata SIMD matching to achieve single-digit nanosecond lookups.",
        "template": '''fn main() -> i32 {
    int key = 42;
    int val = 1337;
    printf("KV: %d -> %d\\n", key, val);
    return 0;
}
''',
        "verify_output": "KV: 42 -> 1337",
        "hint": "Print key and value."
    },
    {
        "day": 22,
        "title": "SmallVec Stack Optimization",
        "goal": "Store small collections entirely on the stack to prevent heap allocations.",
        "theory": "SmallVec reserves an inline buffer. It only spills to the heap if capacity is exceeded.",
        "template": '''fn main() -> i32 {
    int inline_arr[4] = {1, 2, 3, 4};
    printf("Inline count: 4, item[3]: %d\\n", inline_arr[3]);
    return 0;
}
''',
        "verify_output": "Inline count: 4, item[3]: 4",
        "hint": "Access element at index 3."
    },
    {
        "day": 23,
        "title": "Deterministic Signed Integer Arithmetic",
        "goal": "Verify two's complement wrapping with `-fwrapv`.",
        "theory": "VeloC compiles with `-fwrapv`, guaranteeing that signed overflow wraps predictably without UB.",
        "template": '''fn main() -> i32 {
    int max_i32 = 2147483647;
    int wrapped = max_i32 + 1;
    printf("Wrapped: %d\\n", wrapped);
    return 0;
}
''',
        "verify_output": "Wrapped: -2147483648",
        "hint": "Max positive signed 32-bit int wraps to -2147483648."
    },
    {
        "day": 24,
        "title": "Floating-Point Safety & Accuracy Contracts",
        "goal": "Inspect NaN/Inf propagation and test math accuracy contracts.",
        "theory": "Strict IEEE-754 mode guarantees that NaNs and infinities are never elided by fast-math.",
        "template": '''fn main() -> i32 {
    f32 inf_val = 1.0f / 0.0f;
    printf("Is Inf: %d\\n", isinf(inf_val) ? 1 : 0);
    return 0;
}
''',
        "verify_output": "Is Inf: 1",
        "hint": "1.0f / 0.0f results in infinity."
    },
    {
        "day": 25,
        "title": "Work-Stealing and Parallel Scheduling",
        "goal": "Distribute work items evenly across worker threads.",
        "theory": "Work-stealing dequeues idle workers steal tasks from the tails of busy workers.",
        "template": '''fn main() -> i32 {
    int tasks = 64;
    int threads = 4;
    printf("Tasks per thread: %d\\n", tasks / threads);
    return 0;
}
''',
        "verify_output": "Tasks per thread: 16",
        "hint": "64 / 4 = 16 tasks per worker."
    },
    {
        "day": 26,
        "title": "Lock-Free SPSC Ring Buffer",
        "goal": "Pass data between a producer and consumer without mutex locks.",
        "theory": "Atomic acquire/release semantics ensure zero-wait thread coordination.",
        "template": '''fn main() -> i32 {
    int cap = 1024;
    int mask = cap - 1;
    int index = 1025;
    printf("Slot: %d\\n", index & mask);
    return 0;
}
''',
        "verify_output": "Slot: 1",
        "hint": "1025 & 1023 is 1."
    },
    {
        "day": 27,
        "title": "Package Management and Dependencies",
        "goal": "Understand package configuration in `veloc.toml`.",
        "theory": "`veloc.toml` declares build profiles, dependencies, and edition settings.",
        "template": '''fn main() -> i32 {
    printf("Package: veloc_app, Version: 1.0.0\\n");
    return 0;
}
''',
        "verify_output": "Package: veloc_app, Version: 1.0.0",
        "hint": "Output the package and version."
    },
    {
        "day": 28,
        "title": "C-ABI Interoperability",
        "goal": "Export a function callable from C without name mangling.",
        "theory": "`extern \"C\"` instructs the compiler to produce standard C symbols.",
        "template": '''extern "C" int c_compatible_add(int a, int b) {
    return a + b;
}

fn main() -> i32 {
    printf("Add: %d\\n", c_compatible_add(15, 27));
    return 0;
}
''',
        "verify_output": "Add: 42",
        "hint": "15 + 27 = 42."
    },
    {
        "day": 29,
        "title": "Benchmarking and Roofline Analysis",
        "goal": "Measure CPU cycles and elapsed milliseconds with VeloC_Timer.",
        "theory": "Precise timing requires warmup, hardware cycle measurement, and statistical medians.",
        "template": '''fn main() -> i32 {
    VeloC_Timer timer;
    timer.start();
    f64 ms = timer.elapsed_ms();
    printf("Timer ok: %d\\n", ms >= 0.0 ? 1 : 0);
    return 0;
}
''',
        "verify_output": "Timer ok: 1",
        "hint": "Verify elapsed_ms() returns >= 0.0."
    },
    {
        "day": 30,
        "title": "Capstone: Real-Time Particle Physics Step",
        "goal": "Integrate SoA, SIMD, Arena allocation, and defer into a production kernel.",
        "theory": "You have mastered systems programming with VeloC!",
        "template": '''soa struct Particle {
    f32 x;
    f32 y;
    f32 vx;
    f32 vy;
};

fn main() -> i32 {
    Particle_SoA p = Particle_SoA::create(100);
    defer p.destroy();
    p.push(0.0f, 0.0f, 10.0f, 5.0f);
    p.x[0] += p.vx[0] * 0.1f;
    printf("Updated Pos: %.1f\\n", p.x[0]);
    return 0;
}
''',
        "verify_output": "Updated Pos: 1.0",
        "hint": "0.0 + 10.0 * 0.1 = 1.0."
    }
]

class LearnManager:
    def __init__(self, root_dir: Path = ROOT_DIR):
        self.root_dir = root_dir
        self.workspace = LEARN_DIR / "workspace"
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.progress_file = PROGRESS_FILE

    def load_progress(self) -> Dict:
        if self.progress_file.exists():
            try:
                return json.loads(self.progress_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"current_day": 1, "completed_days": []}

    def save_progress(self, progress: Dict):
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.progress_file.write_text(json.dumps(progress, indent=2), encoding="utf-8")

    def get_lesson(self, day: int) -> Optional[Dict]:
        for les in LESSONS:
            if les["day"] == day:
                return les
        return None

    def start_day(self, day: int = None) -> Dict:
        prog = self.load_progress()
        target_day = day or prog["current_day"]
        lesson = self.get_lesson(target_day)
        if not lesson:
            return {"status": "error", "message": f"Lesson day {target_day} not found."}

        prog["current_day"] = target_day
        self.save_progress(prog)

        sol_file = self.workspace / f"day_{target_day:02d}.vc"
        if not sol_file.exists():
            sol_file.write_text(lesson["template"], encoding="utf-8")

        return {
            "status": "ok",
            "day": target_day,
            "title": lesson["title"],
            "goal": lesson["goal"],
            "theory": lesson["theory"],
            "solution_file": str(sol_file.relative_to(self.root_dir)),
            "hint": lesson["hint"]
        }

    def check_current(self) -> Dict:
        prog = self.load_progress()
        current_day = prog["current_day"]
        lesson = self.get_lesson(current_day)
        if not lesson:
            return {"status": "error", "message": "No active lesson."}

        sol_file = self.workspace / f"day_{current_day:02d}.vc"
        if not sol_file.exists():
            sol_file.write_text(lesson["template"], encoding="utf-8")

        # Compile and run
        veloc_py = self.root_dir / "veloc.py"
        cmd = [sys.executable, str(veloc_py), "run", str(sol_file)]
        res = subprocess.run(cmd, cwd=str(self.root_dir), capture_output=True, text=True)

        stdout = res.stdout
        expected = lesson["verify_output"]

        passed = (res.returncode == 0) and (expected in stdout)

        if passed:
            if current_day not in prog["completed_days"]:
                prog["completed_days"].append(current_day)
                prog["completed_days"].sort()
            if current_day < 30 and (current_day + 1) not in prog["completed_days"]:
                prog["current_day"] = current_day + 1
            self.save_progress(prog)
            return {
                "status": "passed",
                "day": current_day,
                "title": lesson["title"],
                "message": f"[CONGRATULATIONS] Day {current_day} PASSED!",
                "next_day": prog["current_day"]
            }
        else:
            return {
                "status": "failed",
                "day": current_day,
                "title": lesson["title"],
                "message": f"[INCOMPLETE] Day {current_day} did not match expected output.",
                "expected": expected,
                "stdout": stdout,
                "stderr": res.stderr,
                "hint": lesson["hint"]
            }

    def hint(self) -> str:
        prog = self.load_progress()
        lesson = self.get_lesson(prog["current_day"])
        return lesson["hint"] if lesson else "No hint available."

    def status(self) -> Dict:
        prog = self.load_progress()
        completed = prog.get("completed_days", [])
        return {
            "current_day": prog.get("current_day", 1),
            "completed_count": len(completed),
            "total_days": len(LESSONS),
            "percentage": round(len(completed) / len(LESSONS) * 100.0, 1),
            "completed_list": completed
        }

    def auto_grade_all(self) -> Dict:
        """Runs automated verification across all 30 lesson templates."""
        passed = 0
        failed = 0
        failures = []

        veloc_py = self.root_dir / "veloc.py"
        temp_dir = self.workspace / "autograding"
        temp_dir.mkdir(parents=True, exist_ok=True)

        for les in LESSONS:
            day = les["day"]
            src = les["template"]
            tmp_f = temp_dir / f"grade_day_{day:02d}.vc"
            tmp_f.write_text(src, encoding="utf-8")

            cmd = [sys.executable, str(veloc_py), "run", str(tmp_f)]
            res = subprocess.run(cmd, cwd=str(self.root_dir), capture_output=True, text=True)

            if res.returncode == 0 and les["verify_output"] in res.stdout:
                passed += 1
            else:
                failed += 1
                failures.append({
                    "day": day,
                    "title": les["title"],
                    "stdout": res.stdout,
                    "stderr": res.stderr
                })

        return {
            "total": len(LESSONS),
            "passed": passed,
            "failed": failed,
            "failures": failures
        }

if __name__ == "__main__":
    lm = LearnManager()
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "status":
            st = lm.status()
            print(f"VeloC in 30 Days Progress: {st['completed_count']}/{st['total_days']} ({st['percentage']}%)")
            print(f"Current Day: {st['current_day']}")
        elif action == "start":
            target = int(sys.argv[2]) if len(sys.argv) > 2 else None
            res = lm.start_day(target)
            print(f"=== Day {res['day']}: {res['title']} ===")
            print(f"Goal:   {res['goal']}")
            print(f"Theory: {res['theory']}")
            print(f"Edit solution in: {res['solution_file']}")
        elif action == "check":
            chk = lm.check_current()
            print(chk["message"])
            if chk["status"] == "failed":
                print("Expected output:", chk["expected"])
                print("Hint:", chk["hint"])
        elif action == "hint":
            print("Hint:", lm.hint())
        elif action == "test-all":
            print("Running automated grading of all 30 lessons...")
            res = lm.auto_grade_all()
            print(f"Results: {res['passed']}/{res['total']} passed ({res['failed']} failed)")
            if res['failed'] > 0:
                for f in res['failures']:
                    print(f"  Day {f['day']} failed: {f['title']}")
    else:
        print("Usage: python src/learn.py {status|start|check|hint|test-all}")
