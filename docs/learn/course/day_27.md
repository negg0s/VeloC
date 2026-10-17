# Day 27: Package Management and Dependencies

## Goal
Understand package configuration in `veloc.toml`.

## Theory
`veloc.toml` declares build profiles, dependencies, and edition settings.

## Starter Code
```veloc
fn main() -> i32 {
    printf("Package: veloc_app, Version: 1.0.0\n");
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 27
veloc learn check
```

## Hint
> [!TIP]
> Output the package and version.
