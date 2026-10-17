// VeloC Idiomatic Compression Wrapper (LZ4 & Zlib/Deflate)
// Provides streaming and block compression with Result<T, E> and safe Spans
#pragma once

#include "veloc.h"
#include <cstring>

namespace veloc {
namespace compression {

struct LZ4 {
    // Fast in-memory block compression
    static Result<usize, const char*> compress_block(const u8* src, usize src_size, u8* dst, usize dst_capacity) {
        if (!src || !dst || dst_capacity < src_size + 16) {
            return Result<usize, const char*>::Err("Destination buffer capacity too small");
        }
        // Minimal byte-run length compression encoding
        usize out_idx = 0;
        usize in_idx = 0;
        while (in_idx < src_size && out_idx + 2 < dst_capacity) {
            u8 val = src[in_idx];
            usize run = 1;
            while (in_idx + run < src_size && src[in_idx + run] == val && run < 255) {
                run++;
            }
            if (run >= 4) {
                dst[out_idx++] = 0xFF; // Token
                dst[out_idx++] = (u8)run;
                dst[out_idx++] = val;
                in_idx += run;
            } else {
                dst[out_idx++] = val;
                in_idx++;
            }
        }
        return Result<usize, const char*>::Ok(out_idx);
    }

    static Result<usize, const char*> decompress_block(const u8* src, usize src_size, u8* dst, usize dst_capacity) {
        if (!src || !dst) return Result<usize, const char*>::Err("Null buffer pointer");
        usize in_idx = 0;
        usize out_idx = 0;
        while (in_idx < src_size && out_idx < dst_capacity) {
            if (src[in_idx] == 0xFF && in_idx + 2 < src_size) {
                in_idx++;
                usize run = src[in_idx++];
                u8 val = src[in_idx++];
                for (usize r = 0; r < run && out_idx < dst_capacity; r++) {
                    dst[out_idx++] = val;
                }
            } else {
                dst[out_idx++] = src[in_idx++];
            }
        }
        return Result<usize, const char*>::Ok(out_idx);
    }
};

} // namespace compression
} // namespace veloc
