# Screencast: Zero-Cost Memory Arenas vs OS Malloc

## Overview
This screencast demonstrates zero-cost memory arenas vs os malloc step-by-step with exact shell commands and expected outputs.

## Walkthrough Script

### Action 1: Step 1: Create arena benchmark
```bash
veloc run examples/particles.vc
```

### Action 2: Step 2: Inspect arena reset cycles
```bash
veloc bench --incremental
```

### Action 3: Step 3: Check memory leak telemetry
```bash
veloc check examples/particles.vc --bounds-report
```
