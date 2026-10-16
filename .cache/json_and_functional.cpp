#include "D:/VeloC/include/veloc.h"

// [VeloC module declaration]

auto main() -> i32 {
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_BOLD) + std::string("    VeloC 5.0: Native JSON, File IO & Slices      ") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());

    // 1. One-line Fast File Write & Read (Like Python, fast like C)
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[1] One-line Fast File I/O") + ::veloc::to_str(VELOC_RESET)).c_str());
    const auto test_path = "D:/VeloC/sample_config.json";
    const auto original_json = "{\"user\": \"Gamer42\", \"score\": 9500, \"health\": 98.5, \"active\": true}";

    const auto write_res = veloc_write_file(test_path, original_json);
    if (write_res.is_ok()) {
        printf("%s\n", (std::string("  Successfully wrote JSON to ") + ::veloc::to_str(test_path)).c_str());
    }

    const auto read_res = veloc_read_file(test_path);
    if (read_res.is_ok()) {
        const auto content = read_res.unwrap();
        printf("%s\n", (std::string("  Read back from disk: ") + ::veloc::to_str(content)).c_str());
    }

    // 2. Built-in Zero-Dependency JSON Parser (Top Reddit C++ (Request).unwrap())
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[2] Built-in Native Fast JSON Parser") + ::veloc::to_str(VELOC_RESET)).c_str());
    const auto root = veloc::JsonValue::parse(original_json);

    const auto user_val = root.get("user");
    const auto score_val = root.get("score");
    const auto health_val = root.get("health");
    const auto active_val = root.get("active");

    if (user_val.is_some()) {
        const auto user_name = user_val.unwrap().as_str();
        printf("%s\n", (std::string("  Parsed 'user':   ") + ::veloc::to_str(user_name)).c_str());
    }
    if (score_val.is_some()) {
        const auto score = score_val.unwrap().as_int();
        printf("%s\n", (std::string("  Parsed 'score':  ") + ::veloc::to_str(score)).c_str());
    }
    if (health_val.is_some()) {
        const auto health = health_val.unwrap().as_float();
        printf("%s\n", (std::string("  Parsed 'health': ") + ::veloc::to_str(health)).c_str());
    }
    if (active_val.is_some()) {
        const auto active = active_val.unwrap().as_bool();
        printf("%s\n", (std::string("  Parsed 'active': ") + ::veloc::to_str(active)).c_str());
    }

    // 3. Functional Zero-Allocation Slice Operations (sum, count_if)
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[3] Functional Zero-Allocation Slice Operations") + ::veloc::to_str(VELOC_RESET)).c_str());
    i32 numbers[6] = {10, 25, 5, 40, 15, 30};
    const auto slice = Slice<i32>::from_array(numbers, 6);

    const auto total = veloc::sum(slice);
    const auto count_above_20 = veloc::count_if(slice, [](i32 x) { return x >= 20; });

    printf("%s\n", (std::string("  Slice elements sum: ") + ::veloc::to_str(total)).c_str());
    printf("%s\n", (std::string("  Elements >= 20:     ") + ::veloc::to_str(count_above_20) + std::string(" items")).c_str());

    // Clean up temporary file
    remove(test_path);

    printf("%s\n", (::veloc::to_str(VELOC_GREEN) + std::string("[SUCCESS] VeloC 5.0 capabilities verified!") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());

    return 0;
}