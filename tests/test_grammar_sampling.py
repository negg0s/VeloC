import unittest
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from lexer import Lexer
from parser import Parser


class TestGrammarSampling(unittest.TestCase):
    def generate_random_valid_program(self, seed: int) -> str:
        rng = random.Random(seed)
        types = ["i32", "i64", "f32", "bool"]
        funcs = []

        for f_idx in range(rng.randint(2, 5)):
            ret_t = rng.choice(types)
            fn_name = f"func_{f_idx}"
            statements = []
            for s_idx in range(rng.randint(1, 4)):
                var_name = f"var_{s_idx}"
                v_type = rng.choice(types)
                val = str(rng.randint(1, 100)) if v_type != "bool" else "true"
                statements.append(f"    let {var_name}: {v_type} = {val};")

            ret_val = "0" if ret_t in ("i32", "i64") else ("1.0" if ret_t == "f32" else "true")
            statements.append(f"    return {ret_val};")
            body = "\n".join(statements)
            funcs.append(f"fn {fn_name}() -> {ret_t} {{\n{body}\n}}")

        program_code = "module SampledProgram;\n\n" + "\n\n".join(funcs) + "\n"
        return program_code

    def test_grammar_samples_parse_cleanly(self):
        """Verify that 20 randomly sampled programs conforming to the grammar parse with 0 errors."""
        for seed in range(20):
            code = self.generate_random_valid_program(seed)
            tokens = Lexer(code, f"<seed_{seed}>").tokenize()
            parser = Parser(tokens, code, f"<seed_{seed}>")
            prog = parser.parse_program()
            self.assertIsNotNone(prog)
            self.assertGreater(len(prog.declarations), 0)

if __name__ == '__main__':
    unittest.main()
