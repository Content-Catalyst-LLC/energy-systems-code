#include <stdio.h>

int main(void) {
    const double generation = 3000.0;
    const double load = 3000.0;
    const double imbalance = generation - load;
    printf("generation_mw,load_mw,imbalance_mw\n");
    printf("%.6f,%.6f,%.12f\n", generation, load, imbalance);
    return (imbalance > 1e-9 || imbalance < -1e-9) ? 1 : 0;
}
