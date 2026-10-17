# Screencast: Package Manager, Dependencies, and Lockfile Integrity

## Overview
This screencast demonstrates package manager, dependencies, and lockfile integrity step-by-step with exact shell commands and expected outputs.

## Walkthrough Script

### Action 1: Step 1: Add a dependency
```bash
veloc add veloc-data
```

### Action 2: Step 2: Audit supply chain
```bash
veloc audit --lock
```

### Action 3: Step 3: Generate SBOM
```bash
veloc sbom --format=cyclonedx
```
