#include <stdio.h>

int main(void) {
    const double gross = 2400.0;
    const double invested = 180.0;
    const double eroi = gross / invested;
    const double net = gross - invested;

    printf("gross_mwh,invested_mwh,eroi,net_energy_mwh\n");
    printf("%.6f,%.6f,%.9f,%.6f\n", gross, invested, eroi, net);
    return 0;
}
