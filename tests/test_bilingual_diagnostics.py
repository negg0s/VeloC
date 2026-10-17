import sys
import unittest
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from diagnostics import DiagnosticReporter, DiagnosticCode, explain_error_code, set_diagnostic_lang

class TestBilingualDiagnostics(unittest.TestCase):
    def test_english_diagnostics(self):
        set_diagnostic_lang("en")
        rep = DiagnosticReporter("let val = 42;", "main.vc", beginner_mode=True, lang="en")
        rep.error(DiagnosticCode.E0002, "Incompatible types in assignment", 1, 5, 3, "use `as i64`")
        rendered = rep.render()
        self.assertIn("error[E0002]", rendered)
        self.assertIn("= help: use `as i64`", rendered)
        self.assertIn("= beginner tip:", rendered)

    def test_russian_diagnostics(self):
        set_diagnostic_lang("ru")
        rep = DiagnosticReporter("let val = 42;", "main.vc", beginner_mode=True, lang="ru")
        rep.error(DiagnosticCode.E0002, "Несовместимые типы в присваивании", 1, 5, 3, "используйте `as i64`")
        rendered = rep.render()
        self.assertIn("ошибка[E0002]", rendered)
        self.assertIn("= подсказка: используйте `as i64`", rendered)
        self.assertIn("= совет новичку:", rendered)

    def test_explain_code_bilingual(self):
        exp_en = explain_error_code("E0001", lang="en")
        self.assertIn("Syntax Error", exp_en)
        exp_ru = explain_error_code("E0001", lang="ru")
        self.assertIn("Синтаксическая ошибка", exp_ru)

if __name__ == "__main__":
    unittest.main()
