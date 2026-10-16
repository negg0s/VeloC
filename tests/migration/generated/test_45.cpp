#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
int main() { int cnt = 0; for (int i = 0; i < 10; i++) { if (i == 4) break; cnt++; } std::cout << cnt; return 0; }