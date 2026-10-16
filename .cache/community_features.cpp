#include "D:/VeloC/include/veloc.h"

// [VeloC module declaration]

// 1. Modern function syntax
auto divide(f32 a, f32 b) -> Result<f32, const char*> {
    if (b == 0.0f) {
        return Result<f32, const char*>::Err("Division by zero!");
    }
    return Result<f32, const char*>::Ok(a / b);
}

auto find_item(i32 target) -> Option<i32> {
    if (target > 0) {
        return Option<i32>::Some(target * 10);
    }
    return Option<i32>::None();
}

// 2. Built-in Tests (Directly inside language, like Zig & (Rust).unwrap())
void _veloc_test_case_1() {

    const auto a = 10;
    auto b = 20;
    b += 5;
    assert_eq(a + b, 35);
}

void _veloc_test_case_2() {

    const auto ok_res = divide(100.0f, 4.0f);
    assert_true(ok_res.is_ok());
    assert_eq((i32)ok_res.unwrap(), 25);

    const auto err_res = divide(10.0f, 0.0f);
    assert_true(err_res.is_err());
    assert_eq(err_res.unwrap_or(-1.0f), -1.0f);
}

void _veloc_test_case_3() {

    const auto opt_some = find_item(5);
    assert_true(opt_some.is_some());
    assert_eq(opt_some.unwrap(), 50);

    const auto opt_none = find_item(-3);
    assert_true(opt_none.is_none());
    assert_eq(opt_none.unwrap_or(999), 999);
}

void _veloc_test_case_4() {

    i32 numbers[5] = {10, 20, 30, 40, 50};
    auto s = Slice<i32>::from_array(numbers, 5);
    assert_eq(s[0], 10);
    assert_eq(s[4], 50);
    s[2] = 99;
    assert_eq(s[2], 99);
}

// 3. Regular main program execution
auto main() -> i32 {
    printf("==================================================\n");
    printf("     VeloC 2.0: Massive Reddit Community Update   \n");
    printf("==================================================\n");

    // String interpolation (No format string mismatch (bugs).unwrap())
    const auto name = "Developer";
    const auto speedup = 21.7;
    printf("%s\n", (std::string("Hello ") + ::veloc::to_str(name) + std::string("! VeloC speedup is ") + ::veloc::to_str(speedup) + std::string("x over standard C++!")).c_str());

    // Result<T, E>
    const auto res = divide(42.0f, 2.0f);
    if (res.is_ok()) {
        const auto val = res.unwrap();
        printf("%s\n", (std::string("Division Result: 42 / 2 = ") + ::veloc::to_str(val)).c_str());
    }

    // Subprocess execution (Top Reddit C++ complaint (solved).unwrap())
    printf("Spawning native subprocess from VeloC...\n");
    veloc_exec("echo [Subprocess Output]: Hello from Windows shell!");

    printf("Community features demonstration complete!\n");
    printf("==================================================\n");

    return 0;
}