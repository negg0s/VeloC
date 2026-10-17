# Screencast: Structure of Arrays (SoA) and 256-bit AVX2 SIMD

## Overview
This screencast demonstrates structure of arrays (soa) and 256-bit avx2 simd step-by-step with exact shell commands and expected outputs.

## Walkthrough Script

### Action 1: Step 1: View SoA definition
```bash
cat examples/particles.vc
```

### Action 2: Step 2: Compile with optimization report
```bash
veloc build examples/particles.vc --opt-report
```

### Action 3: Step 3: Measure 50M particles throughput
```bash
veloc run examples/particles.vc
```
