SELECT SUM(power_kw) AS approximate_energy_kwh FROM power_observation;
SELECT scenario, energy_kwh, useful_energy_kwh, losses_kwh,
       energy_kwh-useful_energy_kwh-losses_kwh AS calculated_residual_kwh
FROM scenario_result ORDER BY scenario;
SELECT * FROM scenario_efficiency ORDER BY overall_efficiency DESC;
