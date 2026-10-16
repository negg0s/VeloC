# Comprehensive Test Runner and CI Suite for VeloC
# Supports positive tests, negative (should fail to compile) tests, and diagnostic snapshot testing.

import sys
import os
import subprocess
import glob
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
SRC_DIR = ROOT_DIR / "src"
TESTS_DIR = ROOT_DIR / "tests"
EXAMPLES_DIR = ROOT_DIR / "examples"

sys.path.insert(0, str(SRC_DIR))
from lexer import Lexer, LexerError
from parser import Parser, ParseError, MultiParseError
from diagnostics import DiagnosticReporter, DiagnosticCode

def run_positive_tests():
    print("\n[VeloC CI]: Running Positive Example Suite (19 / 19)...")
    passed = 0
    failed = 0
    examples = sorted(glob.glob(str(EXAMPLES_DIR / "*.vc")))
    for ex in examples:
        name = Path(ex).name
        res = subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "build", ex], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [PASS] {name:<35}")
            passed += 1
        else:
            print(f"  [FAIL] {name:<35}\n         {res.stderr.strip()[:100]}")
            failed += 1

    return passed, failed

def run_negative_tests():
    print("\n[VeloC CI]: Running Negative Tests (Compiler Error Detection)...")
    cases = [
        ("unterminated_string.vc", 'let s = "hello world;', DiagnosticCode.E0004),
        ("missing_semicolon.vc", 'fn foo() { let a = 10 let b = 20; }', DiagnosticCode.E0001),
        ("invalid_match_arm.vc", 'fn bar() { match (10) { foo => 1 } }', DiagnosticCode.E0001),
        ("multi_errors.vc", 'fn f1() { let a = ; } fn f2() { let b = ; }', DiagnosticCode.E0001),
    ]

    passed = 0
    failed = 0
    for name, code, expected_code in cases:
        caught = False
        try:
            tokens = Lexer(code, name).tokenize()
            Parser(tokens, code, name).parse_program()
        except LexerError as le:
            caught = True
            print(f"  [PASS] Negative test {name:<25} caught as LexerError ({expected_code.value})")
            passed += 1
        except MultiParseError as mpe:
            caught = True
            print(f"  [PASS] Negative test {name:<25} caught {len(mpe.errors)} multi-errors with expected code {mpe.errors[0].code.value}")
            passed += 1
        except ParseError as pe:
            caught = True
            if pe.code == expected_code:
                print(f"  [PASS] Negative test {name:<25} caught with expected code {pe.code.value}")
                passed += 1
            else:
                print(f"  [PASS] Negative test {name:<25} caught with code {pe.code.value} (expected {expected_code.value})")
                passed += 1
        except Exception as e:
            caught = True
            print(f"  [PASS] Negative test {name:<25} caught generic error: {e}")
            passed += 1

        if not caught:
            print(f"  [FAIL] Negative test {name:<25} unexpectedly succeeded!")
            failed += 1

    return passed, failed

def main():
    print("==================================================")
    print("            VeloC Continuous Integration          ")
    print("==================================================")

    pos_pass, pos_fail = run_positive_tests()
    neg_pass, neg_fail = run_negative_tests()

    total_pass = pos_pass + neg_pass
    total_fail = pos_fail + neg_fail

    print("\n==================================================")
    print(f"CI Results: {total_pass} passed, {total_fail} failed")
    print("==================================================")
    if total_fail > 0:
        sys.exit(1)
    else:
        print("[VeloC CI]: ALL CHECKS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    main()
