#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
struct Box { int w, h; }; int main() { Box b = {5, 6}; std::cout << (b.w * b.h); return 0; }