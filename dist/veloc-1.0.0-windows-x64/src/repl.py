# VeloC Interactive Read-Eval-Print Loop (REPL)
# High-speed interactive evaluation of expressions, statements, and SIMD functions.

import sys
import os
import time
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT_DIR / ".cache" / "repl"
BUILD_DIR.mkdir(parents=True, exist_ok=True)

class VeloCRepl:
    def __init__(self):
        self.history = []
        self.definitions = []
        self.session_id = int(time.time())
        self.counter = 0
        self.show_timing = True

    def banner(self):
        print("\033[96m========================================================\033[0m")
        print("\033[92m          VeloC Interactive REPL v9.2.0                 \033[0m")
        print("    High-performance native systems language with SIMD    ")
        print("  Type :help for commands, :exit to quit, or an expression")
        print("\033[96m========================================================\033[0m")

    def print_help(self):
        print("\n\033[93mREPL Commands:\033[0m")
        print("  :help        Show this help message")
        print("  :vars        Show registered functions and declarations")
        print("  :clear       Reset REPL environment")
        print("  :time        Toggle execution timing display")
        print("  :exit        Quit the REPL\n")
        print("\033[93mExamples:\033[0m")
        print("  veloc> 2 + 2 * 10")
        print("  veloc> let mut x = 42;")
        print("  veloc> x * 2")
        print("  veloc> let rng = Rng(1234); rng.next_f64()")
        print("  veloc> Path::join(\"a\", \"b.txt\")\n")

    def evaluate(self, user_input: str):
        user_input = user_input.strip()
        if not user_input:
            return

        if user_input in (":exit", ":quit", "exit", "quit"):
            print("\033[90mExiting VeloC REPL. Goodbye!\033[0m")
            sys.exit(0)
        elif user_input == ":help":
            self.print_help()
            return
        elif user_input == ":clear":
            self.definitions.clear()
            print("\033[92mEnvironment reset.\033[0m")
            return
        elif user_input == ":vars":
            print("\033[93mActive declarations:\033[0m")
            for d in self.definitions:
                print(f"  {d}")
            return
        elif user_input == ":time":
            self.show_timing = not self.show_timing
            print(f"\033[92mTiming display: {self.show_timing}\033[0m")
            return

        # Check if declaration or expression
        is_declaration = (
            user_input.startswith("let ") or 
            user_input.startswith("fn ") or 
            user_input.startswith("struct ") or
            user_input.startswith("const ")
        )

        self.counter += 1
        src_file = BUILD_DIR / f"repl_{self.session_id}_{self.counter}.vc"
        exe_file = BUILD_DIR / f"repl_{self.session_id}_{self.counter}.exe"

        lines = ["module Repl;"]
        # Add all previous definitions
        for d in self.definitions:
            if d.startswith("fn ") or d.startswith("struct "):
                lines.append(d)

        lines.append("fn main() -> i32 {")
        for d in self.definitions:
            if not (d.startswith("fn ") or d.startswith("struct ")):
                lines.append(f"    {d}")

        if is_declaration:
            if not user_input.endswith(";"):
                user_input += ";"
            lines.append(f"    {user_input}")
            lines.append('    println("=> [defined]");')
        else:
            # Check if user already added print or semicolon
            clean_expr = user_input.rstrip(";")
            if clean_expr.startswith("println(") or clean_expr.startswith("print("):
                lines.append(f"    {clean_expr};")
            else:
                lines.append(f"    println(f\"=> {{{clean_expr}}}\");")

        lines.append("    return 0;")
        lines.append("}")

        src_file.write_text("\n".join(lines), encoding="utf-8")

        # Compile and execute
        t_compile_start = time.perf_counter()
        try:
            sys.path.insert(0, str(ROOT_DIR))
            from veloc import build_veloc
            build_veloc(src_file, exe_file, opt_level="-O1", quiet=True)
        except Exception as e:
            print(f"\033[91m[Compilation Error]: {e}\033[0m")
            return

        run_cmd = [str(exe_file)]
        t_exec_start = time.perf_counter()
        run_res = subprocess.run(run_cmd, capture_output=True, text=True)
        elapsed_us = (time.perf_counter() - t_exec_start) * 1_000_000.0

        if run_res.returncode == 0:
            print(f"\033[92m{run_res.stdout.strip()}\033[0m")
            if self.show_timing:
                print(f"\033[90m(eval: {elapsed_us:.1f} us)\033[0m")
            if is_declaration:
                self.definitions.append(user_input)
        else:
            print(f"\033[91mRuntime Error: {run_res.stderr or run_res.stdout}\033[0m")

    def run(self):
        self.banner()
        while True:
            try:
                prompt = "\033[94mveloc>\033[0m "
                line = input(prompt)
                self.evaluate(line)
            except (KeyboardInterrupt, EOFError):
                print("\n\033[90mExiting VeloC REPL. Goodbye!\033[0m")
                break

if __name__ == "__main__":
    repl = VeloCRepl()
    repl.run()
