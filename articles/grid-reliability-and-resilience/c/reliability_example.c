#include <stdio.h>

int main(void) {
    const double available = 42000.0;
    const double peak = 36000.0;
    const double reserve_margin = (available - peak) / peak;
    printf("available_mw,peak_mw,reserve_margin\n");
    printf("%.6f,%.6f,%.9f\n", available, peak, reserve_margin);
    return 0;
}
