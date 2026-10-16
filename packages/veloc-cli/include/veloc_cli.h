#ifndef VELOC_CLI_H
#define VELOC_CLI_H

#include <veloc.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <unordered_map>
#include <immintrin.h>

namespace veloc {
namespace cli {

    // ========================================================================
    // 1. Command-Line Argument Parser
    // ========================================================================
    class ArgParser {
    public:
        std::string app_name;
        std::unordered_map<std::string, std::string> options;
        std::vector<std::string> positional;

        ArgParser(const std::string& name) : app_name(name) {}

        void parse(int argc, char** argv) {
            for (int i = 1; i < argc; i++) {
                std::string arg = argv[i];
                if (arg.rfind("--", 0) == 0) {
                    size_t eq = arg.find('=');
                    if (eq != std::string::npos) {
                        std::string k = arg.substr(2, eq - 2);
                        std::string v = arg.substr(eq + 1);
                        options[k] = v;
                    } else if (i + 1 < argc && argv[i + 1][0] != '-') {
                        options[arg.substr(2)] = argv[++i];
                    } else {
                        options[arg.substr(2)] = "true";
                    }
                } else if (arg.rfind("-", 0) == 0 && arg.size() > 1) {
                    options[arg.substr(1)] = (i + 1 < argc && argv[i + 1][0] != '-') ? argv[++i] : "true";
                } else {
                    positional.push_back(arg);
                }
            }
        }

        bool has(const std::string& key) const {
            return options.find(key) != options.end();
        }

        std::string get(const std::string& key, const std::string& default_val = "") const {
            auto it = options.find(key);
            return (it != options.end()) ? it->second : default_val;
        }
    };

    // ========================================================================
    // 2. ANSI Colored Terminal Formatter & Table Generator
    // ========================================================================
    class TerminalTable {
    public:
        std::vector<std::string> headers;
        std::vector<std::vector<std::string>> rows;

        TerminalTable(const std::vector<std::string>& h) : headers(h) {}

        void add_row(const std::vector<std::string>& row) {
            rows.push_back(row);
        }

        void print() const {
            if (headers.empty()) return;
            std::vector<usize> col_widths(headers.size(), 0);
            for (usize i = 0; i < headers.size(); i++) {
                col_widths[i] = headers[i].size();
            }
            for (const auto& r : rows) {
                for (usize i = 0; i < r.size() && i < col_widths.size(); i++) {
                    if (r[i].size() > col_widths[i]) col_widths[i] = r[i].size();
                }
            }

            // Print Header
            printf(VELOC_CYAN);
            for (usize i = 0; i < headers.size(); i++) {
                printf("%-*s  ", (int)col_widths[i], headers[i].c_str());
            }
            printf(VELOC_RESET "\n");

            // Print Separator
            for (usize i = 0; i < headers.size(); i++) {
                for (usize k = 0; k < col_widths[i]; k++) printf("-");
                printf("  ");
            }
            printf("\n");

            // Print Rows
            for (const auto& r : rows) {
                for (usize i = 0; i < headers.size(); i++) {
                    const char* val = (i < r.size()) ? r[i].c_str() : "";
                    printf("%-*s  ", (int)col_widths[i], val);
                }
                printf("\n");
            }
        }
    };

    // ========================================================================
    // 3. Ultra-Fast AVX2 SIMD Grep (Substring Search)
    // Searches for exact byte matches across gigabytes with 32-byte SIMD strides
    // ========================================================================
    class SIMDGrep {
    public:
        static usize search(const char* text, usize text_len, const char* pattern, usize pattern_len) {
            if (!text || text_len == 0 || !pattern || pattern_len == 0) return 0;
            if (pattern_len > text_len) return 0;

            usize matches = 0;
            char first_ch = pattern[0];
            char last_ch = pattern[pattern_len - 1];

            __m256i first_vec = _mm256_set1_epi8(first_ch);
            __m256i last_vec = _mm256_set1_epi8(last_ch);

            usize i = 0;
            for (; i + 32 <= text_len - pattern_len + 1; i += 32) {
                __m256i chunk_first = _mm256_loadu_si256((const __m256i*)&text[i]);
                __m256i chunk_last = _mm256_loadu_si256((const __m256i*)&text[i + pattern_len - 1]);

                __m256i cmp_first = _mm256_cmpeq_epi8(chunk_first, first_vec);
                __m256i cmp_last = _mm256_cmpeq_epi8(chunk_last, last_vec);
                __m256i mask_vec = _mm256_and_si256(cmp_first, cmp_last);

                u32 mask = (u32)_mm256_movemask_epi8(mask_vec);
                while (mask != 0) {
                    u32 bit_idx = (u32)__builtin_ctz(mask);
                    mask &= mask - 1;

                    // Verify interior of pattern if length > 2
                    if (pattern_len <= 2 || memcmp(&text[i + bit_idx + 1], pattern + 1, pattern_len - 2) == 0) {
                        matches++;
                    }
                }
            }

            // Scalar tail
            for (; i <= text_len - pattern_len; i++) {
                if (text[i] == first_ch && memcmp(&text[i], pattern, pattern_len) == 0) {
                    matches++;
                }
            }

            return matches;
        }
    };

} // namespace cli
} // namespace veloc

#endif // VELOC_CLI_H
