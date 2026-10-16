#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
int main() { int x = 10; { int x = 20; } std::cout << x; return 0; }