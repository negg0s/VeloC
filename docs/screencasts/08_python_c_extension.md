# Screencast: Accelerating Python with Zero-Copy NumPy Buffers

## Overview
This screencast demonstrates accelerating python with zero-copy numpy buffers step-by-step with exact shell commands and expected outputs.

## Walkthrough Script

### Action 1: Step 1: Build Python extension
```bash
veloc pyext examples/particles.vc
```

### Action 2: Step 2: Run comparative benchmark
```bash
python benchmarks/bench_pyext.py
```
