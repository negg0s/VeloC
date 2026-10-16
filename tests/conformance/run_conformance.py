# VeloC Specification Conformance & Coverage Verification Tool
import os
import re
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
SPEC_DIR = ROOT_DIR / "docs" / "spec"
TESTS_DIR = ROOT_DIR / "tests" / "conformance"

def extract_spec_rules():
    rules = {}
    rule_re = re.compile(r'(RULE-[A-Z]+-\d+)(?::\s*([^\n\r]+))?')
    for file in SPEC_DIR.glob("*.*"):
        content = file.read_text(encoding="utf-8")
        for match in rule_re.finditer(content):
            rule_id = match.group(1)
            desc = match.group(2) or "Core specification invariant"
            if rule_id not in rules:
                rules[rule_id] = (desc.strip(), file.name)
    return rules

def extract_test_coverage():
    covered = {}
    rule_re = re.compile(r'RULE-[A-Z]+-\d+')
    for file in TESTS_DIR.glob("*.vc"):
        content = file.read_text(encoding="utf-8")
        for match in rule_re.finditer(content):
            rule_id = match.group(0)
            if rule_id not in covered:
                covered[rule_id] = []
            covered[rule_id].append(file.name)
    return covered

def main():
    print("==================================================")
    print("      VeloC Specification Conformance Matrix      ")
    print("==================================================")
    
    rules = extract_spec_rules()
    coverage = extract_test_coverage()
    
    total_rules = len(rules)
    covered_rules = 0
    
    print(f"{'Rule ID':<16} {'Spec File':<22} {'Status':<10} {'Test Target'}")
    print("-" * 75)
    
    for rule_id in sorted(rules.keys()):
        desc, spec_file = rules[rule_id]
        if rule_id in coverage:
            covered_rules += 1
            test_files = ", ".join(sorted(set(coverage[rule_id])))
            status = "\033[32mCOVERED\033[0m"
            print(f"{rule_id:<16} {spec_file:<22} {status:<19} {test_files}")
        else:
            status = "\033[33mPENDING\033[0m"
            print(f"{rule_id:<16} {spec_file:<22} {status:<19} [None]")
            
    pct = (covered_rules / total_rules * 100.0) if total_rules > 0 else 0.0
    print("-" * 75)
    print(f"Total Rules Defined: {total_rules}")
    print(f"Rules with Conformance Tests: {covered_rules} ({pct:.1f}% specification coverage)")
    
    print("\nRunning All Conformance Test Suites...")
    passed = 0
    failed = 0
    test_files = sorted(list(TESTS_DIR.glob("*.vc")))
    for tf in test_files:
        cmd = [sys.executable, str(ROOT_DIR / "veloc.py"), "run", str(tf)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  \033[32m[PASS]\033[0m {tf.name:<30} 100% assertions verified")
            passed += 1
        else:
            print(f"  \033[31m[FAIL]\033[0m {tf.name:<30} Exit code: {res.returncode}")
            failed += 1
            
    print(f"\nConformance Results: {passed} suites passed, {failed} failed.")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
