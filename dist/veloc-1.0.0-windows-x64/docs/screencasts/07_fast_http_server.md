# Screencast: Processing 3.4 Million HTTP Requests per Second

## Overview
This screencast demonstrates processing 3.4 million http requests per second step-by-step with exact shell commands and expected outputs.

## Walkthrough Script

### Action 1: Step 1: Build the network package
```bash
veloc build packages/veloc-net/src/http.vc
```

### Action 2: Step 2: Run benchmark suite
```bash
veloc run packages/veloc-net/tests/test_net.vc
```
