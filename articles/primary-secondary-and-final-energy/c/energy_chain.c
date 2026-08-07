#include <stdio.h>

int main(void) {
    const double primary = 100.0;
    const double own_use_fraction = 0.05;
    const double non_energy_fraction = 0.05;
    const double conversion_efficiency = 0.50;
    const double delivery_efficiency = 0.90;
    const double end_use_efficiency = 0.80;
    const double service_factor = 0.75;

    const double own_use = primary * own_use_fraction;
    const double non_energy = primary * non_energy_fraction;
    const double transformation_input = primary - own_use - non_energy;
    const double secondary = transformation_input * conversion_efficiency;
    const double final = secondary * delivery_efficiency;
    const double useful = final * end_use_efficiency;
    const double service = useful * service_factor;
    const double losses = own_use + non_energy + (transformation_input - secondary) + (secondary - final) + (final - useful) + (useful - service);
    const double residual = primary - losses - service;

    printf("metric,value_mwh\n");
    printf("primary_energy,%.9f\n", primary);
    printf("secondary_energy,%.9f\n", secondary);
    printf("final_energy,%.9f\n", final);
    printf("useful_energy,%.9f\n", useful);
    printf("service_energy_equivalent,%.9f\n", service);
    printf("residual,%.12f\n", residual);
    return 0;
}
