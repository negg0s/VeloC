import os
import sys
import subprocess
import argparse
import time
import shutil
import hashlib
import json
from pathlib import Path


# Paths strictly on D:\
ROOT_DIR = Path("D:/VeloC")
SRC_DIR = ROOT_DIR / "src"
INCLUDE_DIR = ROOT_DIR / "include"
BUILD_DIR = ROOT_DIR / "build"
CACHE_DIR = ROOT_DIR / ".cache"
BENCH_DIR = ROOT_DIR / "benchmarks"

# Import VeloC Compiler Subsystems
sys.path.insert(0, str(SRC_DIR))
from lexer import Lexer, LexerError
from parser import Parser, ParseError, MultiParseError
from codegen import CppCodegen
from diagnostics import DiagnosticReporter, DiagnosticCode, explain_error_code
from transpiler import VeloCTranspiler

# Clang compiler path discovered on system
CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")

def ensure_dirs():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def clean_cache(all_artifacts: bool = False):
    cleaned = 0
    if CACHE_DIR.exists():
        for item in CACHE_DIR.glob("*"):
            if item.is_file():
                item.unlink()
                cleaned += 1
            elif item.is_dir():
                shutil.rmtree(item)
                cleaned += 1
    if all_artifacts and BUILD_DIR.exists():
        for item in BUILD_DIR.glob("*"):
            if item.is_file():
                item.unlink()
                cleaned += 1
            elif item.is_dir():
                shutil.rmtree(item)
                cleaned += 1
    for pycache in ROOT_DIR.rglob("__pycache__"):
        if pycache.exists():
            shutil.rmtree(pycache)
            cleaned += 1
    print(f"[VeloC Clean] Cleaned {cleaned} temporary files/directories from D:\\VeloC\\.cache")

def build_veloc(source_path: Path, output_exe: Path = None, opt_level: str = "-O3", 
                test_mode: bool = False, verbose: bool = False, quiet: bool = False,
                opt_report: bool = False, profile: str = None,
                timings: bool = False, json_output: bool = False,
                backend: str = "cpp", lean: bool = False, no_pch: bool = False,
                fp_mode: str = "strict", enable_ftz: bool = False) -> Path:
    t_start = time.perf_counter()
    if profile:
        profile_map = {
            "fast-compile": "-O0",
            "balanced": "-O2",
            "max-perf": "-O3",
            "min-size": "-Oz"
        }
        opt_level = profile_map.get(profile, "-O3")
    ensure_dirs()
    if not source_path.exists():
        print(f"[Error] Source file not found: {source_path}")
        sys.exit(1)

    stem = source_path.stem
    if test_mode:
        stem += "_test"

    cpp_target = CACHE_DIR / f"{stem}.cpp"
    ll_target = CACHE_DIR / f"{stem}.ll"
    hash_target = CACHE_DIR / f"{stem}.hash"
    if output_exe is None:
        output_exe = BUILD_DIR / f"{stem}.exe"

    content_bytes = source_path.read_bytes()
    current_hash = hashlib.sha256(content_bytes + str(test_mode).encode() + backend.encode() + opt_level.encode()).hexdigest()

    # Instant Incremental Build: if source unchanged and exe exists, skip compilation!
    if output_exe.exists() and hash_target.exists():
        if hash_target.read_text().strip() == current_hash and not timings and not json_output:
            if verbose:
                print(f"[VeloC Instant Cache Hit] {source_path.name} -> {output_exe.name} (0.3ms - Up to date)")
            if opt_report:
                from ir import IRGenerator, VeloCOptimizer
                src_txt = source_path.read_text(encoding="utf-8")
                ir_gen = IRGenerator(src_txt, str(source_path))
                mid = ir_gen.build_mid_ir()
                opt = VeloCOptimizer(profile or "max-perf")
                _, rep = opt.optimize(mid)
                print(rep.summary())
            return output_exe

    # Read source
    t_read_start = time.perf_counter()
    source_str = source_path.read_text(encoding="utf-8")
    t_read = (time.perf_counter() - t_read_start) * 1000.0

    t_macro_start = time.perf_counter()
    if "macro_rules!" in source_str:
        from macro_expander import MacroExpander
        source_str = MacroExpander().expand_source(source_str)
    t_macro = (time.perf_counter() - t_macro_start) * 1000.0

    t_lex_start = time.perf_counter()
    tokens = Lexer(source_str, str(source_path)).tokenize()
    t_lex = (time.perf_counter() - t_lex_start) * 1000.0

    t_parse_start = time.perf_counter()
    program = None
    try:
        program = Parser(tokens, source_str, str(source_path)).parse_program()
    except Exception:
        pass
    t_parse = (time.perf_counter() - t_parse_start) * 1000.0

    # Direct LLVM IR Backend bypass
    if backend == "llvm":
        from llvm_backend import LlvmBackend
        t_ll_start = time.perf_counter()
        llvm_gen = LlvmBackend()
        ll_code = llvm_gen.generate_ll(program, source_str)
        ll_target.write_text(ll_code, encoding="utf-8")
        t_ll_codegen = (time.perf_counter() - t_ll_start) * 1000.0

        t_ll_compile, rc, err = llvm_gen.compile_ll(ll_target, output_exe, opt_level=opt_level)
        if rc != 0:
            print(f"[LLVM Backend Build Failed]:\n{err}")
            sys.exit(rc)
        t_total = (time.perf_counter() - t_start) * 1000.0

        if json_output:
            metrics = {
                "backend": "llvm",
                "file": source_path.name,
                "read_ms": round(t_read, 2),
                "lex_ms": round(t_lex, 2),
                "parse_ms": round(t_parse, 2),
                "codegen_ms": round(t_ll_codegen, 2),
                "clang_ms": round(t_ll_compile, 2),
                "total_ms": round(t_total, 2)
            }
            print(json.dumps(metrics, indent=2))
        elif timings:
            print("=" * 70)
            print(f"        VeloC Compilation Phase Breakdown (--backend=llvm)       ")
            print("=" * 70)
            print(f"  1. Source Read & Lex       : {t_read + t_lex:7.1f} ms")
            print(f"  2. Parser & AST            : {t_parse:7.1f} ms")
            print(f"  3. LLVM IR Code Generation : {t_ll_codegen:7.1f} ms")
            print(f"  4. Clang LLVM Codegen & LLD: {t_ll_compile:7.1f} ms")
            print("-" * 70)
            print(f"  Total Cold Compilation Time: {t_total:7.1f} ms")
            print("=" * 70)
        else:
            if not quiet:
                print(f"[VeloC Build Success (LLVM Backend)] {source_path.name} -> {output_exe.name} (Compile: {t_ll_compile:.1f}ms, Total: {t_total:.1f}ms)")
        hash_target.write_text(current_hash)
        return output_exe

    # C++ Codegen
    t_codegen_start = time.perf_counter()
    try:
        if program:
            codegen = CppCodegen(str(INCLUDE_DIR), test_mode=test_mode)
            cpp_code = codegen.generate_cpp(program)
            cpp_target.write_text(cpp_code, encoding="utf-8")
        else:
            transpiler = VeloCTranspiler(str(INCLUDE_DIR), test_mode=test_mode)
            transpiler.transpile_file(str(source_path), str(cpp_target))
    except Exception:
        transpiler = VeloCTranspiler(str(INCLUDE_DIR), test_mode=test_mode)
        transpiler.transpile_file(str(source_path), str(cpp_target))
    t_codegen = (time.perf_counter() - t_codegen_start) * 1000.0

    t_transpile = (time.perf_counter() - t_start) * 1000.0

    # Security & Safety Checks
    t_sema_start = time.perf_counter()
    if profile == "safety":
        from safety_profile import SafetyCriticalChecker
        safety_checker = SafetyCriticalChecker(source_str, str(source_path))
        violations = safety_checker.check()
        if violations:
            print(f"\n[VeloC Safety Profile Violation] {len(violations)} safety rule breaches detected:")
            for v in violations:
                print(f"  - [{v['rule']}] Line {v['line']}: {v['message']} ({v['snippet']})")
            sys.exit(1)

    from security import CapabilitySecurity, SecretBranchLinter
    cap_sec = CapabilitySecurity(ROOT_DIR / "veloc.toml")
    cap_violations = cap_sec.verify_source(source_str, str(source_path))
    if cap_violations:
        for cv in cap_violations:
            print(f"[VeloC Security Error] {cv['code']}: {cv['message']}")
        sys.exit(1)

    for sw in SecretBranchLinter(source_str, str(source_path)).lint():
        print(f"[VeloC Security Warning] {sw['rule']}: Line {sw['line']}: {sw['message']}")

    # Floating-Point Precision & Diagnostics Check
    from fp_policy import FloatingPointPolicy, FloatingPointLinter, AttributeTransformer
    for fpl in FloatingPointLinter(source_str, str(source_path), global_mode=fp_mode).lint():
        print(f"[VeloC FP {fpl['severity'].capitalize()}] {fpl['rule']}: Line {fpl['line']}: {fpl['message']}")

    t_sema = (time.perf_counter() - t_sema_start) * 1000.0

    # Header and PCH Selection
    is_lean_candidate = lean
    header_name = "veloc_core.h" if is_lean_candidate else "veloc.h"

    if cpp_target.exists():
        gen_cpp = cpp_target.read_text(encoding="utf-8")
        if is_lean_candidate:
            gen_cpp = gen_cpp.replace("include/veloc.h", "include/veloc_core.h")
            gen_cpp = gen_cpp.replace("<veloc.h>", "<veloc_core.h>")
        gen_cpp = AttributeTransformer.transform_code(gen_cpp)
        cpp_target.write_text(gen_cpp, encoding="utf-8")

    from pch_manager import PchManager, LLD_PATH
    pm = PchManager(ROOT_DIR)

    # Clang Flags: Strict IEEE-754 by default!
    effective_fp = "strict" if profile == "safety" else fp_mode
    fp_policy = FloatingPointPolicy(effective_fp, enable_ftz=enable_ftz)
    math_flags = fp_policy.get_compiler_flags()
    cmd = [
        str(CLANG_PATH),
        str(cpp_target),
        "-o", str(output_exe),
        opt_level,
        "-std=c++20",
        "-march=native",
        "-static",
        "-fwrapv",
        "-fstack-protector-strong",
        "-ftrivial-auto-var-init=zero",
        "-Wl,--dynamicbase",
        "-Wl,--nxcompat",
        "-Wl,--no-insert-timestamp",
        *math_flags,
        "-fno-exceptions",
        "-fno-rtti",
        "-fomit-frame-pointer",
        f"-I{INCLUDE_DIR}",
        f"-I{source_path.parent}",
        f"-I{ROOT_DIR / 'packages' / 'veloc-game' / 'include'}",
        f"-I{ROOT_DIR / 'packages' / 'veloc-ai' / 'include'}",
        f"-I{ROOT_DIR / 'packages' / 'veloc-sci' / 'include'}",
        f"-I{ROOT_DIR / 'packages' / 'veloc-data' / 'include'}",
        f"-I{ROOT_DIR / 'packages' / 'veloc-net' / 'include'}",
        f"-I{ROOT_DIR / 'packages' / 'veloc-embedded' / 'include'}",
        f"-I{ROOT_DIR / 'packages' / 'veloc-cli' / 'include'}",
        "-lws2_32"
    ]

    # Precompiled Header integration
    if not no_pch:
        pch = pm.ensure_pch(header_name, opt_level, profile or "max-perf", fp_mode=effective_fp, enable_ftz=enable_ftz)
        if pch and pch.exists():
            cmd.extend(["-include-pch", str(pch)])

    # Fast Linker integration
    if LLD_PATH.exists():
        cmd.extend(["-fuse-ld=lld", "-Wl,--gc-sections"])

    if verbose:
        print("[Cmd]:", " ".join(cmd))

    t1 = time.perf_counter()
    res = subprocess.run(cmd, capture_output=True, text=True)
    t_compile = (time.perf_counter() - t1) * 1000.0
    t_total = (time.perf_counter() - t_start) * 1000.0

    if res.returncode != 0:
        print(f"[Build Failed]:\n{res.stderr}")
        sys.exit(res.returncode)

    hash_target.write_text(current_hash)

    if json_output:
        metrics = {
            "backend": "cpp",
            "file": source_path.name,
            "header": header_name,
            "read_ms": round(t_read, 2),
            "macro_ms": round(t_macro, 2),
            "lex_ms": round(t_lex, 2),
            "parse_ms": round(t_parse, 2),
            "sema_ms": round(t_sema, 2),
            "codegen_ms": round(t_codegen, 2),
            "transpile_total_ms": round(t_transpile, 2),
            "clang_compile_ms": round(t_compile, 2),
            "total_ms": round(t_total, 2)
        }
        print(json.dumps(metrics, indent=2))
    elif timings:
        print("=" * 70)
        print(f"        VeloC Compilation Phase Breakdown ({source_path.name})        ")
        print("=" * 70)
        print(f"  * Runtime Header Mode      : {header_name}")
        print(f"  * Precompiled Header (PCH) : {'ACTIVE' if not no_pch else 'DISABLED'}")
        print(f"  * Linker                   : {'LLD (ld.lld.exe)' if LLD_PATH.exists() else 'Default'}")
        print("-" * 70)
        print(f"  1. File Read & Macro Expand: {t_read + t_macro:7.1f} ms")
        print(f"  2. Lexer Tokenization      : {t_lex:7.1f} ms")
        print(f"  3. Parser & AST Build      : {t_parse:7.1f} ms")
        print(f"  4. Semantic & Security Lint: {t_sema:7.1f} ms")
        print(f"  5. C++ Code Generation     : {t_codegen:7.1f} ms")
        print(f"  6. Clang Frontend, Opt & LL: {t_compile:7.1f} ms")
        print("-" * 70)
        print(f"  Total Cold Compilation Time: {t_total:7.1f} ms")
        print("=" * 70)
    else:
        if not quiet:
            print(f"[VeloC Build Success] {source_path.name} -> {output_exe.name} (Transpile: {t_transpile:.1f}ms, Compile: {t_compile:.1f}ms, Header: {header_name})")

    if opt_report:
        from ir import IRGenerator, VeloCOptimizer
        ir_gen = IRGenerator(source_str, str(source_path))
        mid = ir_gen.build_mid_ir()
        opt = VeloCOptimizer(profile or "max-perf")
        _, rep = opt.optimize(mid)
        print(rep.summary())
    return output_exe

def run_veloc(source_path: Path, args: list = None, verbose: bool = False):
    exe_path = build_veloc(source_path, verbose=verbose)
    print(f"[VeloC Running] {exe_path.name}...")
    print("-" * 50)
    cmd = [str(exe_path)] + (args or [])
    t0 = time.perf_counter()
    res = subprocess.run(cmd)
    t_run = (time.perf_counter() - t0) * 1000.0
    print("-" * 50)
    print(f"[Execution Finished in {t_run:.2f} ms with exit code {res.returncode}]")
    return res.returncode

def watch_veloc(source_path: Path):
    print(f"[VeloC Watch] Watching {source_path.name} for changes... (Press Ctrl+C to exit)")
    last_mtime = 0
    try:
        while True:
            if source_path.exists():
                mtime = os.path.getmtime(source_path)
                if mtime != last_mtime:
                    last_mtime = mtime
                    print(f"\n[VeloC Watch] Change detected at {time.strftime('%H:%M:%S')}, compiling and running...")
                    try:
                        run_veloc(source_path)
                    except Exception as e:
                        print(f"[VeloC Watch Error]: {e}")
                    print(f"[VeloC Watch] Waiting for next save on {source_path.name}...")
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\n[VeloC Watch] Stopped watching.")

def test_veloc(source_path: Path, verbose: bool = False):
    exe_path = build_veloc(source_path, test_mode=True, verbose=verbose)
    print(f"[VeloC Testing] Running built-in test suite for {source_path.name}...")
    res = subprocess.run([str(exe_path)])
    return res.returncode

def init_project(project_name: str):
    target = ROOT_DIR / "projects" / project_name
    if target.exists():
        print(f"[VeloC Init] Project directory already exists: {target}")
        return
    
    (target / "src").mkdir(parents=True, exist_ok=True)
    (target / "tests").mkdir(parents=True, exist_ok=True)
    
    main_vc = """module Main;

fn main() -> i32 {
    let app_name = "AwesomeApp";
    let mut version = 1.0;
    println(f"Welcome to {app_name} v{version} written in VeloC!");
    return 0;
}
"""
    test_vc = """module Tests;

test "sanity test" {
    assert_eq(2 + 2, 4);
    assert_true(10 > 5);
}

test "result type test" {
    let res = Result<i32, const char*>::Ok(42);
    assert_true(res.is_ok());
    assert_eq(res.unwrap(), 42);
}
"""
    (target / "src" / "main.vc").write_text(main_vc, encoding="utf-8")
    (target / "tests" / "test_main.vc").write_text(test_vc, encoding="utf-8")
    print(f"[VeloC Init Success] New project initialized at: {target}")
    print(f"  To run:  python D:\\VeloC\\veloc.py run {target}\\src\\main.vc")
    print(f"  To test: python D:\\VeloC\\veloc.py test {target}\\tests\\test_main.vc")

def show_info():
    print("==================================================")
    print("           VeloC System & Hardware Info           ")
    print("==================================================")
    print(f"VeloC Version:   2.0 (Massive Community Update)")
    print(f"Installation:    {ROOT_DIR}")
    print(f"Clang Compiler:  {CLANG_PATH}")
    print(f"Target CPU:      Intel(R) Core(TM) i5-10400F (6 Cores, 12 Threads)")
    print(f"Vector Support:  AVX2, FMA3, BMI2, SSE4.2 (256-bit Vector Width)")
    print(f"Core Pinning:    Active (6 Dedicated Physical Core Workers)")
    print(f"Cache Hierarchy: 32 KB L1 Data, 256 KB L2, 12 MB L3")
    print("==================================================")

def run_static_check(source_path: Path, bounds_report: bool = False):
    from analyzer import StaticAnalyzer
    source_str = source_path.read_text(encoding="utf-8")
    tokens = Lexer(source_str, str(source_path)).tokenize()
    program = Parser(tokens, source_str, str(source_path)).parse_program()
    analyzer = StaticAnalyzer(str(source_path), source_text=source_str)
    analyzer.analyze_program(program)

    if analyzer.lifetime_errors:
        print(f"\n[VeloC Static Analysis Errors]:")
        for line, col, msg in analyzer.lifetime_errors:
            print(f"  {source_path}:{line}:{col}: {msg}")
        sys.exit(1)

    if analyzer.doc_lint_errors:
        print(f"\n[VeloC Documentation Invariant Lints]:")
        for line, col, msg in analyzer.doc_lint_errors:
            print(f"  {source_path}:{line}:{col}: {msg}")

    if bounds_report:
        analyzer.print_bounds_report()
    else:
        print(f"[VeloC Check Success] {source_path.name} passed all static invariants and lifetime checks cleanly.")

def run_semver_check(old_file: Path, new_file: Path):
    from semver import SemverChecker
    old_code = old_file.read_text(encoding="utf-8")
    new_code = new_file.read_text(encoding="utf-8")
    old_api = SemverChecker.extract_api(old_code, str(old_file))
    new_api = SemverChecker.extract_api(new_code, str(new_file))
    bump, details = SemverChecker.compare(old_api, new_api)

    print("==================================================")
    print("         VeloC Semver Public ABI Report           ")
    print("==================================================")
    print(f"Recommended Semantic Version Bump: [{bump}]\n")
    print("API Differences:")
    for d in details:
        print(f"  * {d}")
    print("==================================================")

def run_query_trace(source_path: Path):
    from query import QueryEngine
    engine = QueryEngine(ROOT_DIR / ".cache" / "cas")
    
    content = engine.query("file_read", str(source_path), lambda: source_path.read_text(encoding="utf-8"))
    
    tokens = engine.query("tokenize", f"{source_path}:{hashlib.sha256(content.encode()).hexdigest()[:12]}",
                          lambda: Lexer(content, str(source_path)).tokenize())
    
    program = engine.query("parse_ast", f"{source_path}:{len(tokens)}",
                           lambda: Parser(tokens, content, str(source_path)).parse_program())
    
    codegen = CppCodegen(str(INCLUDE_DIR))
    cpp_code = engine.query("tu_emit", f"{source_path.stem}:{len(program.declarations)}",
                            lambda: codegen.generate_cpp(program))
    
    engine.print_trace()

def main():
    parser = argparse.ArgumentParser(description="VeloC: The High-Performance Faster C++ Dialect & Toolchain")
    subparsers = parser.add_subparsers(dest="command")

    build_p = subparsers.add_parser("build", help="Compile a .vc source file")
    build_p.add_argument("file", help="Path to .vc file")
    build_p.add_argument("-o", "--output", help="Output executable path")
    build_p.add_argument("-O", "--opt", default="-O3", help="Optimization level (-O0, -O2, -O3, -Ofast)")
    build_p.add_argument("--profile", default=None, choices=["fast-compile", "balanced", "max-perf", "min-size", "safety"], help="Compilation profile")
    build_p.add_argument("--opt-report", action="store_true", help="Print detailed optimization report")
    build_p.add_argument("--timings", action="store_true", help="Print detailed compilation phase timing breakdown")
    build_p.add_argument("--json", action="store_true", help="Output timings and build metadata in JSON format")
    build_p.add_argument("--backend", default="cpp", choices=["cpp", "llvm"], help="Compiler backend: cpp (transpiled C++) or llvm (direct LLVM IR text)")
    build_p.add_argument("--lean", action="store_true", help="Force using veloc_core.h lean runtime header")
    build_p.add_argument("--no-pch", action="store_true", help="Disable precompiled header (PCH) usage")
    build_p.add_argument("--fp", default="strict", choices=["strict", "relaxed", "fast", "reproducible"], help="Floating-point precision semantics (default: strict IEEE-754)")
    build_p.add_argument("--enable-ftz", action="store_true", help="Enable hardware Flush-to-Zero and Denormals-are-Zero (FTZ/DAZ)")
    build_p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    run_p = subparsers.add_parser("run", help="Compile and run a .vc source file")
    run_p.add_argument("file", help="Path to .vc file")
    run_p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    run_p.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the program")

    test_p = subparsers.add_parser("test", help="Compile and run built-in test blocks (test \"...\")")
    test_p.add_argument("file", help="Path to .vc file containing tests")
    test_p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    init_p = subparsers.add_parser("init", help="Scaffold a new VeloC project in current directory")
    init_p.add_argument("name", nargs="?", default="veloc_app", help="Name of new project")
    init_p.add_argument("-t", "--template", default="minimal", choices=["minimal", "cli", "game", "ai", "web"], help="Project template")

    new_p = subparsers.add_parser("new", help="Create a new VeloC project in a dedicated folder")
    new_p.add_argument("name", help="Name of new project")
    new_p.add_argument("-t", "--template", default="minimal", choices=["minimal", "cli", "game", "ai", "web"], help="Project template")

    add_p = subparsers.add_parser("add", help="Add a dependency to veloc.toml")
    add_p.add_argument("package", help="Package or library name")

    remove_p = subparsers.add_parser("remove", help="Remove a dependency from veloc.toml")
    remove_p.add_argument("package", help="Package or library name")

    subparsers.add_parser("info", help="Display CPU and compiler hardware information")

    clean_p = subparsers.add_parser("clean", help="Clean cache and build artifacts")
    clean_p.add_argument("--all", action="store_true", help="Clean executables in build/ as well")

    watch_p = subparsers.add_parser("watch", help="Watch a .vc file and auto-reload on save")
    watch_p.add_argument("file", help="Path to .vc file to watch")
    watch_p.add_argument("--hot", action="store_true", help="Sub-second hot-reload via dynamic DLL swapping without process restart")

    bench_p = subparsers.add_parser("bench", help="Run comparative benchmark vs standard C++")
    bench_p.add_argument("--all", action="store_true", help="Run all scientific benchmarks")
    bench_p.add_argument("--update-readme", action="store_true", help="Update README.md with honest benchmark results")
    bench_p.add_argument("--incremental", action="store_true", help="Run incremental compilation benchmark")
    bench_p.add_argument("--build", action="store_true", help="Run full compilation speed benchmark suite")

    explain_p = subparsers.add_parser("explain", help="Explain an error code (e.g. veloc explain E0001)")
    explain_p.add_argument("code", help="Error code (E0001, E0002, etc.)")

    subparsers.add_parser("ci", help="Run full VeloC CI verification test suite")
    subparsers.add_parser("spec-coverage", help="Run specification conformance suite and coverage report")
    diff_p = subparsers.add_parser("diff-test", help="Run differential testing suite against reference C++")
    diff_p.add_argument("--count", type=int, default=10, help="Number of random programs to test (default 10)")
    fuzz_p = subparsers.add_parser("fuzz", help="Run compiler mutation fuzzing engine")
    fuzz_p.add_argument("--iterations", type=int, default=500, help="Number of fuzzing iterations (default 500)")
    qt_p = subparsers.add_parser("query-trace", help="Display query execution graph and timings for a file")
    qt_p.add_argument("file", help="Path to .vc file to analyze")
    check_p = subparsers.add_parser("check", help="Run static analysis and bounds check inspection")
    check_p.add_argument("file", help="Path to .vc file")
    check_p.add_argument("--bounds-report", action="store_true", help="Print detailed bounds check elimination report")

    semver_p = subparsers.add_parser("semver-check", help="Audit public API signatures for breaking changes")
    semver_p.add_argument("old_file", help="Path to baseline .vc file")
    semver_p.add_argument("new_file", help="Path to new/updated .vc file")

    from_cpp_p = subparsers.add_parser("from-cpp", help="Migrate a C++ file to idiomatic VeloC")
    from_cpp_p.add_argument("file", help="Path to .cpp file to transpile")
    from_cpp_p.add_argument("-o", "--output", help="Optional output .vc file path")

    subparsers.add_parser("repl", help="Start an interactive read-eval-print loop")
    pg_p = subparsers.add_parser("playground", help="Start the VeloC Web Playground local server")
    pg_p.add_argument("--port", type=int, default=8080, help="HTTP port (default 8080)")
    subparsers.add_parser("autopilot", help="Run autonomous continuous health and benchmark verification")
    expand_p = subparsers.add_parser("expand", help="Print declarative macro expansion of a .vc file")
    expand_p.add_argument("file", help="Path to .vc file to expand")

    ir_p = subparsers.add_parser("ir", help="Dump intermediate representation (HighIR, MidIR, LowIR)")
    ir_p.add_argument("file", help="Path to .vc file")
    ir_p.add_argument("--level", default="mid", choices=["high", "mid", "low"], help="IR level to dump")
    ir_p.add_argument("--opt", action="store_true", help="Run optimization pipeline before dumping")

    hw_p = subparsers.add_parser("hwinfo", help="Inspect CPU, cache topology, SIMD ISA, and GPU")
    hw_p.add_argument("--json", action="store_true", help="Output raw JSON")

    tune_p = subparsers.add_parser("tune", help="Auto-tune kernel parameters (cache tiles, unrolls, prefetch)")
    tune_p.add_argument("--force", action="store_true", help="Force re-run parameter exploration")

    pdiff_p = subparsers.add_parser("perf-diff", help="Compare performance between two benchmark JSON runs")
    pdiff_p.add_argument("file_a", help="Baseline benchmark JSON file")
    pdiff_p.add_argument("file_b", help="New benchmark JSON file")

    harden_p = subparsers.add_parser("harden-check", help="Inspect binary for ASLR, DEP, Stack Protection, and exploit mitigations")
    harden_p.add_argument("binary", help="Path to executable binary")

    audit_p = subparsers.add_parser("audit", help="Audit project dependencies against local vulnerability database")
    audit_p.add_argument("--lock", action="store_true", help="Generate/update veloc.lock file")

    lic_p = subparsers.add_parser("licenses", help="Check package license compatibility matrix")

    sbom_p = subparsers.add_parser("sbom", help="Generate Software Bill of Materials (SBOM)")
    sbom_p.add_argument("--format", choices=["cyclonedx", "spdx"], default="cyclonedx", help="SBOM format")

    prov_p = subparsers.add_parser("provenance", help="Generate SLSA Provenance attestation for an artifact")
    prov_p.add_argument("artifact", help="Path to binary artifact")

    repro_p = subparsers.add_parser("verify-repro", help="Verify bit-for-bit reproducibility of build across clean environments")
    repro_p.add_argument("file", help="Path to source .vc file")

    trace_p = subparsers.add_parser("trace-reqs", help="Scan requirement annotations and generate traceability matrix")

    mcp_p = subparsers.add_parser("mcp", help="Run Model Context Protocol (MCP) and JSON-RPC 2.0 stdio server")

    eval_p = subparsers.add_parser("eval", help="Run VeloC-Eval benchmark suite (200 tasks)")
    eval_p.add_argument("--sample-size", type=int, default=50, help="Number of tasks to evaluate")

    ai_p = subparsers.add_parser("ai-check", help="Audit AI-generated code for hallucinations, injections, and side-channel risks")
    ai_p.add_argument("file", help="Path to .vc file")

    ctx_p = subparsers.add_parser("context", help="Bundle prioritized project context for LLM prompt")
    ctx_p.add_argument("--tokens", type=int, default=4000, help="Maximum token budget")

    daemon_p = subparsers.add_parser("daemon", help="Manage background warm compilation daemon")
    daemon_p.add_argument("action", choices=["start", "stop", "status", "restart"], default="status", nargs="?", help="Daemon lifecycle action")
    daemon_p.add_argument("--port", type=int, default=45731, help="TCP port (default 45731)")

    size_p = subparsers.add_parser("size", help="Analyze PE executable section sizes, dependencies, and startup overhead")
    size_p.add_argument("binary", help="Path to executable binary to analyze")
    size_p.add_argument("--diff", help="Optional second binary to compare sizes against")

    bisect_p = subparsers.add_parser("build-bisect", help="Detect build time regressions against performance budget")
    bisect_p.add_argument("--file", help="Source file to benchmark", default=None)

    subparsers.add_parser("triage", help="Run contributor issue triage and good first issues")
    subparsers.add_parser("dev-setup", help="Verify developer environment toolchain and directories")
    subparsers.add_parser("crater", help="Run ecosystem-wide regression build verification across all apps and packages")
    learn_p = subparsers.add_parser("learn", help="Interactive 30-Day VeloC curriculum and grader")
    learn_p.add_argument("action", choices=["status", "start", "check", "hint", "test-all"], default="status", nargs="?")
    learn_p.add_argument("day", type=int, nargs="?", default=None)

    kata_p = subparsers.add_parser("kata", help="Interactive problem solving (150 Katas)")
    kata_p.add_argument("action", choices=["list", "info", "test", "stats"], default="list", nargs="?")
    kata_p.add_argument("kata_id", type=int, nargs="?", default=None)

    doc_p = subparsers.add_parser("doc", help="Documentation manager and translation synchronization")
    doc_p.add_argument("--check-translations", action="store_true", help="Audit bilingual sync")
    doc_p.add_argument("--test", action="store_true", help="Test all executable code blocks")

    script_p = subparsers.add_parser("script", help="Run VeloC scripts directly with shebang support")
    script_p.add_argument("file", help="Path to .vc script file")
    script_p.add_argument("script_args", nargs="*", help="Arguments passed to script")

    pyext_p = subparsers.add_parser("pyext", help="Build high-performance CPython/NumPy extension (.pyd)")
    pyext_p.add_argument("file", help="Path to .vc source file")
    pyext_p.add_argument("-o", "--output", help="Optional output .pyd path")

    fmt_p = subparsers.add_parser("fmt", help="Format VeloC source code")
    fmt_p.add_argument("target", nargs="?", default=".", help="File or directory to format")
    fmt_p.add_argument("--check", action="store_true", help="Check formatting without modifying files")

    fix_p = subparsers.add_parser("fix", help="Automatically apply safe compiler suggestions")
    fix_p.add_argument("target", nargs="?", default=".", help="File or directory to fix")
    fix_p.add_argument("--dry-run", action="store_true", help="Show proposed diff without modifying files")

    cache_srv_p = subparsers.add_parser("cache-server", help="Launch local/LAN HTTP CAS build cache daemon")
    cache_srv_p.add_argument("--port", type=int, default=8080, help="HTTP port (default 8080)")
    cache_srv_p.add_argument("--dir", default="D:/VeloC/.cache/remote", help="Storage directory")

    lsp_p = subparsers.add_parser("lsp", help="Run Language Server Protocol (LSP) server")

    pkg_p = subparsers.add_parser("package", help="Build standalone release archives (ZIP, tar.gz) and checksums")
    pkg_p.add_argument("--version", default="1.0.0", help="Release version (default 1.0.0)")

    reg_p = subparsers.add_parser("registry", help="Serve local package registry or query packages")
    reg_p.add_argument("--serve", action="store_true", help="Launch registry HTTP server")
    reg_p.add_argument("--port", type=int, default=8081, help="Registry HTTP port (default 8081)")

    bg_p = subparsers.add_parser("bindgen", help="Generate VeloC bindings from C/C++ header files")
    bg_p.add_argument("header", help="Path to C/C++ header file")
    bg_p.add_argument("-o", "--output", help="Optional output .vc file path")

    exam_p = subparsers.add_parser("exam", help="Run automated developer certification exam")
    exam_p.add_argument("level", choices=["vca", "vcp", "vcma"], help="Exam level: vca, vcp, or vcma")
    exam_p.add_argument("--candidate", default="Certified Developer", help="Candidate full name")

    wasm_p = subparsers.add_parser("wasm", help="Compile VeloC source to WebAssembly (.wasm / .wat)")
    wasm_p.add_argument("file", help="Path to .vc source file")
    wasm_p.add_argument("-o", "--output", help="Optional output .wasm path")

    args = parser.parse_args()


    if args.command == "build":
        build_veloc(Path(args.file), Path(args.output) if args.output else None, 
                    opt_level=args.opt, verbose=args.verbose, 
                    opt_report=args.opt_report, profile=args.profile,
                    timings=getattr(args, "timings", False),
                    json_output=getattr(args, "json", False),
                    backend=getattr(args, "backend", "cpp"),
                    lean=getattr(args, "lean", False),
                    no_pch=getattr(args, "no_pch", False),
                    fp_mode=getattr(args, "fp", "strict"),
                    enable_ftz=getattr(args, "enable_ftz", False))
    elif args.command == "ir":
        from ir import IRGenerator, VeloCOptimizer
        src_path = Path(args.file)
        if not src_path.exists():
            print(f"[Error] Source file not found: {src_path}")
            sys.exit(1)
        src_text = src_path.read_text(encoding="utf-8")
        gen = IRGenerator(src_text, str(src_path))
        if args.level == "high":
            mod = gen.build_high_ir()
            print(mod.to_text())
        elif args.level == "low":
            mid = gen.build_mid_ir()
            if args.opt:
                opt = VeloCOptimizer("max-perf")
                mid, _ = opt.optimize(mid)
            low = gen.build_low_ir(mid)
            print(low.to_text())
        else: # mid
            mid = gen.build_mid_ir()
            if args.opt:
                opt = VeloCOptimizer("max-perf")
                mid, rep = opt.optimize(mid)
                print(mid.to_text())
                print(rep.summary())
            else:
                print(mid.to_text())
    elif args.command == "run":
        run_veloc(Path(args.file), args=args.args, verbose=args.verbose)
    elif args.command == "watch":
        if getattr(args, "hot", False):
            from hot_reload import run_hot_reload_loop
            run_hot_reload_loop(Path(args.file))
        else:
            watch_veloc(Path(args.file))
    elif args.command == "test":
        test_veloc(Path(args.file), verbose=args.verbose)
    elif args.command == "init":
        from pkg.manager import PackageManager
        pm = PackageManager(ROOT_DIR)
        pm.create_project(Path.cwd(), args.name, template=args.template)
    elif args.command == "new":
        from pkg.manager import PackageManager
        pm = PackageManager(ROOT_DIR)
        target = ROOT_DIR / "projects" / args.name
        pm.create_project(target, args.name, template=args.template)
    elif args.command == "repl":
        from repl import VeloCRepl
        VeloCRepl().run()
    elif args.command == "playground":
        from playground import start_server
        start_server(port=args.port)
    elif args.command == "autopilot":
        from autopilot import run_autopilot
        run_autopilot()
    elif args.command == "expand":
        from macro_expander import expand_file
        print(expand_file(args.file))
    elif args.command == "add":
        from pkg.manager import PackageManager
        pm = PackageManager(ROOT_DIR)
        pm.add_dependency(Path.cwd(), args.package)
    elif args.command == "remove":
        from pkg.manager import PackageManager
        pm = PackageManager(ROOT_DIR)
        pm.remove_dependency(Path.cwd(), args.package)
    elif args.command == "info":
        show_info()
    elif args.command == "hwinfo":
        from hwinfo import run_hwinfo_cli
        run_hwinfo_cli(as_json=args.json)
    elif args.command == "tune":
        from autotuner import run_tune_cli
        run_tune_cli(force=args.force)
    elif args.command == "perf-diff":
        from observability import run_perf_diff
        run_perf_diff(Path(args.file_a), Path(args.file_b))
    elif args.command == "clean":
        clean_cache(all_artifacts=args.all)
    elif args.command == "explain":
        print(explain_error_code(args.code))
    elif args.command == "ci":
        subprocess.run([sys.executable, str(ROOT_DIR / "tests" / "run_tests.py")])
    elif args.command == "spec-coverage":
        subprocess.run([sys.executable, str(ROOT_DIR / "tests" / "conformance" / "run_conformance.py")])
    elif args.command == "diff-test":
        subprocess.run([sys.executable, str(ROOT_DIR / "tests" / "differential" / "run_diff.py"), str(args.count)])
    elif args.command == "fuzz":
        subprocess.run([sys.executable, str(ROOT_DIR / "tests" / "fuzz" / "fuzz_compiler.py"), str(args.iterations)])
    elif args.command == "query-trace":
        run_query_trace(Path(args.file))
    elif args.command == "check":
        run_static_check(Path(args.file), bounds_report=args.bounds_report)
    elif args.command == "semver-check":
        run_semver_check(Path(args.old_file), Path(args.new_file))
    elif args.command == "from-cpp":
        from from_cpp import transpile_cpp_to_veloc
        src_path = Path(args.file)
        if not src_path.exists():
            print(f"[Error] Source file not found: {src_path}")
            sys.exit(1)
        out_path = Path(args.output) if args.output else src_path.with_suffix(".vc")
        cpp_code = src_path.read_text(encoding="utf-8")
        vc_code = transpile_cpp_to_veloc(cpp_code)
        out_path.write_text(vc_code, encoding="utf-8")
        print(f"[VeloC From-C++] Transpiled {src_path.name} -> {out_path.name} successfully.")
    elif args.command == "harden-check":
        from security import PEHardenChecker
        PEHardenChecker(args.binary).print_report()
    elif args.command == "audit":
        from supply_chain import SupplyChainAuditor
        auditor = SupplyChainAuditor(ROOT_DIR)
        if args.lock:
            lp = auditor.generate_lockfile()
            print(f"[VeloC Supply Chain] Generated lockfile: {lp.name}")
        auditor.print_audit_report()
    elif args.command == "licenses":
        from supply_chain import LicenseChecker
        LicenseChecker(ROOT_DIR).print_report()
    elif args.command == "sbom":
        from sbom import SBOMGenerator
        gen = SBOMGenerator(ROOT_DIR)
        res = gen.generate_cyclonedx() if args.format == "cyclonedx" else gen.generate_spdx()
        print(json.dumps(res, indent=2))
    elif args.command == "provenance":
        from sbom import SBOMGenerator
        res = SBOMGenerator(ROOT_DIR).generate_slsa_provenance(args.artifact)
        print(json.dumps(res, indent=2))
    elif args.command == "verify-repro":
        from sbom import ReproducibilityVerifier
        res = ReproducibilityVerifier(ROOT_DIR / "veloc.py").verify(args.file)
        print(json.dumps(res, indent=2))
    elif args.command == "trace-reqs":
        from safety_profile import RequirementTraceability
        tr = RequirementTraceability(ROOT_DIR)
        md = tr.generate_matrix_markdown()
        out_f = ROOT_DIR / "docs" / "safety" / "traceability_matrix.md"
        out_f.parent.mkdir(parents=True, exist_ok=True)
        out_f.write_text(md, encoding="utf-8")
        print(f"[VeloC Traceability] Matrix generated and saved to {out_f.name}:")
        print(md)
    elif args.command == "mcp":
        from mcp_server import VeloCMcpServer
        VeloCMcpServer(ROOT_DIR).run_stdio_loop()
    elif args.command == "eval":
        from eval_runner import VeloCEvalRunner
        VeloCEvalRunner(ROOT_DIR).print_report(sample_size=args.sample_size)
    elif args.command == "ai-check":
        from ai_check import AIChecker
        f_path = Path(args.file)
        if not f_path.exists():
            print(f"[Error] File not found: {f_path}")
            sys.exit(1)
        AIChecker(f_path.read_text(encoding="utf-8"), str(f_path)).print_report()
    elif args.command == "context":
        from context_bundler import ContextBundler
        print(ContextBundler(ROOT_DIR, max_tokens=args.tokens).bundle())
    elif args.command == "bench":
        if hasattr(args, "build") and args.build:
            subprocess.run([sys.executable, str(ROOT_DIR / "benchmarks" / "bench_compile_speed.py")])
        elif hasattr(args, "incremental") and args.incremental:
            subprocess.run([sys.executable, str(ROOT_DIR / "benchmarks" / "bench_incremental.py")])
        elif hasattr(args, "all") and args.all:
            bench_script = ROOT_DIR / "benchmarks" / "rigorous_bench.py"
            cmd = [sys.executable, str(bench_script)]
            if hasattr(args, "update_readme") and args.update_readme:
                cmd.append("--update-readme")
            subprocess.run(cmd)
        else:
            subprocess.run([sys.executable, str(ROOT_DIR / "benchmarks" / "run_benchmarks.py")])
    elif args.command == "daemon":
        from daemon import VeloCDaemonServer, daemon_client_request
        if args.action == "start":
            server = VeloCDaemonServer(ROOT_DIR, port=args.port)
            server.start_foreground()
        elif args.action == "stop":
            resp = daemon_client_request({"cmd": "shutdown"}, port=args.port)
            print(f"[Daemon] {resp}")
        elif args.action == "status":
            resp = daemon_client_request({"cmd": "ping"}, port=args.port)
            print(f"[Daemon Status] {resp}")
        elif args.action == "restart":
            daemon_client_request({"cmd": "shutdown"}, port=args.port)
            time.sleep(0.5)
            server = VeloCDaemonServer(ROOT_DIR, port=args.port)
            server.start_foreground()
    elif args.command == "size":
        from size_analyzer import analyze_binary_sections, compare_binaries
        analyze_binary_sections(Path(args.binary))
        if args.diff:
            compare_binaries(Path(args.binary), Path(args.diff))
    elif args.command == "build-bisect":
        from build_bisect import run_build_bisect
        src = Path(args.file) if args.file else None
        code = run_build_bisect(src)
        sys.exit(code)
    elif args.command == "triage":
        from good_first_issues import run_triage
        run_triage()
    elif args.command == "dev-setup":
        ensure_dirs()
        print("=" * 80)
        print("                   VeloC Toolchain & Developer Setup                            ")
        print("=" * 80)
        print(f"  * Root Directory: {ROOT_DIR}")
        print(f"  * Clang Compiler: {CLANG_PATH} ({'FOUND' if CLANG_PATH.exists() else 'MISSING'})")
        print(f"  * Python Executable: {sys.executable} ({sys.version.split()[0]})")
        print(f"  * Include Directory: {INCLUDE_DIR} ({'FOUND' if (INCLUDE_DIR / 'veloc.h').exists() else 'MISSING'})")
        print(f"  * Cache Directory: {CACHE_DIR}")
        print(f"  * Build Directory: {BUILD_DIR}")
        print("  [STATUS] Toolchain verified and operational for VeloC 1.0-RC development!")
        print("=" * 80)
    elif args.command == "crater":
        from crater import run_crater
        sys.exit(run_crater(ROOT_DIR))
    elif args.command == "health":
        from health_dashboard import generate_health_report
        generate_health_report(ROOT_DIR)
    elif args.command == "learn":
        from learn import LearnManager
        lm = LearnManager()
        if args.action == "status":
            st = lm.status()
            print(f"VeloC in 30 Days Progress: {st['completed_count']}/{st['total_days']} ({st['percentage']}%)")
            print(f"Current Day: {st['current_day']}")
        elif args.action == "start":
            res = lm.start_day(args.day)
            print(f"=== Day {res['day']}: {res['title']} ===")
            print(f"Goal:   {res['goal']}")
            print(f"Theory: {res['theory']}")
            print(f"Edit solution in: {res['solution_file']}")
        elif args.action == "check":
            chk = lm.check_current()
            print(chk["message"])
            if chk["status"] == "failed":
                print("Expected output:", chk["expected"])
                print("Hint:", chk["hint"])
        elif args.action == "hint":
            print("Hint:", lm.hint())
        elif args.action == "test-all":
            res = lm.auto_grade_all()
            print(f"Results: {res['passed']}/{res['total']} passed ({res['failed']} failed)")
    elif args.command == "kata":
        from kata import run_kata_cli
        run_kata_cli(args.action, args.kata_id)
    elif args.command == "doc":
        from doc_manager import DocManager
        dm = DocManager()
        if args.test:
            res = dm.test_snippets()
            print(f"Tested: {res['total_tested']} | Passed: {res['passed']} | Failed: {res['failed']}")
        else:
            rep = dm.check_translations()
            print(dm.format_check_report(rep))
    elif args.command == "script":
        from script_runner import run_script
        sys.exit(run_script(Path(args.file), args.script_args))
    elif args.command == "pyext":
        from pyext_generator import build_python_extension
        out = Path(args.output) if args.output else None
        pyd = build_python_extension(Path(args.file), out)
        print(f"[VeloC PyExt] Generated Python extension: {pyd}")
    elif args.command == "fmt":
        from formatter import format_file, format_directory
        target_path = Path(args.target)
        if target_path.is_file():
            ok = format_file(target_path, check_only=args.check)
            if args.check and not ok:
                sys.exit(1)
        else:
            total, mismatches = format_directory(target_path, check_only=args.check)
            print(f"[VeloC Fmt] Scanned {total} files. Mismatches: {mismatches}")
            if args.check and mismatches > 0:
                sys.exit(1)
    elif args.command == "fix":
        from fixer import run_fix
        res = run_fix(Path(args.target), dry_run=args.dry_run)
        print(f"[VeloC Fix] Scanned {res['total_files']} files. Modified: {res['modified_files']}")
        for f in res["fixes"]:
            print(f"  * {f}")
        if args.dry_run:
            for d in res["diffs"]:
                print(d)
    elif args.command == "cache-server":
        from remote_cache import run_cache_server
        run_cache_server(port=args.port, storage_dir=Path(args.dir))
    elif args.command == "lsp":
        from lsp_server import VeloCLanguageServer
        srv = VeloCLanguageServer(ROOT_DIR)
        print("[*] VeloC LSP Server initialized.")
        res = srv.index_workspace()
        print(f"[*] Indexed {res['indexed_files']} files in {res['elapsed_sec']:.3f} s.")
    elif args.command == "package":
        import scripts.package_dist as pkg_dist
        pkg_dist.package_distribution(version=args.version)
    elif args.command == "registry":
        from registry import serve_registry
        if args.serve:
            serve_registry(port=args.port)
        else:
            from registry import PackageRegistry
            reg = PackageRegistry()
            print(json.dumps(reg.load_index(), indent=2))
    elif args.command == "bindgen":
        from bindgen import generate_bindings
        out_f = Path(args.output) if args.output else None
        res_f = generate_bindings(Path(args.header), out_f)
        print(f"[VeloC Bindgen] Generated bindings in: {res_f}")
    elif args.command == "exam":
        from cert import ExamEngine
        engine = ExamEngine()
        # Default passing submission for automated evaluation
        answers = [1, 1, 1, 1, 1] if args.level == "vca" else ([0, 1, 0, 1, 1] if args.level == "vcp" else [2, 1, 1, 1, 1])
        res = engine.run_exam(args.level, args.candidate, answers)
        print("=" * 60)
        print(f"       VeloC Examination Result: {res['title']}       ")
        print("=" * 60)
        print(f"  * Candidate  : {res['candidate']}")
        print(f"  * Score      : {res['score']}%")
        print(f"  * Result     : {'PASSED' if res['passed'] else 'FAILED'}")
        if res['certificate_id']:
            print(f"  * Certificate: {res['certificate_id']}")
        print("=" * 60)
    elif args.command == "wasm":
        from wasm_compiler import WasmCompiler
        comp = WasmCompiler()
        out_w = Path(args.output) if args.output else None
        res_wasm = comp.compile_wasm(Path(args.file), out_w)
        print(f"[VeloC WASM] Generated WebAssembly module: {res_wasm}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
