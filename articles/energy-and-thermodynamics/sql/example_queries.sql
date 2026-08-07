.headers on
.mode csv

SELECT
    scenario,
    1.0 - cold_temperature_k / hot_temperature_k AS carnot_efficiency,
    (1.0 - cold_temperature_k / hot_temperature_k) * second_law_fraction AS actual_efficiency,
    heat_input_mj * (1.0 - cold_temperature_k / hot_temperature_k) * second_law_fraction AS work_output_mj
FROM thermodynamic_scenarios
ORDER BY actual_efficiency DESC;

SELECT
    scenario,
    hot_temperature_k / (hot_temperature_k - cold_temperature_k) * heat_pump_fraction AS heating_cop
FROM thermodynamic_scenarios
ORDER BY heating_cop DESC;
