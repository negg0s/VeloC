# Screencast: Sub-Second Compilation with PCH and LLD Linker

## Overview
This screencast demonstrates sub-second compilation with pch and lld linker step-by-step with exact shell commands and expected outputs.

## Walkthrough Script

### Action 1: Step 1: Benchmark cold vs warm build
```bash
veloc build examples/particles.vc --timings
```

### Action 2: Step 2: Run hot reloading
```bash
veloc watch examples/particles.vc --hot
```
