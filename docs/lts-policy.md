# VeloC Long-Term Support (LTS) & Stability Policy

## 1. Overview & Commitment
VeloC commits to uncompromising backward compatibility and production stability. Systems software deployed on VeloC must continue to compile and execute predictably without maintenance churn.

---

## 2. Release Cadence & Lifecycles

| Release Stream | Cadence | Support Window | Breaking Changes | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Major (X.0.0)** | Every 24 months | 3 Years (LTS) | Permitted (via RFC) | Generational language improvements |
| **Minor (1.X.0)** | Every 3 months | Supported until next Minor | Strictly Prohibited | Backward-compatible features, stdlib |
| **Patch (1.X.Y)** | Monthly / On-demand | Active release stream | Strictly Prohibited | Security patches, bug fixes, compiler optimizations |

---

## 3. Backward Compatibility Invariants
1. **Source Compatibility**: Any valid code written for VeloC 1.0.0 must continue to compile without errors on any subsequent 1.X.Y compiler.
2. **ABI / Interop Guarantee**: The C ABI export signature (`extern "C"`) is frozen for all 1.X releases.
3. **Deprecation Cycle**: No stable feature may be removed without being marked deprecated with compile-time warnings for at least one full major version cycle.
4. **Automated Migration (`veloc fix`)**: If an edition or major release introduces alternative idioms, an automated migration tool must be provided.
