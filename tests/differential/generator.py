import random
from typing import List

class VeloCProgramGenerator:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.var_count = 0

    def fresh_var(self) -> str:
        self.var_count += 1
        return f"v_{self.var_count}"

    def gen_arith_expr(self, depth: int = 0) -> str:
        if depth >= 3 or self.rng.random() < 0.4:
            return str(self.rng.randint(1, 50))
        op = self.rng.choice(["+", "-", "*", "%", "^", "&", "|"])
        left = self.gen_arith_expr(depth + 1)
        right = self.gen_arith_expr(depth + 1)
        # Avoid division or modulo by 0
        if op in ("/", "%"):
            right = f"({right} + 1)"
        return f"({left} {op} {right})"

    def gen_program(self) -> str:
        lines: List[str] = [
            "// Auto-generated Differential Test for VeloC",
            "#include <veloc.h>",
            "#include <cstdio>",
            "#include <cstdint>",
            "",
            "fn compute_checksum() -> i64 {",
            "    let mut checksum: i64 = 0;",
        ]

        # Generate local variables with arithmetic
        num_vars = self.rng.randint(3, 8)
        vars = []
        for _ in range(num_vars):
            vname = self.fresh_var()
            expr = self.gen_arith_expr()
            lines.append(f"    let {vname}: i64 = {expr};")
            lines.append(f"    checksum = (checksum * 31 + {vname}) ^ 0x5bf03635;")
            vars.append(vname)

        # Generate a loop
        lines.append("    let mut loop_acc: i64 = 0;")
        limit = self.rng.randint(5, 20)
        lines.append(f"    for (int i = 0; i < {limit}; ++i) {{")
        chosen_var = self.rng.choice(vars)
        lines.append(f"        loop_acc = (loop_acc + i * {chosen_var}) & 0x7FFFFFFF;")
        lines.append("    }")
        lines.append("    checksum = (checksum ^ loop_acc) * 17;")

        # Generate match expression
        lines.append("    let match_in: i32 = (checksum % 5 + 5) % 5;")
        lines.append("    let match_res: i64 = match (match_in) {")
        lines.append("        0 => 101,")
        lines.append("        1 => 202,")
        lines.append("        2 => 303,")
        lines.append("        _ => 404")
        lines.append("    };")
        lines.append("    checksum = checksum + match_res;")

        # Generate if-let Option unwrap
        lines.append("    let opt_val = Option<i64>::Some(checksum % 1000);")
        lines.append("    if let val = opt_val {")
        lines.append("        checksum = checksum + val * 3;")
        lines.append("    }")

        lines.append("    return checksum;")
        lines.append("}")
        lines.append("")
        lines.append("fn main() -> i32 {")
        lines.append("    let cs = compute_checksum();")
        lines.append('    printf("CHECKSUM=%lld\\n", (long long)cs);')
        lines.append("    return 0;")
        lines.append("}")
        return "\n".join(lines) + "\n"
