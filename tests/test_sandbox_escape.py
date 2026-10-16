import unittest
from src.security import PluginSandbox, CapabilitySecurity, SecretBranchLinter

class TestSandboxAndCapabilities(unittest.TestCase):
    def test_sandbox_path_traversal_escape(self):
        sandbox = PluginSandbox(allowed_caps=["time.now"])
        malicious_code = 'let f = read_text("../../windows/system32/cmd.exe");'
        res = sandbox.execute_snippet(malicious_code)
        self.assertFalse(res["success"])
        self.assertTrue(res["escaped"])
        self.assertIn("SandboxViolation", res["error"])

    def test_sandbox_process_spawn_escape(self):
        sandbox = PluginSandbox(allowed_caps=["fs.read"])
        malicious_code = 'system("whoami");'
        res = sandbox.execute_snippet(malicious_code)
        self.assertFalse(res["success"])
        self.assertTrue(res["escaped"])

    def test_capability_security_enforcement(self):
        cap_sec = CapabilitySecurity()
        cap_sec.allowed_caps = {"time.now", "rng.secure"}
        cap_sec.denied_caps = {"net.*", "proc.exec"}

        # Allowed
        self.assertTrue(cap_sec.is_allowed("time.now"))
        self.assertTrue(cap_sec.is_allowed("rng.secure"))
        # Denied
        self.assertFalse(cap_sec.is_allowed("net.http"))
        self.assertFalse(cap_sec.is_allowed("proc.exec"))

        violations = cap_sec.verify_source('let res = http_get("https://example.com");')
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["code"], "E0801")
        self.assertEqual(violations[0]["capability"], "net.http")

    def test_secret_branch_linter(self):
        code_leak = '''
        let key: Secret<u64> = Secret(42);
        if (key == 42) {
            println("matched");
        }
        '''
        linter = SecretBranchLinter(code_leak)
        warnings = linter.lint()
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["rule"], "SEC-001")
        self.assertIn("side-channel timing leak", warnings[0]["message"])

        code_safe = '''
        let key: Secret<u64> = Secret(42);
        let valid = key.constant_time_compare(other);
        '''
        linter_safe = SecretBranchLinter(code_safe)
        self.assertEqual(len(linter_safe.lint()), 0)

if __name__ == '__main__':
    unittest.main()
