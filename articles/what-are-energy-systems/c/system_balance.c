#include <stdio.h>

int main(void) {
    const double primary_input_mwh = 12100.0;
    const double useful_service_mwh = 3657.578;
    const double conversion_network_losses_mwh = 8442.422;
    const double boundary_residual_mwh = primary_input_mwh - useful_service_mwh - conversion_network_losses_mwh;

    printf("primary_input_mwh,useful_service_mwh,conversion_network_losses_mwh,boundary_residual_mwh\n");
    printf("%.3f,%.3f,%.3f,%.3f\n",
           primary_input_mwh,
           useful_service_mwh,
           conversion_network_losses_mwh,
           boundary_residual_mwh);
    return 0;
}
