#include <iostream>
#include <vector>
#include <veloc.h>
int main() { std::cout << 1 << std::endl; float* p = (float*)veloc_aligned_alloc(32, sizeof(float)*1000000); std::cout << 2 << std::endl; veloc_aligned_free(p); std::cout << 3 << std::endl; return 0; }
