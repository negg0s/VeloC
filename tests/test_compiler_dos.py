import unittest
import time
from src.macro_expander import MacroExpander

class TestCompilerDoSRobustness(unittest.TestCase):
    def test_recursive_macro_bomb_defense(self):
        bomb = '''
        macro_rules! bomb {
            () => { bomb!() };
        }
        bomb!();
        '''
        expander = MacroExpander()
        t0 = time.perf_counter()
        with self.assertRaises(RecursionError) as ctx:
            expander.expand_source(bomb, max_depth=32)
        elapsed = time.perf_counter() - t0

        self.assertIn("E0901", str(ctx.exception))
        self.assertLess(elapsed, 0.5, "Compiler must abort macro explosion in <0.5s")

    def test_giant_literal_size_limit(self):
        # 20 MB code string
        huge_code = "let x = \"" + ("A" * (20 * 1024 * 1024)) + "\";"
        expander = MacroExpander()
        t0 = time.perf_counter()
        with self.assertRaises(ValueError) as ctx:
            expander.expand_source(huge_code)
        elapsed = time.perf_counter() - t0

        self.assertIn("E0903", str(ctx.exception))
        self.assertLess(elapsed, 0.2, "Compiler must reject oversized literal in <0.2s")

    def test_nested_brackets_depth_limit(self):
        # 500 levels of nested parentheses
        nested = "(" * 500 + "42" + ")" * 500
        from src.security import SafeInputGuard
        is_safe = SafeInputGuard.validate_json_depth(nested, max_depth=64)
        self.assertFalse(is_safe, "Deeply nested brackets (>64) must be flagged")

if __name__ == '__main__':
    unittest.main()
