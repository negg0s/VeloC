#include <iostream>
int main() { std::cout << 1 << std::endl; void* p = malloc(4000000); std::cout << (p != nullptr) << std::endl; free(p); return 0; }
