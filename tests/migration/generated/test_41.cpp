#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
struct Vec2 { float x, y; }; Vec2 add(Vec2 a, Vec2 b) { return {a.x + b.x, a.y + b.y}; } int main() { Vec2 v = add({1, 2}, {3, 4}); std::cout << (int)(v.x + v.y); return 0; }