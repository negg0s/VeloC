#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
int fact(int n) { if (n <= 1) return 1; return n * fact(n-1); } int main() { std::cout << fact(5); return 0; }