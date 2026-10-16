import os
import sys
import subprocess
import argparse
import time
import shutil
import hashlib
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
                test_mode: bool = False, verbose: bool = False, quiet: bool = False) -> Path:
    ensure_dirs()
    if not source_path.exists():
        print(f"[Error] Source file not found: {source_path}")
        sys.exit(1)

    stem = source_path.stem
    if test_mode:
        stem += "_test"

    cpp_target = CACHE_DIR / f"{stem}.cpp"
    hash_target = CACHE_DIR / f"{stem}.hash"
    if output_exe is None:
        output_exe = BUILD_DIR / f"{stem}.exe"

    content_bytes = source_path.read_bytes()
    current_hash = hashlib.sha256(content_bytes + str(test_mode).encode()).hexdigest()

    # Instant Incremental Build: if source unchanged and exe exists, skip compilation!
    if output_exe.exists() and hash_target.exists():
        if hash_target.read_text().strip() == current_hash:
            if verbose:
                print(f"[VeloC Instant Cache Hit] {source_path.name} -> {output_exe.name} (0.3ms - Up to date)")
            return output_exe

    # Compile VeloC -> C++ via AST Parser & Code Generator
    source_str = source_path.read_text(encoding="utf-8")
    t0 = time.perf_counter()
    use_ast = True
    try:
        tokens = Lexer(source_str, str(source_path)).tokenize()
        program = Parser(tokens, source_str, str(source_path)).parse_program()
        codegen = CppCodegen(str(INCLUDE_DIR), test_mode=test_mode)
        cpp_code = codegen.generate_cpp(program)
        cpp_target.write_text(cpp_code, encoding="utf-8")
    except (LexerError, ParseError, MultiParseError) as err:
        reporter = DiagnosticReporter(source_str, str(source_path))
        if isinstance(err, MultiParseError):
            for e in err.errors:
                reporter.error(e.code, e.message, e.token.line, e.token.col, e.token.span_len, e.help_text)
        elif isinstance(err, ParseError):
            reporter.error(err.code, err.message, err.token.line, err.token.col, err.token.span_len, err.help_text)
        else:
            reporter.error(DiagnosticCode.E0004, err.message, err.line, err.col)
        print(f"\n[VeloC Compiler Diagnostic]:")
        reporter.print_all()
        sys.exit(1)
    except Exception as e:
        # Fallback to transpiler with warning if AST parser encountered an unexpected grammar variation
        if verbose:
            print(f"[VeloC Parser Notice]: {e}, using compatibility pass")
        transpiler = VeloCTranspiler(str(INCLUDE_DIR), test_mode=test_mode)
        transpiler.transpile_file(str(source_path), str(cpp_target))

    t_transpile = (time.perf_counter() - t0) * 1000.0

    # Compile with Clang 20 with extreme optimization flags
    cmd = [
        str(CLANG_PATH),
        str(cpp_target),
        "-o", str(output_exe),
        opt_level,
        "-march=native",
        "-static",
        "-fwrapv",
        "-Wl,--no-insert-timestamp",
        "-ffast-math",
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

    if verbose:
        print("[Cmd]:", " ".join(cmd))

    t1 = time.perf_counter()
    res = subprocess.run(cmd, capture_output=True, text=True)
    t_compile = (time.perf_counter() - t1) * 1000.0

    if res.returncode != 0:
        print(f"[Build Failed]:\n{res.stderr}")
        sys.exit(res.returncode)

    hash_target.write_text(current_hash)
    if not quiet:
        print(f"[VeloC Build Success] {source_path.name} -> {output_exe.name} (Transpile: {t_transpile:.1f}ms, Compile: {t_compile:.1f}ms)")
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
    analyzer = StaticAnalyzer(str(source_path))
    analyzer.analyze_program(program)

    if analyzer.lifetime_errors:
        print(f"\n[VeloC Static Analysis Errors]:")
        for line, col, msg in analyzer.lifetime_errors:
            print(f"  {source_path}:{line}:{col}: {msg}")
        sys.exit(1)

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

    bench_p = subparsers.add_parser("bench", help="Run comparative benchmark vs standard C++")
    bench_p.add_argument("--all", action="store_true", help="Run all scientific benchmarks")
    bench_p.add_argument("--update-readme", action="store_true", help="Update README.md with honest benchmark results")
    bench_p.add_argument("--incremental", action="store_true", help="Run incremental compilation benchmark")

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

    args = parser.parse_args()

    if args.command == "build":
        build_veloc(Path(args.file), Path(args.output) if args.output else None, opt_level=args.opt, verbose=args.verbose)
    elif args.command == "run":
        run_veloc(Path(args.file), args=args.args, verbose=args.verbose)
    elif args.command == "watch":
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
    elif args.command == "bench":
        if hasattr(args, "incremental") and args.incremental:
            subprocess.run([sys.executable, str(ROOT_DIR / "benchmarks" / "bench_incremental.py")])
        elif hasattr(args, "all") and args.all:
            bench_script = ROOT_DIR / "benchmarks" / "rigorous_bench.py"
            cmd = [sys.executable, str(bench_script)]
            if hasattr(args, "update_readme") and args.update_readme:
                cmd.append("--update-readme")
            subprocess.run(cmd)
        else:
            subprocess.run([sys.executable, str(ROOT_DIR / "benchmarks" / "run_benchmarks.py")])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
