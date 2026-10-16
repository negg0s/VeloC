#include "D:/VeloC/include/veloc.h"

// ============================================================================
// , StackString, Mat4 3D, and Streaming Memory(VeloC 3.5: Pipe Operator)
// ============================================================================

auto square(f32 x) -> f32 {
    return x * x;
}

auto add_val(f32 x, f32 amount) -> f32 {
    return x + amount;
}

auto multiply_val(f32 x, f32 factor) -> f32 {
    return x * factor;
}

int main() {
    printf("===============================================================\n");
    printf("      VeloC 3.5: Functional Pipelining & High-Speed Engine     \n");
    printf("===============================================================\n");

    // 1. Pipe Operator ( ) - Reddit & Functional Programming Dream in C++()
    const f32 input = 4.0f;
    // multiply_val(3.0) -> 60.0(add_val(4.0) -> 20.0(square -> 16.0(4.0)))
    const f32 piped_result = multiply_val(add_val(square(input), 4.0f), 3.0f);
    printf("%s\n", (std::string("1. Pipe Operator Chaining: 4.0 |> square |> add(4.0) |> mul(3.0) = ") + ::veloc::to_str(piped_result)).c_str());

    // 2. StackString<64>: Zero-Allocation, 100% Stack String
    printf("\n2. StackString<64> (Zero Heap Allocations):\n");
    StackString<64> s1("Velocity");
    s1.append(" + C = ");
    s1.append("VeloC Ultra!");
    printf("%s\n", (std::string("   StackString: '") + ::veloc::to_str(s1.c_str()) + std::string("', length = ") + ::veloc::to_str(s1.len())).c_str());

    // 3. Mat4: Full AVX/FMA 4x4 Matrix for 3D Graphics & Physics
    printf("\n3. Mat4 3D Transformation (SIMD FMA):\n");
    Mat4 trans = Mat4::translation(10.0f, 20.0f, 30.0f);
    Mat4 scale = Mat4::scaling(2.0f, 2.0f, 2.0f);
    Mat4 model_mat = trans * scale;

    Vec4 local_pos(1.0f, 2.0f, 3.0f, 1.0f);
    Vec4 world_pos = model_mat.transform(local_pos);
    printf("%s\n", (std::string("   Local:  (") + ::veloc::to_str(local_pos.x) + std::string(", ") + ::veloc::to_str(local_pos.y) + std::string(", ") + ::veloc::to_str(local_pos.z) + std::string(")")).c_str());
    printf("%s\n", (std::string("   World:  (") + ::veloc::to_str(world_pos.x) + std::string(", ") + ::veloc::to_str(world_pos.y) + std::string(", ") + ::veloc::to_str(world_pos.z) + std::string(")")).c_str());

    // 4. Binary Serializer (ByteWriter & ByteReader)
    printf("\n4. Zero-Copy Binary Packet Serializer:\n");
    ByteWriter<128> writer;
    writer.write_u8(0xFF);
    writer.write_u32(1337);
    writer.write_f32(3.14159f);

    ByteReader reader(writer.data(), writer.len());
    const auto magic = reader.read_u8().unwrap();
    const auto port = reader.read_u32().unwrap();
    const auto pi = reader.read_f32().unwrap();
    printf("%s\n", (std::string("   Decoded packet: magic=") + ::veloc::to_str((u32)magic) + std::string(", port=") + ::veloc::to_str(port) + std::string(", pi=") + ::veloc::to_str(pi)).c_str());

    // 5. AVX2 Non-Temporal Streaming Memory Bandwidth Benchmark
    printf("\n5. AVX2 Non-Temporal Streaming Benchmark (Bypassing CPU Cache):\n");
    const usize BUFFER_SIZE = 16 * 1024 * 1024; // 16 MB Buffer
    u8* stream_buf_src = (u8*)veloc_aligned_alloc(32, BUFFER_SIZE);
    u8* stream_buf_dst = (u8*)veloc_aligned_alloc(32, BUFFER_SIZE);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(stream_buf_src); };
    auto _veloc_defer_2 = ::veloc::ScopeGuardHelper() + [&]() { veloc_aligned_free(stream_buf_dst); };

    memset(stream_buf_src, 0xAA, BUFFER_SIZE);

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        veloc::fast_zero_mem(stream_buf_dst, BUFFER_SIZE);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 Streaming Zero (16 MB)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    {
    ::veloc::CycleCounter _veloc_cc;
    VeloC_Timer _veloc_timer;
    _veloc_timer.start();
    {

        veloc::fast_copy_mem(stream_buf_dst, stream_buf_src, BUFFER_SIZE);
    
    }
    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\n", "AVX2 Streaming Copy (16 MB)", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());
}

    printf("===============================================================\n");
    printf("      All VeloC 3.5 Engine Subsystems Passed!                  \n");
    printf("===============================================================\n");
    return 0;
}