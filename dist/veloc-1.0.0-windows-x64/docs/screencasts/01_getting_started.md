# Screencast: Getting Started with VeloC in 5 Minutes

## Overview
This screencast demonstrates getting started with veloc in 5 minutes step-by-step with exact shell commands and expected outputs.

## Walkthrough Script

### Action 1: Step 1: Check hardware and toolchain
```bash
veloc info
```

### Action 2: Step 2: Initialize a new project
```bash
veloc new demo_app --template=cli
```

### Action 3: Step 3: Build the application
```bash
cd demo_app && veloc build src/main.vc
```

### Action 4: Step 4: Run built-in tests
```bash
veloc test src/main.vc
```
