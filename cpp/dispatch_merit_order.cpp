#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Generator {
    std::string name;
    double capacity_mw;
    double variable_cost;
    double emissions;
};

int main() {
    std::vector<Generator> fleet = {
        {"Wind", 300.0, 0.0, 0.0},
        {"Solar", 280.0, 0.0, 0.0},
        {"Nuclear", 650.0, 18.0, 12.0},
        {"Gas CC", 450.0, 48.0, 370.0},
        {"Coal", 500.0, 62.0, 950.0},
        {"Gas CT", 180.0, 92.0, 560.0}
    };

    double demand = 1200.0;
    std::sort(fleet.begin(), fleet.end(), [](const Generator& a, const Generator& b) {
        return a.variable_cost < b.variable_cost;
    });

    std::cout << "generator,dispatch_mwh,cost_usd,emissions_kg\n";
    for (const auto& gen : fleet) {
        if (demand <= 0) break;
        double dispatch = std::min(gen.capacity_mw, demand);
        demand -= dispatch;
        std::cout << gen.name << "," << dispatch << "," << dispatch * gen.variable_cost
                  << "," << dispatch * gen.emissions << "\n";
    }

    return 0;
}
