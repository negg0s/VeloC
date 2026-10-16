#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
int main() { int arr[3] = {10, 20, 30}; int* p = arr; std::cout << *(p + 1); return 0; }