#include "veloc.h"
#include <algorithm>
#include <vector>
#include <cmath>
#include <chrono>
#include <complex>
#include <cassert>
#include <cstdio>

int main() {
    printf("==================================================\n");
    printf("   Testing VeloC C++ Complex Header Interoperability\n");
    printf("==================================================\n");

    // 1. <algorithm> & <vector>
    std::vector<int> data = {5, 2, 8, 1, 9};
    std::sort(data.begin(), data.end());
    assert(data[0] == 1 && data[4] == 9);
    auto it = std::lower_bound(data.begin(), data.end(), 5);
    assert(*it == 5);
    printf("  [PASS] <algorithm> and <vector> template interop verified.\n");

    // 2. <cmath>
    double s = std::sin(3.141592653589793 / 2.0);
    assert(std::abs(s - 1.0) < 1e-9);
    printf("  [PASS] <cmath> floating-point functions verified.\n");

    // 3. <chrono>
    auto t1 = std::chrono::high_resolution_clock::now();
    auto t2 = std::chrono::high_resolution_clock::now();
    auto diff = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
    assert(diff >= 0);
    printf("  [PASS] <chrono> duration templates verified.\n");

    // 4. <complex>
    std::complex<double> c1(3.0, 4.0);
    std::complex<double> c2(1.0, 2.0);
    auto c3 = c1 * c2;
    assert(c3.real() == -5.0 && c3.imag() == 10.0);
    printf("  [PASS] <complex> operator overloading verified.\n");

    printf("==================================================\n");
    printf("[ALL 5 COMPLEX C++ HEADERS PASSED INTEROP TEST]\n");
    return 0;
}
