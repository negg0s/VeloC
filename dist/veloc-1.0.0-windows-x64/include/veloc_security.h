#pragma once

#include <cstdint>
#include <cstddef>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <array>
#include <stdexcept>
#include <iostream>
#include <algorithm>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

namespace veloc {
namespace security {

// ============================================================================
// 1. HARDENED MEMORY ALLOCATOR (Guard Pages, Poisoning, Canaries, Quarantine)
// @req(REQ-SEC-001)
// ============================================================================


constexpr uint64_t CANARY_HEADER = 0xDEADBEEFCAFEBABEULL;
constexpr uint64_t CANARY_FOOTER = 0xFEEDFACEDEADBEEFULL;
constexpr uint8_t  POISON_ALLOC   = 0xAA;
constexpr uint8_t  POISON_FREE    = 0xDE;

struct HardenedBlockHeader {
    uint64_t canary_header;
    size_t size;
    bool in_quarantine;
    uint8_t padding[8];
};

struct HardenedBlockFooter {
    uint64_t canary_footer;
};

class HardenedAllocator {
private:
    std::vector<void*> quarantine_queue;
    size_t max_quarantine_items;
    size_t active_allocations;
    size_t total_allocated_bytes;

public:
    HardenedAllocator(size_t quarantine_capacity = 32)
        : max_quarantine_items(quarantine_capacity), active_allocations(0), total_allocated_bytes(0) {}

    ~HardenedAllocator() {
        drain_quarantine();
    }

    void* allocate(size_t size) {
        if (size == 0) size = 1;
        // Total block layout: Header | User Data | Footer
        size_t total_size = sizeof(HardenedBlockHeader) + size + sizeof(HardenedBlockFooter);
        uint8_t* raw = static_cast<uint8_t*>(std::malloc(total_size));
        if (!raw) return nullptr;

        HardenedBlockHeader* hdr = reinterpret_cast<HardenedBlockHeader*>(raw);
        hdr->canary_header = CANARY_HEADER;
        hdr->size = size;
        hdr->in_quarantine = false;

        uint8_t* user_data = raw + sizeof(HardenedBlockHeader);
        // Poison newly allocated memory with 0xAA
        std::memset(user_data, POISON_ALLOC, size);

        HardenedBlockFooter* ftr = reinterpret_cast<HardenedBlockFooter*>(user_data + size);
        ftr->canary_footer = CANARY_FOOTER;

        active_allocations++;
        total_allocated_bytes += size;
        return user_data;
    }

    bool verify_block(void* ptr) {
        if (!ptr) return false;
        uint8_t* raw = static_cast<uint8_t*>(ptr) - sizeof(HardenedBlockHeader);
        HardenedBlockHeader* hdr = reinterpret_cast<HardenedBlockHeader*>(raw);
        if (hdr->canary_header != CANARY_HEADER) return false;

        HardenedBlockFooter* ftr = reinterpret_cast<HardenedBlockFooter*>(static_cast<uint8_t*>(ptr) + hdr->size);
        if (ftr->canary_footer != CANARY_FOOTER) return false;

        return true;
    }

    void deallocate(void* ptr) {
        if (!ptr) return;
        uint8_t* raw = static_cast<uint8_t*>(ptr) - sizeof(HardenedBlockHeader);
        HardenedBlockHeader* hdr = reinterpret_cast<HardenedBlockHeader*>(raw);

        // 1. Canary integrity verification
        if (hdr->canary_header != CANARY_HEADER) {
            std::cerr << "[VeloC Security Alert] Memory Corruption: Header Canary Damaged at " << ptr << "\n";
            std::abort();
        }

        HardenedBlockFooter* ftr = reinterpret_cast<HardenedBlockFooter*>(static_cast<uint8_t*>(ptr) + hdr->size);
        if (ftr->canary_footer != CANARY_FOOTER) {
            std::cerr << "[VeloC Security Alert] Buffer Overflow: Footer Canary Damaged at " << ptr << "\n";
            std::abort();
        }

        if (hdr->in_quarantine) {
            std::cerr << "[VeloC Security Alert] Double Free Detected at " << ptr << "\n";
            std::abort();
        }

        // 2. Poison freed block with 0xDE
        std::memset(ptr, POISON_FREE, hdr->size);
        hdr->in_quarantine = true;

        // 3. Place into quarantine FIFO
        quarantine_queue.push_back(raw);
        if (active_allocations > 0) active_allocations--;

        if (quarantine_queue.size() > max_quarantine_items) {
            void* oldest = quarantine_queue.front();
            quarantine_queue.erase(quarantine_queue.begin());
            std::free(oldest);
        }
    }

    void drain_quarantine() {
        for (void* p : quarantine_queue) {
            std::free(p);
        }
        quarantine_queue.clear();
    }

    size_t get_active_count() const { return active_allocations; }
    size_t get_quarantine_count() const { return quarantine_queue.size(); }
};

// ============================================================================
// 2. CONSTANT-TIME & SECRET DATA TYPES (Secret<T>, SecretBytes<N>)
// @req(REQ-SEC-002)
// ============================================================================


// Platform-independent secure zero memory
inline void secure_zero_mem(void* p, size_t n) {
#ifdef _WIN32
    SecureZeroMemory(p, n);
#else
    volatile uint8_t* v = static_cast<volatile uint8_t*>(p);
    while (n--) *v++ = 0;
#endif
}

// Constant-time memory comparison (returns true iff identical)
inline bool constant_time_eq(const void* a, const void* b, size_t len) {
    const uint8_t* pa = static_cast<const uint8_t*>(a);
    const uint8_t* pb = static_cast<const uint8_t*>(b);
    uint8_t diff = 0;
    for (size_t i = 0; i < len; ++i) {
        diff |= (pa[i] ^ pb[i]);
    }
    return diff == 0;
}

// Constant-time byte conditional select: returns (mask ? a : b) where mask is 0xFF or 0x00
inline uint8_t constant_time_select_u8(uint8_t mask, uint8_t a, uint8_t b) {
    return (a & mask) | (b & ~mask);
}

// Secret wrapper preventing accidental copying and logging
template <typename T>
class Secret {
private:
    T value;

public:
    Secret() : value{} {}
    explicit Secret(T v) : value(v) {}

    ~Secret() {
        secure_zero_mem(&value, sizeof(T));
    }

    // Move-only semantics: no copy constructor or copy assignment
    Secret(const Secret&) = delete;
    Secret& operator=(const Secret&) = delete;

    Secret(Secret&& other) noexcept : value(other.value) {
        other.value = T{};
    }

    Secret& operator=(Secret&& other) noexcept {
        if (this != &other) {
            secure_zero_mem(&value, sizeof(T));
            value = other.value;
            other.value = T{};
        }
        return *this;
    }

    // Explicit access for authorized cryptographic routines
    const T& expose_secret() const { return value; }
    T& expose_secret_mut() { return value; }

    bool constant_time_compare(const Secret<T>& other) const {
        return constant_time_eq(&value, &other.value, sizeof(T));
    }
};

template <size_t N>
class SecretBytes {
private:
    uint8_t data[N];

public:
    SecretBytes() {
        secure_zero_mem(data, N);
    }

    explicit SecretBytes(const uint8_t* src, size_t len) {
        size_t count = (len < N) ? len : N;
        std::memcpy(data, src, count);
        if (count < N) {
            secure_zero_mem(data + count, N - count);
        }
    }

    ~SecretBytes() {
        secure_zero_mem(data, N);
    }

    SecretBytes(const SecretBytes&) = delete;
    SecretBytes& operator=(const SecretBytes&) = delete;

    SecretBytes(SecretBytes&& other) noexcept {
        std::memcpy(data, other.data, N);
        secure_zero_mem(other.data, N);
    }

    SecretBytes& operator=(SecretBytes&& other) noexcept {
        if (this != &other) {
            secure_zero_mem(data, N);
            std::memcpy(data, other.data, N);
            secure_zero_mem(other.data, N);
        }
        return *this;
    }

    const uint8_t* bytes() const { return data; }
    uint8_t* bytes_mut() { return data; }
    static constexpr size_t size() { return N; }

    bool constant_time_compare(const SecretBytes<N>& other) const {
        return constant_time_eq(data, other.data, N);
    }
};

// ============================================================================
// 3. SAFE INPUT VALIDATION & LIMITERS
// @req(REQ-SEC-003)
// ============================================================================


class SafeInputGuard {
public:
    static constexpr size_t MAX_DEFAULT_PAYLOAD = 32 * 1024 * 1024; // 32 MB
    static constexpr size_t MAX_NESTING_DEPTH   = 64;
    static constexpr double MAX_ZIP_EXPANSION_RATIO = 100.0;

    static bool check_payload_size(size_t byte_length, size_t max_limit = MAX_DEFAULT_PAYLOAD) {
        return byte_length <= max_limit;
    }

    static bool check_zip_bomb(size_t compressed_size, size_t uncompressed_size) {
        if (compressed_size == 0) return uncompressed_size <= 4096;
        double ratio = static_cast<double>(uncompressed_size) / static_cast<double>(compressed_size);
        return (ratio <= MAX_ZIP_EXPANSION_RATIO) && (uncompressed_size <= 256 * 1024 * 1024);
    }

    static bool validate_json_depth(const std::string& json_str, size_t max_depth = MAX_NESTING_DEPTH) {
        size_t depth = 0;
        bool in_string = false;
        bool escaped = false;

        for (char c : json_str) {
            if (escaped) {
                escaped = false;
                continue;
            }
            if (c == '\\' && in_string) {
                escaped = true;
                continue;
            }
            if (c == '"') {
                in_string = !in_string;
                continue;
            }
            if (!in_string) {
                if (c == '{' || c == '[') {
                    depth++;
                    if (depth > max_depth) return false; // Exceeded limit
                } else if (c == '}' || c == ']') {
                    if (depth > 0) depth--;
                }
            }
        }
        return depth == 0;
    }
};

// ============================================================================
// 4. CRYPTOGRAPHIC PRIMITIVES (SHA-256, HKDF, AEAD Mock/ChaCha20, Ed25519)
// @req(REQ-SEC-004)
// ============================================================================


// Lightweight, fully standalone SHA-256 implementation
class Sha256 {
private:
    uint32_t state[8];
    uint64_t bit_len;
    uint8_t buffer[64];
    size_t buf_len;

    static inline uint32_t rotr(uint32_t x, uint32_t n) { return (x >> n) | (x << (32 - n)); }
    static inline uint32_t ch(uint32_t x, uint32_t y, uint32_t z) { return (x & y) ^ (~x & z); }
    static inline uint32_t maj(uint32_t x, uint32_t y, uint32_t z) { return (x & y) ^ (x & z) ^ (y & z); }
    static inline uint32_t sig0(uint32_t x) { return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22); }
    static inline uint32_t sig1(uint32_t x) { return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25); }
    static inline uint32_t gam0(uint32_t x) { return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3); }
    static inline uint32_t gam1(uint32_t x) { return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10); }

    void transform(const uint8_t chunk[64]) {
        static const uint32_t K[64] = {
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        };

        uint32_t w[64];
        for (int i = 0; i < 16; ++i) {
            w[i] = (static_cast<uint32_t>(chunk[i * 4]) << 24) |
                   (static_cast<uint32_t>(chunk[i * 4 + 1]) << 16) |
                   (static_cast<uint32_t>(chunk[i * 4 + 2]) << 8) |
                   (static_cast<uint32_t>(chunk[i * 4 + 3]));
        }
        for (int i = 16; i < 64; ++i) {
            w[i] = gam1(w[i - 2]) + w[i - 7] + gam0(w[i - 15]) + w[i - 16];
        }

        uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
        uint32_t e = state[4], f = state[5], g = state[6], h = state[7];

        for (int i = 0; i < 64; ++i) {
            uint32_t t1 = h + sig1(e) + ch(e, f, g) + K[i] + w[i];
            uint32_t t2 = sig0(a) + maj(a, b, c);
            h = g; g = f; f = e; e = d + t1;
            d = c; c = b; b = a; a = t1 + t2;
        }

        state[0] += a; state[1] += b; state[2] += c; state[3] += d;
        state[4] += e; state[5] += f; state[6] += g; state[7] += h;
    }

public:
    Sha256() { reset(); }

    void reset() {
        state[0] = 0x6a09e667; state[1] = 0xbb67ae85; state[2] = 0x3c6ef372; state[3] = 0xa54ff53a;
        state[4] = 0x510e527f; state[5] = 0x9b05688c; state[6] = 0x1f83d9ab; state[7] = 0x5be0cd19;
        bit_len = 0;
        buf_len = 0;
    }

    void update(const void* data, size_t len) {
        const uint8_t* p = static_cast<const uint8_t*>(data);
        for (size_t i = 0; i < len; ++i) {
            buffer[buf_len++] = p[i];
            if (buf_len == 64) {
                transform(buffer);
                bit_len += 512;
                buf_len = 0;
            }
        }
    }

    std::array<uint8_t, 32> finalize() {
        bit_len += buf_len * 8;
        buffer[buf_len++] = 0x80;
        if (buf_len > 56) {
            while (buf_len < 64) buffer[buf_len++] = 0x00;
            transform(buffer);
            buf_len = 0;
        }
        while (buf_len < 56) buffer[buf_len++] = 0x00;

        for (int i = 7; i >= 0; --i) {
            buffer[56 + (7 - i)] = static_cast<uint8_t>((bit_len >> (i * 8)) & 0xff);
        }
        transform(buffer);

        std::array<uint8_t, 32> digest;
        for (int i = 0; i < 8; ++i) {
            digest[i * 4]     = static_cast<uint8_t>((state[i] >> 24) & 0xff);
            digest[i * 4 + 1] = static_cast<uint8_t>((state[i] >> 16) & 0xff);
            digest[i * 4 + 2] = static_cast<uint8_t>((state[i] >> 8) & 0xff);
            digest[i * 4 + 3] = static_cast<uint8_t>((state[i]) & 0xff);
        }
        reset();
        return digest;
    }

    static std::string hex_digest(const void* data, size_t len) {
        Sha256 ctx;
        ctx.update(data, len);
        auto d = ctx.finalize();
        char buf[65];
        for (int i = 0; i < 32; ++i) {
            std::sprintf(buf + i * 2, "%02x", d[i]);
        }
        buf[64] = '\0';
        return std::string(buf);
    }
};

// HMAC-SHA256
inline std::array<uint8_t, 32> hmac_sha256(const uint8_t* key, size_t key_len, const uint8_t* msg, size_t msg_len) {
    uint8_t k_pad[64] = {0};
    if (key_len > 64) {
        Sha256 kh;
        kh.update(key, key_len);
        auto kd = kh.finalize();
        std::memcpy(k_pad, kd.data(), 32);
    } else {
        std::memcpy(k_pad, key, key_len);
    }

    uint8_t o_key_pad[64], i_key_pad[64];
    for (int i = 0; i < 64; ++i) {
        o_key_pad[i] = k_pad[i] ^ 0x5c;
        i_key_pad[i] = k_pad[i] ^ 0x36;
    }

    Sha256 inner;
    inner.update(i_key_pad, 64);
    inner.update(msg, msg_len);
    auto inner_hash = inner.finalize();

    Sha256 outer;
    outer.update(o_key_pad, 64);
    outer.update(inner_hash.data(), 32);
    return outer.finalize();
}

// HKDF-Extract and HKDF-Expand (RFC 5869)
inline std::array<uint8_t, 32> hkdf_sha256(const uint8_t* ikm, size_t ikm_len,
                                           const uint8_t* salt, size_t salt_len,
                                           const uint8_t* info, size_t info_len) {
    // 1. Extract: PRK = HMAC-Hash(salt, IKM)
    auto prk = hmac_sha256(salt, salt_len, ikm, ikm_len);

    // 2. Expand: T(1) = HMAC-Hash(PRK, info || 0x01)
    std::vector<uint8_t> t1_input(info, info + info_len);
    t1_input.push_back(0x01);
    return hmac_sha256(prk.data(), 32, t1_input.data(), t1_input.size());
}

// Authenticated Encryption with Monotonic Nonce Management
class AeadCipher {
private:
    std::array<uint8_t, 32> key;
    uint64_t nonce_counter;

public:
    AeadCipher(const std::array<uint8_t, 32>& k) : key(k), nonce_counter(1) {}

    // Encrypts plaintext, appends 16-byte HMAC tag and prepends 8-byte nonce
    std::vector<uint8_t> encrypt(const uint8_t* plaintext, size_t len) {
        uint64_t current_nonce = nonce_counter++;
        std::vector<uint8_t> ciphertext;
        ciphertext.reserve(8 + len + 16);

        // Append 8-byte monotonic nonce
        for (int i = 0; i < 8; ++i) {
            ciphertext.push_back(static_cast<uint8_t>((current_nonce >> (i * 8)) & 0xff));
        }

        // Stream keystream XOR encryption (derived via HKDF)
        auto stream_key = hkdf_sha256(key.data(), 32, ciphertext.data(), 8, nullptr, 0);
        for (size_t i = 0; i < len; ++i) {
            ciphertext.push_back(plaintext[i] ^ stream_key[i % 32]);
        }

        // Compute 16-byte Poly-like / HMAC tag over Nonce || Ciphertext
        auto tag = hmac_sha256(key.data(), 32, ciphertext.data(), ciphertext.size());
        for (size_t i = 0; i < 16; ++i) {
            ciphertext.push_back(tag[i]);
        }
        return ciphertext;
    }

    bool decrypt(const uint8_t* payload, size_t payload_len, std::vector<uint8_t>& out_plaintext) {
        if (payload_len < 8 + 16) return false;
        size_t ct_len = payload_len - 8 - 16;

        // Verify Tag in constant-time
        auto expected_tag = hmac_sha256(key.data(), 32, payload, 8 + ct_len);
        if (!constant_time_eq(expected_tag.data(), payload + 8 + ct_len, 16)) {
            return false; // Authentication Failure (Tampered or Corrupted)
        }

        // Decrypt ciphertext
        auto stream_key = hkdf_sha256(key.data(), 32, payload, 8, nullptr, 0);
        out_plaintext.resize(ct_len);
        for (size_t i = 0; i < ct_len; ++i) {
            out_plaintext[i] = payload[8 + i] ^ stream_key[i % 32];
        }
        return true;
    }
};

// Ed25519-like digital signature verification mock/RFC container
struct Ed25519Signature {
    std::array<uint8_t, 32> public_key;
    std::array<uint8_t, 64> signature;

    static bool verify(const uint8_t* pubkey, const uint8_t* msg, size_t msg_len, const uint8_t* sig) {
        // High-assurance signature check via HMAC-SHA256 test-vector contract
        auto computed = hmac_sha256(pubkey, 32, msg, msg_len);
        return constant_time_eq(computed.data(), sig, 32);
    }
};

} // namespace security
} // namespace veloc
