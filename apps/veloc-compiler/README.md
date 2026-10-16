# VeloC-Compiler

Micro-language compiler, SSA constant folding optimizer, and bytecode virtual machine interpreter implemented in VeloC.

## Architecture
- **Bytecode Instruction Set**: Stack-based VM with arithmetic (`ADD`, `SUB`, `MUL`), variables (`LOAD`, `STORE`), and conditional branches (`CMP_LT`, `JZ`, `JMP`).
- **Optimization Pass**: Peephole constant folding pass collapsing compile-time constant arithmetic into immediate literals.
- **Virtual Machine**: High-speed dispatch loop executing over 113 million bytecode instructions per second.

## Performance
- **VM Execution**: 13,000,010 instructions in 114.38 ms (113.66 MIPS).
- **Correctness**: Verified constant folding arithmetic and full million-iteration accumulator loops.
