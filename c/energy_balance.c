#include <stdio.h>

int main(void) {
    double demand_mwh = 690.0;
    double solar_mwh = 455.0;
    double wind_mwh = 120.0;
    double storage_discharge_mwh = 80.0;

    double supply_mwh = solar_mwh + wind_mwh + storage_discharge_mwh;
    double balance_mwh = supply_mwh - demand_mwh;

    printf("demand_mwh,%.2f\n", demand_mwh);
    printf("supply_mwh,%.2f\n", supply_mwh);
    printf("balance_mwh,%.2f\n", balance_mwh);

    return 0;
}
