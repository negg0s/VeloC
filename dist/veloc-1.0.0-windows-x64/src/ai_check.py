"""
VeloC AI-Check: Automated Security & Correctness Auditor for AI-Generated Code
Audits code produced by LLMs for hallucinations, prompt injections, secret timing leaks,
capability violations, and generates auto-remediation patches.
"""

import re
from pathlib import Path
from typing import Dict, List, Any


class AIChecker:
    """Deep inspection engine for AI-generated VeloC snippets."""

    HALLUCINATION_PATTERNS = [
        (re.compile(r'\.push_back\s*\('), ".push()", "LLM hallucinated C++ std::vector::push_back instead of VeloC .push()"),
        (re.compile(r'\bstd::cout\s*<<'), "println()", "LLM hallucinated C++ std::cout instead of VeloC println()"),
        (re.compile(r'println!\s*\('), "println()", "LLM hallucinated Rust println! macro instead of VeloC println()"),
        (re.compile(r'const\s+let\s+'), "let ", "LLM hallucinated 'const let'; VeloC variables are immutable by default"),
        (re.compile(r'\.size\(\)'), ".len()", "Notice: VeloC native collections use .len() or .size()")
    ]

    INJECTION_PATTERNS = [
        re.compile(r'ignore\s+previous\s+instructions', re.IGNORECASE),
        re.compile(r'system\s*\(\s*["\']cmd\.exe', re.IGNORECASE),
        re.compile(r'powershell\s+-enc', re.IGNORECASE),
        re.compile(r'<system>', re.IGNORECASE),
        re.compile(r'\[SYSTEM_PROMPT\]', re.IGNORECASE)
    ]

    def __init__(self, source_code: str, filename: str = "<ai_generated>"):
        self.source = source_code
        self.filename = filename

    def analyze(self) -> Dict[str, Any]:
        issues = []
        remediated_code = self.source

        # 1. Check for prompt injection markers
        for pat in self.INJECTION_PATTERNS:
            if pat.search(self.source):
                issues.append({
                    "type": "PROMPT_INJECTION_RISK",
                    "severity": "CRITICAL",
                    "message": f"Suspicious prompt injection marker or unauthorized shell invocation matching: {pat.pattern}"
                })

        # 2. Check for common LLM syntax hallucinations
        for pat, replacement, msg in self.HALLUCINATION_PATTERNS:
            matches = list(pat.finditer(self.source))
            if matches:
                issues.append({
                    "type": "AI_SYNTAX_HALLUCINATION",
                    "severity": "HIGH",
                    "message": msg,
                    "occurrences": len(matches)
                })
                remediated_code = pat.sub(replacement, remediated_code)

        # 3. Secret timing leaks
        from src.security import SecretBranchLinter
        linter = SecretBranchLinter(self.source, self.filename)
        secret_warnings = linter.lint()
        for sw in secret_warnings:
            issues.append({
                "type": "TIMING_SIDE_CHANNEL",
                "severity": "HIGH",
                "line": sw["line"],
                "message": sw["message"]
            })

        # 4. Capability violations
        from src.security import CapabilitySecurity
        cap_sec = CapabilitySecurity()
        cap_sec.allowed_caps = {"time.now", "rng.secure"}
        cap_sec.denied_caps = {"proc.exec"}
        cap_violations = cap_sec.verify_source(self.source, self.filename)
        for cv in cap_violations:
            issues.append({
                "type": "CAPABILITY_VIOLATION",
                "severity": "HIGH",
                "message": cv["message"]
            })

        # Calculate overall risk score
        critical_count = sum(1 for i in issues if i["severity"] == "CRITICAL")
        high_count = sum(1 for i in issues if i["severity"] == "HIGH")

        if critical_count > 0:
            risk = "CRITICAL (Rejection Advised)"
        elif high_count >= 2:
            risk = "HIGH (Requires Auto-Remediation)"
        elif high_count == 1:
            risk = "MEDIUM (Review Recommended)"
        else:
            risk = "LOW (Safe for Execution)"

        return {
            "filename": self.filename,
            "risk_level": risk,
            "total_issues": len(issues),
            "issues": issues,
            "has_remediation": remediated_code != self.source,
            "remediated_code": remediated_code
        }

    def print_report(self):
        res = self.analyze()
        print("=" * 80)
        print("                 VeloC AI-Check: AI Code Safety & Quality Audit         ")
        print("=" * 80)
        print(f"  Target File:       {res['filename']}")
        print(f"  Risk Evaluation:   {res['risk_level']}")
        print(f"  Detected Issues:   {res['total_issues']}")
        print("-" * 80)
        if not res["issues"]:
            print("  [PASSED] Code is free of AI hallucinations and security vulnerabilities.")
        else:
            for iss in res["issues"]:
                print(f"  [{iss['severity']}] {iss['type']}: {iss['message']}")
        if res["has_remediation"]:
            print("-" * 80)
            print("  [AUTO-REMEDIATION PROPOSED]: Corrected hallucinated method signatures.")
        print("=" * 80)
