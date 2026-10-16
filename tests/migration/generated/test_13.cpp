#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
int main() { int val = 42; int& ref = val; ref = 99; std::cout << val; return 0; }