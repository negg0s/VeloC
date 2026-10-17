# Screencast: Strict IEEE-754 Precision and ULP Accuracy Contracts

## Overview
This screencast demonstrates strict ieee-754 precision and ulp accuracy contracts step-by-step with exact shell commands and expected outputs.

## Walkthrough Script

### Action 1: Step 1: Run accuracy test harness
```bash
python benchmarks/numerics_accuracy_harness.py
```

### Action 2: Step 2: Inspect ULP verification
```bash
python tests/test_nan_propagation.py
```
