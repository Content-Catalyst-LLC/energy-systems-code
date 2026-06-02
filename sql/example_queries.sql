-- Example query after loading data into hourly_energy_profile.
SELECT
    SUM(demand_mwh) AS total_demand_mwh,
    SUM(solar_mwh + wind_mwh) AS total_renewable_mwh,
    AVG((solar_mwh + wind_mwh) / demand_mwh) AS average_hourly_renewable_share
FROM hourly_energy_profile;
