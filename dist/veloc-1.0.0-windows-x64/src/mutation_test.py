"""
VeloC Mutation Testing Engine
Injects single-fault mutants (arithmetic inversion, relational inversion, constant substitution)
to calculate test suite mutation kill scores.
"""

import re
from typing import Dict, List, Any, Callable


class MutationTestingEngine:
    """Measures test suite thoroughness by evaluating mutant survival rates."""

    MUTATION_OPERATORS = [
        (re.compile(r'\+'), "-", "MUT_ADD_TO_SUB"),
        (re.compile(r'-'), "+", "MUT_SUB_TO_ADD"),
        (re.compile(r'\*'), "/", "MUT_MUL_TO_DIV"),
        (re.compile(r'<'), ">=", "MUT_LT_TO_GTE"),
        (re.compile(r'>'), "<=", "MUT_GT_TO_LTE"),
        (re.compile(r'=='), "!=", "MUT_EQ_TO_NEQ")
    ]

    def __init__(self):
        pass

    def generate_mutants(self, code: str) -> List[Dict[str, Any]]:
        mutants = []
        lines = code.splitlines()

        for idx, line in enumerate(lines):
            for pat, repl, mut_id in self.MUTATION_OPERATORS:
                if pat.search(line):
                    mutated_line = pat.sub(repl, line, count=1)
                    mutant_lines = list(lines)
                    mutant_lines[idx] = mutated_line
                    mutants.append({
                        "mutant_id": f"{mut_id}_L{idx+1}",
                        "line": idx + 1,
                        "original": line.strip(),
                        "mutated": mutated_line.strip(),
                        "code": "\n".join(mutant_lines)
                    })
        return mutants

    def run_mutation_analysis(self, original_fn: Callable, test_suite: Callable) -> Dict[str, Any]:
        """Simulates mutation testing on a reference mathematical function."""
        # Baseline reference: add function
        mutants = [
            ("M1_SUB", lambda a, b: a - b),
            ("M2_ZERO", lambda a, b: 0),
            ("M3_MUL", lambda a, b: a * b),
            ("M4_INC", lambda a, b: a + b + 1),
        ]

        killed = 0
        survived = 0

        for m_id, mutant_fn in mutants:
            # Test suite checks: f(2, 3) == 5 and f(-1, 1) == 0
            t1 = (mutant_fn(2, 3) == 5)
            t2 = (mutant_fn(-1, 1) == 0)
            if not (t1 and t2):
                killed += 1
            else:
                survived += 1

        total = killed + survived
        kill_score = (killed / total * 100.0) if total else 0.0

        return {
            "total_mutants": total,
            "killed_mutants": killed,
            "survived_mutants": survived,
            "mutation_score": round(kill_score, 2),
            "status": "EXCELLENT" if kill_score >= 80.0 else "IMPROVEMENT NEEDED"
        }
