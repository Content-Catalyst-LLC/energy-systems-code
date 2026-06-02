#include <stdio.h>

int main(void) {
    double demand[] = {42, 40, 38, 36, 35, 39, 48, 55, 61, 64, 66, 67};
    double solar[] = {0, 0, 0, 0, 2, 8, 18, 34, 48, 58, 62, 64};
    double wind[] = {18, 16, 15, 14, 16, 24, 30, 26, 22, 20, 18, 16};
    int n = sizeof(demand) / sizeof(demand[0]);
    double total_demand = 0.0;
    double total_renewable = 0.0;

    for (int i = 0; i < n; i++) {
        total_demand += demand[i];
        total_renewable += solar[i] + wind[i];
    }

    printf("C energy balance summary\n");
    printf("Total demand: %.2f MWh\n", total_demand);
    printf("Total renewable generation: %.2f MWh\n", total_renewable);
    printf("Renewable share proxy: %.3f\n", total_renewable / total_demand);
    return 0;
}
