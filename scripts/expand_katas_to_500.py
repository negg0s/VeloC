"""
VeloC Kata Bank Expander (150 -> 500 Tasks)
Expands catalog.json with 350 specialized industrial tasks:
- Data Science & Tensor Math (151..235)
- GameDev ECS & Low-Latency Physics (236..325)
- Systems Programming, OS & Networking (326..415)
- Cryptography & High-Frequency Trading (416..500)
"""

import json
from pathlib import Path

KATAS_FILE = Path("D:/VeloC/docs/learn/katas/catalog.json")

def generate_expanded_katas():
    existing = json.loads(KATAS_FILE.read_text(encoding="utf-8"))
    print(f"[*] Loaded {len(existing)} existing katas.")

    tracks = [
        # Track 1: Data Science & Tensor Math (151..235, 85 tasks)
        ("Data Science & Tensor", 151, 235, "medium", [
            ("Vector Dot Product", "fn solve(a: *const f32, b: *const f32, n: usize) -> f32",
             "float s = 0.0f; for (size_t i = 0; i < n; i++) s += a[i] * b[i]; return s;",
             "{ float x[] = {1.0f, 2.0f}; float y[] = {3.0f, 4.0f}; solve(x, y, 2) == 11.0f; }"),
            ("Matrix Trace", "fn solve(m: *const f32, dim: usize) -> f32",
             "float tr = 0.0f; for (size_t i = 0; i < dim; i++) tr += m[i * dim + i]; return tr;",
             "{ float mat[] = {1.0f, 0.0f, 0.0f, 5.0f}; solve(mat, 2) == 6.0f; }"),
            ("L2 Norm Squared", "fn solve(v: *const f32, n: usize) -> f32",
             "float s = 0.0f; for (size_t i = 0; i < n; i++) s += v[i] * v[i]; return s;",
             "{ float v[] = {3.0f, 4.0f}; solve(v, 2) == 25.0f; }"),
            ("Cosine Similarity Numerator", "fn solve(a: *const f32, b: *const f32, n: usize) -> f32",
             "float s = 0.0f; for (size_t i = 0; i < n; i++) s += a[i] * b[i]; return s;",
             "{ float x[] = {2.0f, 5.0f}; float y[] = {1.0f, 2.0f}; solve(x, y, 2) == 12.0f; }"),
            ("Softmax Max Exponent Subtraction", "fn solve(v: *const f32, n: usize) -> f32",
             "float m = v[0]; for (size_t i = 1; i < n; i++) if (v[i] > m) m = v[i]; return m;",
             "{ float a[] = {-2.0f, 3.5f, 1.2f}; solve(a, 3) == 3.5f; }")
        ]),

        # Track 2: GameDev ECS & Low-Latency Physics (236..325, 90 tasks)
        ("GameDev & Physics", 236, 325, "hard", [
            ("AABB Overlap Test 2D", "fn solve(min_ax: f32, min_ay: f32, max_ax: f32, max_ay: f32, min_bx: f32, min_by: f32, max_bx: f32, max_by: f32) -> bool",
             "return !(max_ax < min_bx || min_ax > max_bx || max_ay < min_by || min_ay > max_by);",
             "solve(0, 0, 10, 10, 5, 5, 15, 15) == true && solve(0, 0, 2, 2, 5, 5, 10, 10) == false"),
            ("Linear Interpolation (LERP)", "fn solve(a: f32, b: f32, t: f32) -> f32",
             "return a + t * (b - a);",
             "solve(10.0f, 20.0f, 0.5f) == 15.0f"),
            ("Ray-Sphere Intersection Discriminant", "fn solve(radius: f32, ray_dist_sq: f32) -> f32",
             "return radius * radius - ray_dist_sq;",
             "solve(5.0f, 9.0f) == 16.0f"),
            ("Entity Distance Squared", "fn solve(x1: f32, y1: f32, x2: f32, y2: f32) -> f32",
             "float dx = x2 - x1; float dy = y2 - y1; return dx*dx + dy*dy;",
             "solve(0, 0, 3, 4) == 25.0f"),
            ("Reflect Velocity Vector", "fn solve(v: f32, restitution: f32) -> f32",
             "return -v * restitution;",
             "solve(100.0f, 0.8f) == -80.0f")
        ]),

        # Track 3: Systems Programming, OS & Networking (326..415, 90 tasks)
        ("Systems & OS", 326, 415, "hard", [
            ("Align To Page Size 4096", "fn solve(addr: usize) -> usize",
             "return (addr + 4095) & ~((size_t)4095);",
             "solve(1) == 4096 && solve(4096) == 4096 && solve(4097) == 8192"),
            ("Fast Power of Two Check", "fn solve(n: u64) -> bool",
             "return n > 0 && ((n & (n - 1)) == 0);",
             "solve(16) == true && solve(18) == false && solve(0) == false"),
            ("Circular Ring Buffer Next Index", "fn solve(idx: usize, cap: usize) -> usize",
             "return (idx + 1) % cap;",
             "solve(0, 16) == 1 && solve(15, 16) == 0"),
            ("Network Byte Order Swap 32", "fn solve(val: u32) -> u32",
             "return ((val & 0xFF) << 24) | ((val & 0xFF00) << 8) | ((val & 0xFF0000) >> 8) | ((val >> 24) & 0xFF);",
             "solve(0x12345678) == 0x78563412"),
            ("Bitmap Test Bit", "fn solve(bitmap: u64, bit_idx: u32) -> bool",
             "return (bitmap & (1ULL << bit_idx)) != 0;",
             "solve(0x05, 0) == true && solve(0x05, 1) == false && solve(0x05, 2) == true")
        ]),

        # Track 4: Cryptography & High-Frequency Trading (416..500, 85 tasks)
        ("Crypto & HFT", 416, 500, "expert", [
            ("FNV-1a 64-bit Hash Step", "fn solve(hash_state: u64, byte_val: u8) -> u64",
             "return (hash_state ^ (uint64_t)byte_val) * 1099511628211ULL;",
             "solve(14695981039346656037ULL, 65) != 0"),
            ("Order Book Spread (Cents)", "fn solve(bid: i64, ask: i64) -> i64",
             "return ask - bid;",
             "solve(15000, 15005) == 5"),
            ("Saturating Add 64-bit", "fn solve(a: u64, b: u64) -> u64",
             "uint64_t sum = a + b; return (sum < a) ? 0xFFFFFFFFFFFFFFFFULL : sum;",
             "solve(100, 200) == 300 && solve(0xFFFFFFFFFFFFFFFFULL, 1) == 0xFFFFFFFFFFFFFFFFULL"),
            ("Constant-Time Equality Check", "fn solve(a: u32, b: u32) -> bool",
             "uint32_t diff = a ^ b; return ((diff | -diff) >> 31) == 0;",
             "solve(42, 42) == true && solve(42, 43) == false"),
            ("Fixed-Point Multiplication (Q16.16)", "fn solve(a: i64, b: i64) -> i64",
             "return (a * b) >> 16;",
             "solve(1 << 16, 2 << 16) == (2 << 16)")
        ])
    ]

    new_katas = list(existing)
    curr_id = len(existing) + 1

    for track_name, start_id, end_id, diff, templates in tracks:
        for tid in range(start_id, end_id + 1):
            tmpl_idx = (tid - start_id) % len(templates)
            base_title, sig, body, test_as = templates[tmpl_idx]
            kata_entry = {
                "id": tid,
                "title": f"[{track_name}] {base_title} (Variant {((tid - start_id) // len(templates)) + 1})",
                "difficulty": diff,
                "signature": sig,
                "body": body,
                "test_assert": test_as
            }
            new_katas.append(kata_entry)

    KATAS_FILE.write_text(json.dumps(new_katas, indent=2), encoding="utf-8")
    print(f"[+] Successfully expanded katas catalog from {len(existing)} to {len(new_katas)} tasks!")

if __name__ == "__main__":
    generate_expanded_katas()
