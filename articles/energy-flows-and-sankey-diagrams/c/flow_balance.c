#include <stdio.h>

int main(void) {
    const double input = 100.0;
    const double electricity = 42.0;
    const double losses = 58.0;
    const double residual = input - electricity - losses;
    printf("input_mwh,electricity_mwh,losses_mwh,residual_mwh\n");
    printf("%.6f,%.6f,%.6f,%.12f\n", input, electricity, losses, residual);
    return residual > 1e-9 || residual < -1e-9;
}
