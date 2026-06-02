CREATE TABLE IF NOT EXISTS hourly_energy_profile (
    hour INTEGER PRIMARY KEY,
    demand_mwh REAL NOT NULL CHECK (demand_mwh >= 0),
    solar_mwh REAL NOT NULL CHECK (solar_mwh >= 0),
    wind_mwh REAL NOT NULL CHECK (wind_mwh >= 0),
    thermal_mwh REAL NOT NULL CHECK (thermal_mwh >= 0),
    emissions_factor_tco2_per_mwh REAL NOT NULL CHECK (emissions_factor_tco2_per_mwh >= 0)
);

CREATE VIEW IF NOT EXISTS hourly_energy_balance AS
SELECT
    hour,
    demand_mwh,
    solar_mwh,
    wind_mwh,
    thermal_mwh,
    solar_mwh + wind_mwh AS renewable_mwh,
    CASE
        WHEN demand_mwh > 0 THEN (solar_mwh + wind_mwh) / demand_mwh
        ELSE NULL
    END AS renewable_share_of_demand,
    emissions_factor_tco2_per_mwh
FROM hourly_energy_profile;
