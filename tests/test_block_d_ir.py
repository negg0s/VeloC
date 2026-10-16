"""
Unit tests for VeloC Stage 5 Block D: Multi-Level IR & Custom Optimizer
"""

import unittest
import sys
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
sys.path.insert(0, str(ROOT_DIR / "src"))

from ir import (
    IRGenerator, VeloCOptimizer, OptReport,
    HighIRModule, MidIRModule, LowIRModule,
    BasicBlock, MidInstruction
)

class TestBlockDIR(unittest.TestCase):
    def setUp(self):
        self.sample_code = """
        fn square(x: f32) -> f32 {
            return x * x;
        }

        fn process_matrix(mat: Mat<f32, 4, 4>) -> f32 {
            for i in 0..16 {
                let v = mat[i];
            }
            return 0.0;
        }

        fn main() -> i32 {
            let res = square(5.0);
            return 0;
        }
        """
        self.gen = IRGenerator(self.sample_code, "test_sample.vc")

    def test_high_ir(self):
        high = self.gen.build_high_ir()
        self.assertIn("square", high.functions)
        self.assertIn("process_matrix", high.functions)
        self.assertIn("main", high.functions)
        text = high.to_text()
        self.assertIn("; HighIR Module", text)
        self.assertIn("fn square(x: f32) -> f32", text)

    def test_mid_ir_ssa_cfg(self):
        mid = self.gen.build_mid_ir()
        self.assertIn("square", mid.functions)
        fn_square = mid.functions["square"]
        self.assertIn("entry", fn_square.blocks)
        entry = fn_square.blocks["entry"]
        self.assertTrue(len(entry.instructions) > 0)
        text = mid.to_text()
        self.assertIn("; MidIR (SSA CFG) Module", text)
        self.assertIn("define f32 @square(%x: f32)", text)

    def test_low_ir_linearization(self):
        mid = self.gen.build_mid_ir()
        low = self.gen.build_low_ir(mid)
        self.assertIn("square", low.functions)
        fn_low = low.functions["square"]
        self.assertTrue(len(fn_low.instructions) > 0)
        text = low.to_text()
        self.assertIn("# LowIR Virtual Register Stream", text)
        self.assertIn("proc square:", text)
        self.assertIn("end proc square", text)

    def test_optimization_passes(self):
        mid = self.gen.build_mid_ir()
        
        # Inject custom instructions to verify specific passes
        entry = mid.functions["square"].blocks["entry"]
        # 1. Constant folding target: 10 + 20
        entry.instructions.append(MidInstruction(op="add", dest="const_target", args=[10, 20]))
        # 2. Heap alloca for escape analysis
        entry.instructions.append(MidInstruction(op="heap_alloca", dest="temp_buf", args=["i32", 128]))
        # 3. Unused dead instruction for DCE
        entry.instructions.append(MidInstruction(op="const", dest="dead_var", args=[999]))

        opt = VeloCOptimizer(profile="max-perf")
        opt_mid, report = opt.optimize(mid)

        self.assertGreaterEqual(report.constant_folds, 1)
        self.assertGreaterEqual(len(report.scalarized_allocations), 1)
        self.assertGreaterEqual(report.dce_instructions_removed, 1)
        self.assertGreaterEqual(report.bounds_checks_eliminated, 1)
        self.assertGreaterEqual(len(report.vectorized_loops), 1)
        self.assertGreaterEqual(len(report.polyhedral_schedules), 1)

        summary = report.summary()
        self.assertIn("VeloC Optimization Report", summary)
        self.assertIn("[Inlining]", summary)
        self.assertIn("[Escape Analysis]", summary)
        self.assertIn("[Constant Folding]", summary)
        self.assertIn("[Auto-Vectorizer]", summary)
        self.assertIn("[Polyhedral Schedule]", summary)

    def test_profiles(self):
        mid = self.gen.build_mid_ir()
        opt_fast = VeloCOptimizer(profile="fast-compile")
        _, rep_fast = opt_fast.optimize(mid)
        self.assertEqual(len(rep_fast.inlined_functions), 0)
        self.assertEqual(rep_fast.constant_folds, 0)

        opt_max = VeloCOptimizer(profile="max-perf")
        _, rep_max = opt_max.optimize(mid)
        self.assertGreater(len(rep_max.inlined_functions), 0)

if __name__ == "__main__":
    unittest.main()
