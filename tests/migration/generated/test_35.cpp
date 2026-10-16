#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
int main() { std::vector<int> v = {1, 2, 3}; int sum = 0; for (auto x : v) sum += x; std::cout << sum; return 0; }