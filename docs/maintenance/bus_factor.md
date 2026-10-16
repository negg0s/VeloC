# VeloC Project: Bus Factor Recovery & Continuity Plan

## 1. Purpose & Risk Mitigation
The VeloC project is designed to be resilient against the loss, departure, or unavailability of any single maintainer (Bus Factor $\ge 3$). This document details emergency continuity procedures, credential rotation, and maintainer succession.

---

## 2. Access Delegation & Key Rotation

### 2.1 Cryptographic Signing Keys
- **Release Signing**: Offline GPG keys are backed up in cold hardware security modules (HSM) with 2-of-3 multi-signature split.
- **Transparency Log**: All cryptographic signatures and package digests are appended to `.veloc/transparency.log`.
- **Key Rotation Runbook**:
  1. Revoke compromised/inactive subkeys: `gpg --edit-key <KEY_ID> -> revkey`.
  2. Generate replacement signing key and publish fingerprint to repository `SECURITY.md`.
  3. Re-sign release metadata: `python veloc.py provenance <artifact>`.

### 2.2 Repository & Tooling Access
- Repository ownership is managed by an organizational multi-owner team requiring at least 2 distinct approval signatures for administrative settings.
- Automated CI triggers and release packaging do not depend on personal developer credentials.

---

## 3. Emergency Release Runbook
If an emergency security vulnerability or compiler regression is identified:
1. **Isolation**: Create hotfix branch `release/hotfix-1.0.x`.
2. **Deterministic Verification**: Verify bit-for-bit build reproducibility across multiple independent machines:
   ```bash
   python veloc.py verify-repro <source_file>
   ```
3. **Crater Gate**: Execute the full ecosystem build verification suite:
   ```bash
   python veloc.py crater
   ```
4. **Golden Regression**: Verify golden tests pass:
   ```bash
   python tests/test_golden.py
   ```
5. **Tag & Publish**: Tag release `v1.0.x` and publish updated transparency logs and SBOMs.
