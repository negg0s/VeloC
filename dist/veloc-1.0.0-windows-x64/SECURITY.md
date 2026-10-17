# Security Policy: VeloC Compiler & Runtime

## Reporting a Vulnerability

The VeloC project takes systems security seriously. If you discover a vulnerability or security bug (such as an unhandled panic in the parser, memory corruption, or unsafe bounds bypass), please follow our responsible disclosure protocol:

1. **Email Reports**: Send a detailed report to `security@veloc-lang.org`.
2. **Details to Include**:
   - VeloC compiler version (`veloc --version` or Git commit hash).
   - Minimal reproducible `.vc` source file.
   - Operating system and target CPU details.
3. **Response Timeline**:
   - Initial acknowledgement within **24 hours**.
   - Remediation and patch release within **7 days** for critical CVEs.

---

## Compiler Security Guarantees
- **Minimal Undefined Behavior**: VeloC enforces two's complement integer wrapping (`-fwrapv`, `RULE-UB-001`), eliminating undefined integer overflow optimizer traps.
- **Panic-Free Parsing**: The compiler lexer and parser are fuzzed (`veloc fuzz`) across thousands of mutated inputs to guarantee zero panics or memory corruption on invalid input.
- **Stack Protection**: The static analyzer (`veloc check`) blocks escaping pointers to stack variables.
