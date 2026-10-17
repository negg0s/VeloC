// VeloC Idiomatic Win32 API Wrapper
// Provides safe RAII, Result types, and zero-cost abstraction over Windows SDK
#pragma once

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include "veloc.h"

namespace veloc {
namespace win32 {

// 1. Filesystem & File Operations
struct File {
    HANDLE handle;

    File() : handle(INVALID_HANDLE_VALUE) {}
    explicit File(HANDLE h) : handle(h) {}
    ~File() { close(); }

    File(const File& other) {
        if (other.handle != INVALID_HANDLE_VALUE && other.handle != NULL) {
            DuplicateHandle(GetCurrentProcess(), other.handle, GetCurrentProcess(), &handle, 0, FALSE, DUPLICATE_SAME_ACCESS);
        } else {
            handle = INVALID_HANDLE_VALUE;
        }
    }

    File& operator=(const File& other) {
        if (this != &other) {
            close();
            if (other.handle != INVALID_HANDLE_VALUE && other.handle != NULL) {
                DuplicateHandle(GetCurrentProcess(), other.handle, GetCurrentProcess(), &handle, 0, FALSE, DUPLICATE_SAME_ACCESS);
            } else {
                handle = INVALID_HANDLE_VALUE;
            }
        }
        return *this;
    }

    bool is_valid() const {
        return handle != INVALID_HANDLE_VALUE && handle != NULL;
    }

    void close() {
        if (is_valid()) {
            CloseHandle(handle);
            handle = INVALID_HANDLE_VALUE;
        }
    }

    static Result<File, const char*> open_read(const char* path) {
        HANDLE h = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        if (h == INVALID_HANDLE_VALUE) {
            return Result<File, const char*>::Err("Failed to open file for reading");
        }
        File f(h);
        return Result<File, const char*>::Ok(f);
    }

    static Result<File, const char*> create_write(const char* path) {
        HANDLE h = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (h == INVALID_HANDLE_VALUE) {
            return Result<File, const char*>::Err("Failed to create file for writing");
        }
        File f(h);
        return Result<File, const char*>::Ok(f);
    }

    usize get_size() const {
        if (!is_valid()) return 0;
        LARGE_INTEGER li;
        if (GetFileSizeEx(handle, &li)) {
            return (usize)li.QuadPart;
        }
        return 0;
    }

    Result<usize, const char*> write(const void* buffer, usize bytes_to_write) {
        if (!is_valid()) return Result<usize, const char*>::Err("Invalid file handle");
        DWORD bytes_written = 0;
        if (!WriteFile(handle, buffer, (DWORD)bytes_to_write, &bytes_written, NULL)) {
            return Result<usize, const char*>::Err("WriteFile failed");
        }
        return Result<usize, const char*>::Ok((usize)bytes_written);
    }

    Result<usize, const char*> read(void* buffer, usize bytes_to_read) {
        if (!is_valid()) return Result<usize, const char*>::Err("Invalid file handle");
        DWORD bytes_read = 0;
        if (!ReadFile(handle, buffer, (DWORD)bytes_to_read, &bytes_read, NULL)) {
            return Result<usize, const char*>::Err("ReadFile failed");
        }
        return Result<usize, const char*>::Ok((usize)bytes_read);
    }
};

// 2. Windows Registry Operations
struct Registry {
    static Result<DWORD, const char*> get_dword(HKEY root, const char* subkey, const char* value_name) {
        DWORD data = 0;
        DWORD data_size = sizeof(DWORD);
        DWORD type = REG_DWORD;
        LSTATUS status = RegGetValueA(root, subkey, value_name, RRF_RT_REG_DWORD, &type, &data, &data_size);
        if (status != ERROR_SUCCESS) {
            return Result<DWORD, const char*>::Err("RegGetValueA failed");
        }
        return Result<DWORD, const char*>::Ok(data);
    }

    static bool key_exists(HKEY root, const char* subkey) {
        HKEY hKey;
        if (RegOpenKeyExA(root, subkey, 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
            RegCloseKey(hKey);
            return true;
        }
        return false;
    }
};

// 3. Process Execution & Spawning
struct Process {
    HANDLE process_handle;
    HANDLE thread_handle;
    DWORD process_id;

    Process() : process_handle(INVALID_HANDLE_VALUE), thread_handle(INVALID_HANDLE_VALUE), process_id(0) {}
    ~Process() { close(); }

    Process(const Process& other) : process_id(other.process_id) {
        if (other.process_handle != INVALID_HANDLE_VALUE && other.process_handle != NULL) {
            DuplicateHandle(GetCurrentProcess(), other.process_handle, GetCurrentProcess(), &process_handle, 0, FALSE, DUPLICATE_SAME_ACCESS);
        } else {
            process_handle = INVALID_HANDLE_VALUE;
        }
        if (other.thread_handle != INVALID_HANDLE_VALUE && other.thread_handle != NULL) {
            DuplicateHandle(GetCurrentProcess(), other.thread_handle, GetCurrentProcess(), &thread_handle, 0, FALSE, DUPLICATE_SAME_ACCESS);
        } else {
            thread_handle = INVALID_HANDLE_VALUE;
        }
    }

    Process& operator=(const Process& other) {
        if (this != &other) {
            close();
            process_id = other.process_id;
            if (other.process_handle != INVALID_HANDLE_VALUE && other.process_handle != NULL) {
                DuplicateHandle(GetCurrentProcess(), other.process_handle, GetCurrentProcess(), &process_handle, 0, FALSE, DUPLICATE_SAME_ACCESS);
            } else {
                process_handle = INVALID_HANDLE_VALUE;
            }
            if (other.thread_handle != INVALID_HANDLE_VALUE && other.thread_handle != NULL) {
                DuplicateHandle(GetCurrentProcess(), other.thread_handle, GetCurrentProcess(), &thread_handle, 0, FALSE, DUPLICATE_SAME_ACCESS);
            } else {
                thread_handle = INVALID_HANDLE_VALUE;
            }
        }
        return *this;
    }

    void close() {
        if (process_handle != INVALID_HANDLE_VALUE && process_handle != NULL) {
            CloseHandle(process_handle);
            process_handle = INVALID_HANDLE_VALUE;
        }
        if (thread_handle != INVALID_HANDLE_VALUE && thread_handle != NULL) {
            CloseHandle(thread_handle);
            thread_handle = INVALID_HANDLE_VALUE;
        }
    }

    static Result<Process, const char*> spawn(const char* command_line) {
        STARTUPINFOA si;
        PROCESS_INFORMATION pi;
        ZeroMemory(&si, sizeof(si));
        si.cb = sizeof(si);
        ZeroMemory(&pi, sizeof(pi));

        char cmd[1024];
        strncpy(cmd, command_line, sizeof(cmd) - 1);
        cmd[sizeof(cmd) - 1] = '\0';

        if (!CreateProcessA(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
            return Result<Process, const char*>::Err("CreateProcessA failed");
        }

        Process p;
        p.process_handle = pi.hProcess;
        p.thread_handle = pi.hThread;
        p.process_id = pi.dwProcessId;
        return Result<Process, const char*>::Ok(p);
    }

    int wait_and_get_exit_code(DWORD timeout_ms = INFINITE) {
        if (process_handle == INVALID_HANDLE_VALUE) return -1;
        WaitForSingleObject(process_handle, timeout_ms);
        DWORD exit_code = 0;
        GetExitCodeProcess(process_handle, &exit_code);
        return (int)exit_code;
    }
};

} // namespace win32
} // namespace veloc
