# VeloC Evaluation Order Specification

## 1. Expression Evaluation

### RULE-EVAL-001: Strict Left-to-Right Operand Evaluation
- In binary expressions `A op B`, sub-expression `A` is fully evaluated and all side-effects are completed before sub-expression `B` begins evaluation.
- In function calls `f(a1, a2, ... an)`, the callee `f` is evaluated first, followed by arguments `a1` through `an` strictly from left to right.

### RULE-EVAL-002: Short-Circuit Evaluation
- Logical AND (`A && B`): `B` is evaluated if and only if `A` evaluates to `true`.
- Logical OR (`A || B`): `B` is evaluated if and only if `A` evaluates to `false`.
- Nullish Coalesce (`A ?? B`): `B` is evaluated if and only if `A` is null or `None`.

### RULE-EVAL-003: Pipeline Operator Evaluation
- Pipeline expressions `x |> f |> g(a)` evaluate as `g(f(x), a)` with left-to-right sequencing.
- The output of the left operand is supplied as the first positional argument of the right operand call.

### RULE-EVAL-004: Defer Execution Sequencing
- Multiple `defer` declarations inside the same scope block execute strictly in reverse declaration order (LIFO).
- A defer declared inside an inner block executes immediately upon leaving that inner block, not at the outer function exit.
