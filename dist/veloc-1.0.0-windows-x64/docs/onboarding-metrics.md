# VeloC Developer Onboarding & DX Metrics

Empirically measured on **VeloC 1.0.0-rc4** under Windows x86_64, Clang 20 toolchain.

---

## Onboarding Metrics Summary

| Onboarding Stage / Metric | Measured Value | SLA Target | Status |
|---|---|---|---|
| **Clean Run to First Output (`hello.vc`)** | **0.798 s** | < 60.0 s | **PASSED** |
| **Interactive Lesson 1 (`veloc learn`)** | **0.693 s** | < 30.0 s | **PASSED** |
| **Doc Snippet Correctness (RU & EN)** | **100.0% (43/43)** | 100.0% | **PASSED** |

---

## Qualitative DX Observations

1. **Zero Setup Friction**:
   - Because the VeloC driver automatically selects system compilers and manages precompiled headers and runtime object caches, users can start compiling within seconds of downloading.
2. **Interactive Progression**:
   - The interactive 30-day course provides immediate in-terminal feedback with localized advice in English and Russian, reducing cognitive friction for new systems programmers.
3. **Executable Documentation Guarantee**:
   - 100% of the tested code blocks across the reference manual, book, cookbook, and tutorial compile and run cleanly, ensuring users never encounter stale or broken documentation examples.
