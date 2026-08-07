#include <stdio.h>

int main(void) {
    const double vehicles = 10000.0;
    const double energy_kwh_each = 14.0;
    const double charging_hours = 7.0;
    const double total_mwh = vehicles * energy_kwh_each / 1000.0;
    const double power_mw = total_mwh / charging_hours;

    printf("vehicles,energy_kwh_each,charging_hours,power_mw\n");
    printf("%.0f,%.6f,%.6f,%.6f\n",
           vehicles, energy_kwh_each, charging_hours, power_mw);
    return power_mw > 0.0 ? 0 : 1;
}
