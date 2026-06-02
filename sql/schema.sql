CREATE TABLE IF NOT EXISTS hourly_energy (
    hour INTEGER PRIMARY KEY,
    demand_mwh REAL NOT NULL,
    solar_mwh REAL NOT NULL,
    wind_mwh REAL NOT NULL,
    temperature_c REAL
);

CREATE TABLE IF NOT EXISTS generator_fleet (
    plant TEXT PRIMARY KEY,
    technology TEXT NOT NULL,
    nameplate_mw REAL NOT NULL,
    variable_cost_usd_mwh REAL,
    emissions_kg_co2_mwh REAL,
    forced_outage_rate REAL,
    capacity_credit REAL
);

CREATE TABLE IF NOT EXISTS household_energy_burden (
    household_id TEXT PRIMARY KEY,
    income_usd_yr REAL NOT NULL,
    annual_energy_cost_usd REAL NOT NULL,
    housing_type TEXT,
    region TEXT,
    heat_source TEXT
);
