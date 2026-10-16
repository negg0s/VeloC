#include <iostream>
#include <cstdlib>
int main() { std::cout << 1 << std::endl; void* p = _aligned_malloc(4000000, 32); std::cout << (p != nullptr) << std::endl; _aligned_free(p); return 0; }
