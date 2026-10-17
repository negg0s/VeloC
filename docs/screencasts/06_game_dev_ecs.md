# Screencast: Building an ECS Game Engine with 1M Entities at 3,000 FPS

## Overview
This screencast demonstrates building an ecs game engine with 1m entities at 3,000 fps step-by-step with exact shell commands and expected outputs.

## Walkthrough Script

### Action 1: Step 1: Run 3D rendering benchmark
```bash
veloc run apps/veloc-render/src/main.vc
```

### Action 2: Step 2: Trace frame timings
```bash
veloc run packages/veloc-game/tests/test_game.vc
```
