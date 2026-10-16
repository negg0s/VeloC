#ifndef VELOC_DATA_H
#define VELOC_DATA_H

#include <veloc.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <fstream>
#include <algorithm>
#include <immintrin.h>

namespace veloc {
namespace data {

    // ========================================================================
    // 1. Arrow-like Columnar Vector & DataFrame
    // ========================================================================
    template <typename T>
    class Column {
    public:
        std::string name;
        std::vector<T> values;
        std::vector<u8> null_bitmap; // 1 = valid, 0 = null

        Column(const std::string& col_name) : name(col_name) {}

        void push(const T& val, bool is_valid = true) {
            values.push_back(val);
            null_bitmap.push_back(is_valid ? 1 : 0);
        }

        usize size() const { return values.size(); }

        const T& operator[](usize idx) const { return values[idx]; }
        T& operator[](usize idx) { return values[idx]; }

        bool is_null(usize idx) const { return null_bitmap[idx] == 0; }
    };

    class DataFrame {
    public:
        std::vector<Column<i64>> i64_cols;
        std::vector<Column<f64>> f64_cols;
        std::vector<Column<std::string>> str_cols;
        usize row_count;

        DataFrame() : row_count(0) {}

        void add_i64_column(const std::string& name) {
            i64_cols.emplace_back(name);
        }

        void add_f64_column(const std::string& name) {
            f64_cols.emplace_back(name);
        }

        void add_str_column(const std::string& name) {
            str_cols.emplace_back(name);
        }

        Column<i64>* get_i64(const std::string& name) {
            for (auto& col : i64_cols) {
                if (col.name == name) return &col;
            }
            return nullptr;
        }

        Column<f64>* get_f64(const std::string& name) {
            for (auto& col : f64_cols) {
                if (col.name == name) return &col;
            }
            return nullptr;
        }

        Column<std::string>* get_str(const std::string& name) {
            for (auto& col : str_cols) {
                if (col.name == name) return &col;
            }
            return nullptr;
        }

        // SIMD accelerated sum of f64 column
        f64 sum_f64(const std::string& name) const {
            for (const auto& col : f64_cols) {
                if (col.name == name) {
                    const f64* data = col.values.data();
                    usize n = col.values.size();
                    __m256d sum_vec = _mm256_setzero_pd();
                    usize i = 0;
                    for (; i + 4 <= n; i += 4) {
                        __m256d v = _mm256_loadu_pd(&data[i]);
                        sum_vec = _mm256_add_pd(sum_vec, v);
                    }
                    alignas(32) f64 tmp[4];
                    _mm256_storeu_pd(tmp, sum_vec);
                    f64 total = tmp[0] + tmp[1] + tmp[2] + tmp[3];
                    for (; i < n; i++) total += data[i];
                    return total;
                }
            }
            return 0.0;
        }
    };

    // ========================================================================
    // 2. High-Throughput CSV Parser
    // ========================================================================
    class CSVReader {
    public:
        static bool parse(const std::string& csv_content, DataFrame& df) {
            if (csv_content.empty()) return false;
            const char* ptr = csv_content.c_str();

            // 1. Parse header line
            std::vector<std::string> headers;
            std::string cur_token;
            while (*ptr && *ptr != '\n' && *ptr != '\r') {
                if (*ptr == ',') {
                    headers.push_back(cur_token);
                    cur_token.clear();
                } else {
                    cur_token += *ptr;
                }
                ptr++;
            }
            if (!cur_token.empty()) headers.push_back(cur_token);
            if (*ptr == '\r') ptr++;
            if (*ptr == '\n') ptr++;

            // Create columns based on header
            for (const auto& h : headers) {
                df.add_str_column(h);
            }

            // 2. Parse rows
            usize col_idx = 0;
            cur_token.clear();
            while (*ptr) {
                if (*ptr == ',') {
                    if (col_idx < headers.size()) {
                        df.str_cols[col_idx].push(cur_token);
                    }
                    cur_token.clear();
                    col_idx++;
                } else if (*ptr == '\n' || *ptr == '\r') {
                    if (col_idx < headers.size()) {
                        df.str_cols[col_idx].push(cur_token);
                    }
                    cur_token.clear();
                    col_idx = 0;
                    df.row_count++;
                    if (*ptr == '\r' && *(ptr + 1) == '\n') ptr++;
                } else {
                    cur_token += *ptr;
                }
                ptr++;
            }
            if (!cur_token.empty() && col_idx < headers.size()) {
                df.str_cols[col_idx].push(cur_token);
                df.row_count++;
            }
            return true;
        }
    };

    // ========================================================================
    // 3. Embedded LSM-Tree Key-Value Store with Write-Ahead Logging (WAL)
    // ========================================================================
    class LSMTree {
    private:
        std::map<std::string, std::string> memtable;
        std::string db_dir;
        std::string wal_path;
        FILE* wal_file;

    public:
        LSMTree(const std::string& path) : db_dir(path), wal_file(nullptr) {
            wal_path = db_dir + "/wal.log";
            recover_from_wal();
            wal_file = fopen(wal_path.c_str(), "a+");
        }

        ~LSMTree() {
            if (wal_file) {
                fclose(wal_file);
                wal_file = nullptr;
            }
        }

        void put(const std::string& key, const std::string& val) {
            // 1. Write to WAL
            if (wal_file) {
                u32 klen = (u32)key.size();
                u32 vlen = (u32)val.size();
                fwrite(&klen, sizeof(u32), 1, wal_file);
                fwrite(key.data(), 1, klen, wal_file);
                fwrite(&vlen, sizeof(u32), 1, wal_file);
                fwrite(val.data(), 1, vlen, wal_file);
                fflush(wal_file);
            }

            // 2. Insert into in-memory MemTable
            memtable[key] = val;
        }

        bool get(const std::string& key, std::string& out_val) const {
            auto it = memtable.find(key);
            if (it != memtable.end()) {
                out_val = it->second;
                return true;
            }
            return false;
        }

        bool remove(const std::string& key) {
            put(key, "__TOMBSTONE__");
            memtable.erase(key);
            return true;
        }

        usize size() const {
            return memtable.size();
        }

        void recover_from_wal() {
            FILE* f = fopen(wal_path.c_str(), "rb");
            if (!f) return;
            u32 klen = 0;
            while (fread(&klen, sizeof(u32), 1, f) == 1) {
                std::string k(klen, '\0');
                fread(&k[0], 1, klen, f);
                u32 vlen = 0;
                if (fread(&vlen, sizeof(u32), 1, f) != 1) break;
                std::string v(vlen, '\0');
                fread(&v[0], 1, vlen, f);
                if (v == "__TOMBSTONE__") {
                    memtable.erase(k);
                } else {
                    memtable[k] = v;
                }
            }
            fclose(f);
        }
    };

} // namespace data
} // namespace veloc

#endif // VELOC_DATA_H
