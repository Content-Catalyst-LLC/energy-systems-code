#include <math.h>
#include <stdio.h>

int main(void) {
    const double power_mw = 500.0;
    const double voltage_kv = 345.0;
    const double current_a =
        power_mw * 1000000.0 /
        (sqrt(3.0) * voltage_kv * 1000.0);

    printf("power_mw,voltage_kv,current_a\n");
    printf("%.6f,%.6f,%.6f\n", power_mw, voltage_kv, current_a);
    return current_a > 0.0 ? 0 : 1;
}
