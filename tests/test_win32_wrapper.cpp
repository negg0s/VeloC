#include "wrappers/veloc_win32.h"
#include <cassert>
#include <cstdio>
#include <cstring>

using namespace veloc::win32;

int main() {
    printf("==================================================\n");
    printf("          Testing VeloC Win32 API Wrapper         \n");
    printf("==================================================\n");

    // 1. File test
    const char* test_file = "build/win32_wrapper_test.tmp";
    {
        auto file_res = File::create_write(test_file);
        assert(file_res.is_ok());
        File file = file_res.unwrap();
        const char msg[] = "VeloC Native Win32 Test String";
        auto write_res = file.write(msg, sizeof(msg));
        assert(write_res.is_ok());
        assert(write_res.unwrap() == sizeof(msg));
    }
    printf("  [PASS] File create and write verified.\n");

    // Read back
    {
        auto file_res = File::open_read(test_file);
        assert(file_res.is_ok());
        File file = file_res.unwrap();
        char buf[64] = {0};
        auto read_res = file.read(buf, sizeof(buf));
        assert(read_res.is_ok());
        assert(strcmp(buf, "VeloC Native Win32 Test String") == 0);
    }
    printf("  [PASS] File open, read, and RAII close verified.\n");

    // 2. Registry test (verify HKEY_LOCAL_MACHINE\\SOFTWARE exists)
    bool reg_ok = Registry::key_exists(HKEY_LOCAL_MACHINE, "SOFTWARE");
    assert(reg_ok == true);
    printf("  [PASS] Registry key inspection verified.\n");

    // 3. Process spawning test (spawn cmd.exe /c exit 42)
    {
        auto proc_res = Process::spawn("cmd.exe /c exit 42");
        assert(proc_res.is_ok());
        Process proc = proc_res.unwrap();
        int code = proc.wait_and_get_exit_code();
        assert(code == 42);
    }
    printf("  [PASS] Process spawn and exit code tracking verified (code=42).\n");

    printf("==================================================\n");
    printf("[ALL WIN32 WRAPPER TESTS PASSED]\n");
    return 0;
}
