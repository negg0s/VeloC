#include <iostream>
#include <vector>

int main() {
    auto sum = 0;
    std::vector<int> numbers = {10, 20, 30, 40};
    for (size_t i = 0; i < numbers.size(); i++) {
        sum += numbers[i];
    }
    std::cout << "Sum is: " << sum << std::endl;
    return 0;
}
