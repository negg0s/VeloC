# Day 28: C-ABI Interoperability

## Goal
Export a function callable from C without name mangling.

## Theory
`extern "C"` instructs the compiler to produce standard C symbols.

## Starter Code
```veloc
extern "C" int c_compatible_add(int a, int b) {
    return a + b;
}

fn main() -> i32 {
    printf("Add: %d\n", c_compatible_add(15, 27));
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 28
veloc learn check
```

## Hint
> [!TIP]
> 15 + 27 = 42.
