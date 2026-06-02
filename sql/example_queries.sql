-- Renewable share by hour
SELECT
    hour,
    demand_mwh,
    solar_mwh + wind_mwh AS renewable_mwh,
    (solar_mwh + wind_mwh) / demand_mwh AS renewable_share
FROM hourly_energy
ORDER BY hour;

-- High energy burden households
SELECT
    household_id,
    region,
    housing_type,
    annual_energy_cost_usd / income_usd_yr AS energy_burden
FROM household_energy_burden
WHERE annual_energy_cost_usd / income_usd_yr >= 0.06
ORDER BY energy_burden DESC;

-- Generator merit order
SELECT
    plant,
    technology,
    variable_cost_usd_mwh,
    emissions_kg_co2_mwh
FROM generator_fleet
ORDER BY variable_cost_usd_mwh ASC;
