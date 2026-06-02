#include <iostream>
#include <numeric>
#include <vector>

int main() {
    std::vector<double> demand {42, 40, 38, 36, 35, 39, 48, 55, 61, 64, 66, 67};
    std::vector<double> solar  {0, 0, 0, 0, 2, 8, 18, 34, 48, 58, 62, 64};
    std::vector<double> wind   {18, 16, 15, 14, 16, 24, 30, 26, 22, 20, 18, 16};

    double total_demand = std::accumulate(demand.begin(), demand.end(), 0.0);
    double total_renewable = 0.0;

    for (std::size_t i = 0; i < demand.size(); ++i) {
        total_renewable += solar[i] + wind[i];
    }

    std::cout << "C++ energy balance summary\n";
    std::cout << "Total demand: " << total_demand << " MWh\n";
    std::cout << "Total renewable generation: " << total_renewable << " MWh\n";
    std::cout << "Renewable share proxy: " << total_renewable / total_demand << "\n";
    return 0;
}
