cmake_minimum_required(VERSION 3.20)
project(VeloC_CMake_Integration LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../../cmake")
find_package(VeloC REQUIRED)

add_executable(host_cpp_app main.cpp)
target_link_libraries(host_cpp_app PRIVATE VeloC::Core)
