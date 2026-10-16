import unittest
import subprocess
import sys
import tempfile
from pathlib import Path

class TestMetamorphicCompilation(unittest.TestCase):
    def test_alpha_conversion_metamorphic(self):
        code_orig = '''
        module MetaA;
        #include <veloc.h>
        fn compute() -> i32 {
            let mut sum: i32 = 0;
            for (int i = 0; i < 10; ++i) {
                sum = sum + i;
            }
            return sum;
        }
        fn main() -> i32 {
            println(compute());
            return 0;
        }
        '''

        # Metamorphic variant: alpha-renaming 'sum' -> 'accumulator', 'i' -> 'idx'
        code_renamed = '''
        module MetaB;
        #include <veloc.h>
        fn compute() -> i32 {
            let mut accumulator: i32 = 0;
            for (int idx = 0; idx < 10; ++idx) {
                accumulator = accumulator + idx;
            }
            return accumulator;
        }
        fn main() -> i32 {
            println(compute());
            return 0;
        }
        '''

        with tempfile.TemporaryDirectory() as td:
            src_a = Path(td) / "a.vc"
            src_b = Path(td) / "b.vc"
            exe_a = Path(td) / "a.exe"
            exe_b = Path(td) / "b.exe"

            src_a.write_text(code_orig, encoding="utf-8")
            src_b.write_text(code_renamed, encoding="utf-8")

            veloc_py = Path("D:/VeloC/veloc.py")
            subprocess.run([sys.executable, str(veloc_py), "build", str(src_a), "-o", str(exe_a)], check=True, capture_output=True)
            subprocess.run([sys.executable, str(veloc_py), "build", str(src_b), "-o", str(exe_b)], check=True, capture_output=True)

            res_a = subprocess.run([str(exe_a)], capture_output=True, text=True, check=True)
            res_b = subprocess.run([str(exe_b)], capture_output=True, text=True, check=True)

            self.assertEqual(res_a.stdout.strip(), res_b.stdout.strip())
            self.assertEqual(res_a.stdout.strip(), "45")

if __name__ == '__main__':
    unittest.main()
