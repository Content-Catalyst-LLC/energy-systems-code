% GNU Octave / MATLAB-compatible energy balance example.
demand = [42, 40, 38, 36, 35, 39, 48, 55, 61, 64, 66, 67];
solar =  [0, 0, 0, 0, 2, 8, 18, 34, 48, 58, 62, 64];
wind =   [18, 16, 15, 14, 16, 24, 30, 26, 22, 20, 18, 16];
renewable = solar + wind;
fprintf('Octave energy balance summary\n');
fprintf('Total demand: %.2f MWh\n', sum(demand));
fprintf('Total renewable generation: %.2f MWh\n', sum(renewable));
fprintf('Renewable share proxy: %.3f\n', sum(renewable) / sum(demand));
