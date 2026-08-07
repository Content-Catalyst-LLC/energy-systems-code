#include <stdio.h>

int main(int argc, char **argv) {
    const char *output = argc > 1 ? argv[1] : "c_cycle_metrics.csv";
    const double hot_k = 823.15;
    const double cold_k = 303.15;
    const double heat_input_mj = 1000.0;
    const double second_law_fraction = 0.58;
    const double carnot = 1.0 - cold_k / hot_k;
    const double actual = carnot * second_law_fraction;
    const double work = heat_input_mj * actual;
    const double rejected = heat_input_mj - work;
    const double entropy_generation = rejected / cold_k - heat_input_mj / hot_k;
    const double residual = heat_input_mj - work - rejected;

    FILE *file = fopen(output, "w");
    if (!file) {
        perror("fopen");
        return 1;
    }
    fprintf(file, "scenario,carnot_efficiency,actual_efficiency,work_output_mj,heat_rejected_mj,entropy_generation_mj_per_k,first_law_residual_mj\n");
    fprintf(file, "baseline_steam_cycle,%.12f,%.12f,%.9f,%.9f,%.12f,%.12f\n",
            carnot, actual, work, rejected, entropy_generation, residual);
    fclose(file);
    printf("Wrote %s\n", output);
    return 0;
}
