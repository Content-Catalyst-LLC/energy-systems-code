#include <math.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct { const char *name; double efficiency; } Stage;
int main(void) {
    const double input = 1000.0; double current = input;
    const Stage stages[] = {{"distribution", .975}, {"inverter", .965}, {"motor", .925}, {"drive", .940}};
    puts("stage,input_kwh,efficiency,output_kwh,loss_kwh");
    for (size_t i = 0; i < sizeof(stages)/sizeof(stages[0]); ++i) {
        if (stages[i].efficiency < 0 || stages[i].efficiency > 1) return EXIT_FAILURE;
        const double output = current * stages[i].efficiency;
        printf("%s,%.6f,%.6f,%.6f,%.6f\n", stages[i].name, current, stages[i].efficiency, output, current-output);
        current = output;
    }
    const double losses = input-current, residual = input-current-losses;
    fprintf(stderr, "overall_efficiency=%.9f residual_kwh=%.12f\n", current/input, residual);
    return fabs(residual) < 1e-9 ? EXIT_SUCCESS : EXIT_FAILURE;
}
