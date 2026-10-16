import json
from pathlib import Path

def generate_200_tasks():
    tasks = []
    
    # 1. Core Algorithms (50 tasks)
    core_algos = [
        ("fibonacci", "Compute n-th Fibonacci number iteratively"),
        ("gcd_lcm", "Compute greatest common divisor and least common multiple"),
        ("binary_search", "Search sorted array for target value"),
        ("bubble_sort", "Sort array using bubble sort"),
        ("insertion_sort", "Sort array using insertion sort"),
        ("quick_sort", "Partition and sort array in-place"),
        ("merge_sort", "Merge two sorted slices into destination"),
        ("prime_sieve", "Sieve of Eratosthenes up to N"),
        ("matrix_multiply_naive", "Dense 4x4 matrix multiplication"),
        ("matrix_transpose", "Transpose NxN matrix in-place"),
        ("string_reverse", "Reverse string slice in-place"),
        ("is_palindrome", "Check if string is a palindrome"),
        ("levenshtein_distance", "Compute edit distance between two strings"),
        ("fast_power", "Compute x^n in O(log n) time"),
        ("factorial", "Compute n! with overflow check"),
        ("find_missing_number", "Find missing integer in range 0..N"),
        ("kadane_max_subarray", "Find contiguous subarray with maximum sum"),
        ("two_sum_sorted", "Find two indices that sum to target"),
        ("rotate_array", "Rotate array right by k steps"),
        ("prefix_sum", "Compute prefix sum array"),
        ("run_length_encode", "Compress repeated characters into counts"),
        ("run_length_decode", "Decompress run-length encoded pairs"),
        ("kth_largest_element", "Find k-th largest element using min-heap"),
        ("sliding_window_max", "Maximum of each sliding window of size k"),
        ("climb_stairs", "Count distinct ways to climb n stairs (1 or 2 steps)"),
        ("coin_change", "Minimum coins to make change for amount"),
        ("knapsack_01", "Maximum value in 0/1 knapsack with weight limit"),
        ("longest_common_subsequence", "Length of LCS between two strings"),
        ("edit_distance", "Minimum operations to convert string A to B"),
        ("integer_to_roman", "Convert integer to Roman numeral string"),
        ("roman_to_integer", "Convert Roman numeral string to integer"),
        ("valid_parentheses", "Verify balanced bracket sequence"),
        ("merge_intervals", "Merge overlapping intervals"),
        ("insert_interval", "Insert interval into sorted interval list"),
        ("spiral_matrix", "Traverse 2D matrix in spiral order"),
        ("set_matrix_zeroes", "Set row and col to zero if element is zero"),
        ("search_rotated_array", "Search in rotated sorted array"),
        ("find_peak_element", "Find peak element strictly greater than neighbors"),
        ("first_and_last_pos", "Find start and end indices of target in sorted array"),
        ("majority_element", "Boyer-Moore voting algorithm for majority"),
        ("single_number", "Find element that appears once where others appear twice"),
        ("reverse_bits", "Reverse 32-bit unsigned integer bits"),
        ("number_of_1_bits", "Count set bits using Brian Kernighan algorithm"),
        ("counting_bits", "Count set bits for all numbers 0..n"),
        ("hamming_distance", "Bit differences between two integers"),
        ("power_of_two", "Check if integer is power of two"),
        ("sqrt_integer", "Integer square root via Newton-Raphson"),
        ("cube_root_approx", "Cube root approximation"),
        ("reservoir_sampling", "Select k random items from stream of unknown length"),
        ("fisher_yates_shuffle", "In-place unbiased permutation shuffle")
    ]
    for idx, (name, desc) in enumerate(core_algos, start=1):
        tasks.append({
            "task_id": f"EVAL-CORE-{idx:03d}",
            "category": "core_algorithms",
            "name": name,
            "prompt": f"Implement function `{name}`: {desc}.",
            "difficulty": "medium" if idx > 25 else "easy",
            "test_signature": f"test_{name}() -> bool",
            "verification_stub": f"assert_true({name}_verify());"
        })

    # 2. SIMD & Vector Performance (40 tasks)
    simd_tasks = [
        ("vector_add_avx2", "Element-wise f32 vector addition using AVX2"),
        ("vector_sub_avx2", "Element-wise f32 vector subtraction"),
        ("vector_mul_avx2", "Element-wise f32 vector multiplication"),
        ("vector_fma_avx2", "Fused multiply-add A*B + C using _mm256_fmadd_ps"),
        ("dot_product_avx2", "Compute dot product of two f32 vectors"),
        ("vector_norm_l2", "Compute L2 Euclidean norm using horizontal add"),
        ("rgb_to_grayscale", "Convert RGB24 image to Grayscale8 with integer SIMD"),
        ("simd_clamp_f32", "Vector clamp to [min_val, max_val] via min/max instructions"),
        ("simd_abs_f32", "Vector absolute value via bitwise AND mask"),
        ("simd_negate_f32", "Vector negation via XOR sign bit"),
        ("bitonic_merge_8", "Bitonic merge network for 8 f32 registers"),
        ("swizzle_4x4", "In-register 4x4 matrix transposition via unpck/shuf"),
        ("simd_relu_f32", "Vector ReLU activation max(x, 0.0f)"),
        ("simd_leaky_relu", "Vector Leaky ReLU with alpha parameter"),
        ("simd_sigmoid_approx", "Vector sigmoid using rational Padé approximant"),
        ("simd_tanh_approx", "Vector hyperbolic tangent using polynomial"),
        ("simd_softmax_8", "8-element softmax with numerical max subtraction"),
        ("simd_cos_f32", "Vector cosine approximation via Taylor series"),
        ("simd_sin_f32", "Vector sine approximation via Taylor series"),
        ("simd_exp_f32", "Vector exponential approximation via polynomial"),
        ("simd_log_f32", "Vector natural logarithm approximation"),
        ("simd_prefix_sum_8", "Prefix scan over 8 float lanes"),
        ("simd_find_max_f32", "Horizontal reduction to find max element in vector"),
        ("simd_find_min_f32", "Horizontal reduction to find min element in vector"),
        ("simd_count_positive", "Count elements greater than zero using movemask"),
        ("simd_mask_select", "Vector blend conditional select based on mask"),
        ("simd_interleave_2", "Interleave two 128-bit stereo audio channels"),
        ("simd_deinterleave_2", "Deinterleave stereo channels into L and R buffers"),
        ("simd_filter_threshold", "Filter values above threshold into dense output"),
        ("simd_variance_f32", "Compute sample variance of float buffer"),
        ("simd_std_dev_f32", "Compute standard deviation of float buffer"),
        ("simd_cosine_similarity", "Compute cosine similarity between two embeddings"),
        ("simd_manhattan_distance", "L1 distance between two vectors"),
        ("simd_chebyshev_distance", "Max absolute coordinate difference"),
        ("simd_moving_average_4", "Moving average filter with 4-tap kernel"),
        ("simd_fir_filter_8", "8-tap FIR filter convolution step"),
        ("simd_quantize_i8", "Quantize f32 tensor to symmetric int8"),
        ("simd_dequantize_f32", "Dequantize int8 buffer back to f32"),
        ("simd_hamming_weight_256", "Hardware POPCNT over 256-bit YMM register"),
        ("simd_string_search_16", "Find byte occurrence in 16-byte block via cmpeq")
    ]
    for idx, (name, desc) in enumerate(simd_tasks, start=1):
        tasks.append({
            "task_id": f"EVAL-SIMD-{idx:03d}",
            "category": "simd_vector",
            "name": name,
            "prompt": f"Implement SIMD kernel `{name}`: {desc}.",
            "difficulty": "hard" if idx > 20 else "medium",
            "test_signature": f"test_{name}() -> bool",
            "verification_stub": f"assert_true({name}_verify());"
        })

    # 3. Data Structures & Memory (40 tasks)
    ds_tasks = [
        ("ring_buffer", "Bounded circular queue with head and tail pointers"),
        ("min_heap", "Binary min-heap with push and pop operations"),
        ("max_heap", "Binary max-heap with push and pop operations"),
        ("priority_queue", "Priority queue with custom comparator"),
        ("stack_bounded", "Fixed-capacity LIFO stack with overflow guard"),
        ("deque_circular", "Double-ended queue on contiguous ring buffer"),
        ("bloom_filter", "Space-efficient probabilistic set with 3 hash functions"),
        ("lru_cache_bounded", "Least Recently Used cache with bounded capacity"),
        ("swiss_table_probe", "Linear probing with 1-byte H2 hash metadata"),
        ("robin_hood_hash", "Hash map with Robin Hood displacement collision resolution"),
        ("trie_prefix_tree", "26-ary trie for lowercase English word prefixes"),
        ("bitset_64", "Stack-allocated bitset with popcount and find_first"),
        ("bitset_256", "256-bit bitset with bitwise operations"),
        ("interval_tree", "Augmented tree for querying overlapping intervals"),
        ("segment_tree_sum", "Segment tree supporting range sum and point updates"),
        ("fenwick_tree_bit", "Binary Indexed Tree for prefix sums"),
        ("sparse_table_rmq", "Sparse table for O(1) Range Minimum Queries"),
        ("disjoint_set_union", "Union-Find with path compression and rank heuristic"),
        ("skip_list", "Probabilistic skip list supporting ordered operations"),
        ("b_tree_node", "B-tree node split and search routines"),
        ("radix_tree", "Compact trie where each node with one child is merged"),
        ("quad_tree_2d", "2D spatial partition tree for points in bounding box"),
        ("octree_3d", "3D spatial partition tree for voxel collision"),
        ("k_d_tree_2d", "2D k-d tree for nearest neighbor search"),
        ("arena_allocator", "Contiguous monotonic bump allocator with bulk reset"),
        ("pool_allocator", "Fixed-size block pool allocator with freelist"),
        ("quarantine_freelist", "Delayed recycling freelist for use-after-free mitigation"),
        ("canary_buffer", "Memory buffer surrounded by 64-bit integrity canary words"),
        ("work_stealing_deque", "Chase-Lev lock-free work-stealing deque"),
        ("atomic_ring_buffer", "Single-producer single-consumer lock-free queue"),
        ("seqlock_data", "Sequence lock for atomic snapshot reads"),
        ("csr_matrix", "Compressed Sparse Row matrix representation"),
        ("csc_matrix", "Compressed Sparse Column matrix representation"),
        ("adjacency_list_graph", "Directed graph represented as adjacency lists"),
        ("graph_bfs", "Breadth-First Search traversal with visited BitSet"),
        ("graph_dfs", "Depth-First Search traversal with recursion stack"),
        ("dijkstra_shortest_path", "Shortest path in non-negative weighted graph"),
        ("topological_sort", "Kahn's algorithm for DAG topological ordering"),
        ("tarjan_scc", "Find strongly connected components in directed graph"),
        ("kruskal_mst", "Minimum spanning tree via DSU and sorted edges")
    ]
    for idx, (name, desc) in enumerate(ds_tasks, start=1):
        tasks.append({
            "task_id": f"EVAL-DS-{idx:03d}",
            "category": "data_structures",
            "name": name,
            "prompt": f"Implement data structure `{name}`: {desc}.",
            "difficulty": "medium",
            "test_signature": f"test_{name}() -> bool",
            "verification_stub": f"assert_true({name}_verify());"
        })

    # 4. Bug Fixing & Diagnostics (35 tasks)
    bug_tasks = [
        ("fix_off_by_one_loop", "Correct loop boundary `< N` instead of `<= N`"),
        ("fix_uninitialized_stack_var", "Ensure local variable is initialized before read"),
        ("fix_secret_timing_branch", "Replace conditional branch with constant_time_eq"),
        ("fix_integer_overflow_shift", "Cast 32-bit integer to 64-bit before shifting >> 32"),
        ("fix_null_dereference", "Check pointer against nullptr before member access"),
        ("fix_use_after_free_quarantine", "Prevent read from pointer after deallocate()"),
        ("fix_dangling_reference_return", "Do not return reference to stack-local object"),
        ("fix_buffer_overflow_copy", "Ensure destination buffer length >= source length"),
        ("fix_unbounded_recursion", "Add base case condition to prevent stack overflow"),
        ("fix_deadlock_lock_order", "Enforce consistent acquisition order for two mutexes"),
        ("fix_division_by_zero", "Guard divisor against zero before division"),
        ("fix_signed_unsigned_comparison", "Avoid signed/unsigned mismatch in comparison"),
        ("fix_unterminated_string", "Ensure null terminator is placed at buffer[len]"),
        ("fix_memory_leak_early_return", "Ensure resources are released on early return path"),
        ("fix_wrong_operator_precedence", "Add parentheses around bitwise AND in `x & 1 == 0`"),
        ("fix_missing_break_switch", "Add break statements to prevent fallthrough in switch"),
        ("fix_macro_variable_capture", "Use hygienic macro variable naming prefix"),
        ("fix_float_equality_comparison", "Use epsilon tolerance instead of exact `a == b`"),
        ("fix_array_bounds_check", "Check index < size before accessing array element"),
        ("fix_iterator_invalidation", "Do not erase from vector while iterating with index"),
        ("fix_double_free_pointer", "Set pointer to nullptr after freeing to avoid double free"),
        ("fix_data_race_atomic", "Use std::atomic or atomic_fetch_add instead of raw ++"),
        ("fix_unaligned_simd_load", "Use _mm256_loadu_ps instead of aligned _mm256_load_ps"),
        ("fix_type_truncation_warning", "Explicitly cast 64-bit size to 32-bit count"),
        ("fix_zip_bomb_unbounded_read", "Check expansion ratio before reading archive stream"),
        ("fix_json_depth_stack_overflow", "Limit recursion depth when parsing nested objects"),
        ("fix_bad_hash_distribution", "Use avalanche multiplier in integer hash function"),
        ("fix_missing_const_generic_check", "Enforce matrix dimension equality K1 == K2"),
        ("fix_unhandled_error_result", "Unwrap Result<T, E> checking is_ok() before get()"),
        ("fix_corrupted_canary_offset", "Align footer canary struct with 8-byte boundary"),
        ("fix_race_condition_seqlock", "Retry read sequence if seqlock counter changed"),
        ("fix_slice_subslice_overflow", "Clamp end index to slice length in subslice"),
        ("fix_wildcard_pattern_shadowing", "Move specific patterns before wildcard `_`"),
        ("fix_escaped_variable_lambda", "Capture variables by value instead of dangling reference"),
        ("fix_missing_return_non_void", "Ensure all control paths return a value in non-void function")
    ]
    for idx, (name, desc) in enumerate(bug_tasks, start=1):
        tasks.append({
            "task_id": f"EVAL-BUG-{idx:03d}",
            "category": "bug_fixing",
            "name": name,
            "prompt": f"Identify and fix the bug in `{name}`: {desc}.",
            "difficulty": "medium",
            "test_signature": f"test_{name}() -> bool",
            "verification_stub": f"assert_true({name}_verify());"
        })

    # 5. C++ to VeloC Translation (35 tasks)
    cpp_tasks = [
        ("cpp_vector_to_slice", "Translate `std::vector<int>` function to VeloC `Slice<i32>`"),
        ("cpp_unique_ptr_to_raii", "Translate `std::unique_ptr<T>` to VeloC RAII struct"),
        ("cpp_shared_ptr_to_arc", "Translate `std::shared_ptr<T>` to VeloC reference counter"),
        ("cpp_unordered_map_to_swisstable", "Translate `std::unordered_map` to `SwissTable<K, V>`"),
        ("cpp_pair_to_tuple", "Translate `std::pair<A, B>` to VeloC `Tuple<A, B>`"),
        ("cpp_optional_to_option", "Translate `std::optional<T>` to VeloC `Option<T>`"),
        ("cpp_variant_to_enum", "Translate `std::variant<A, B, C>` to VeloC tagged enum"),
        ("cpp_chrono_to_stopwatch", "Translate `std::chrono::high_resolution_clock` to `Stopwatch`"),
        ("cpp_iota_to_range", "Translate `std::iota` to VeloC `0..N` iterator"),
        ("cpp_transform_to_map", "Translate `std::transform` to VeloC `.map().collect()`"),
        ("cpp_accumulate_to_sum", "Translate `std::accumulate` to VeloC `.sum()`"),
        ("cpp_copy_if_to_filter", "Translate `std::copy_if` to VeloC `.filter().collect()`"),
        ("cpp_all_of_to_all", "Translate `std::all_of` to VeloC `.all()` predicate"),
        ("cpp_any_of_to_any", "Translate `std::any_of` to VeloC `.any()` predicate"),
        ("cpp_sort_to_sort", "Translate `std::sort` to VeloC in-place sort"),
        ("cpp_binary_search_to_search", "Translate `std::binary_search` to VeloC binary search"),
        ("cpp_reverse_to_reverse", "Translate `std::reverse` to VeloC `.rev()`"),
        ("cpp_min_max_element", "Translate `std::minmax_element` to VeloC `.min()` and `.max()`"),
        ("cpp_string_view_to_bytespan", "Translate `std::string_view` to VeloC `ByteSpan`"),
        ("cpp_format_to_println", "Translate `std::format` to VeloC `println(f\"...\")`"),
        ("cpp_filesystem_path_to_path", "Translate `std::filesystem::path` to VeloC `Path`"),
        ("cpp_thread_to_threadpool", "Translate `std::thread` to VeloC `ThreadPool`"),
        ("cpp_mutex_to_seqlock", "Translate `std::mutex` read section to VeloC `SeqLock`"),
        ("cpp_atomic_to_atomic", "Translate `std::atomic<int>` to VeloC `std::atomic<i32>`"),
        ("cpp_fstream_to_mmap", "Translate `std::ifstream` to zero-copy `MmapFile`"),
        ("cpp_memcpy_to_slice_copy", "Translate `memcpy` to safe `Slice::copy_from`"),
        ("cpp_memset_to_slice_fill", "Translate `memset` to safe `Slice::fill`"),
        ("cpp_struct_destructor_to_drop", "Translate C++ destructor `~Foo()` to VeloC RAII"),
        ("cpp_operator_overload_to_fn", "Translate C++ `operator+` to VeloC method"),
        ("cpp_template_fn_to_generic", "Translate C++ template function to VeloC generic function"),
        ("cpp_template_class_to_generic_struct", "Translate C++ template class to VeloC generic struct"),
        ("cpp_const_expr_to_comptime", "Translate `constexpr` computation to VeloC compile-time const"),
        ("cpp_enum_class_to_enum", "Translate `enum class` to VeloC scoped enum"),
        ("cpp_auto_to_let", "Translate C++ `auto` type deduction to VeloC `let`"),
        ("cpp_range_based_for_to_for_in", "Translate `for (const auto& x : vec)` to `for (x in vec)`")
    ]
    for idx, (name, desc) in enumerate(cpp_tasks, start=1):
        tasks.append({
            "task_id": f"EVAL-CPP-{idx:03d}",
            "category": "cpp_to_veloc",
            "name": name,
            "prompt": f"Migrate C++ idiom to VeloC in `{name}`: {desc}.",
            "difficulty": "medium",
            "test_signature": f"test_{name}() -> bool",
            "verification_stub": f"assert_true({name}_verify());"
        })

    return tasks

if __name__ == '__main__':
    tasks = generate_200_tasks()
    out_dir = Path("D:/VeloC/eval")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "tasks.json"
    out_file.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    print(f"Generated {len(tasks)} tasks saved to {out_file}")
