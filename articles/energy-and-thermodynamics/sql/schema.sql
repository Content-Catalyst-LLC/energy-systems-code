DROP TABLE IF EXISTS thermodynamic_scenarios;
CREATE TABLE thermodynamic_scenarios (
    scenario TEXT PRIMARY KEY,
    hot_temperature_k REAL NOT NULL CHECK (hot_temperature_k > 0),
    cold_temperature_k REAL NOT NULL CHECK (cold_temperature_k > 0),
    heat_input_mj REAL NOT NULL CHECK (heat_input_mj > 0),
    second_law_fraction REAL NOT NULL CHECK (second_law_fraction > 0 AND second_law_fraction <= 1),
    ambient_temperature_k REAL NOT NULL CHECK (ambient_temperature_k > 0),
    heat_pump_fraction REAL NOT NULL CHECK (heat_pump_fraction > 0 AND heat_pump_fraction <= 1),
    charge_efficiency REAL NOT NULL CHECK (charge_efficiency >= 0 AND charge_efficiency <= 1),
    discharge_efficiency REAL NOT NULL CHECK (discharge_efficiency >= 0 AND discharge_efficiency <= 1),
    retention_fraction REAL NOT NULL CHECK (retention_fraction >= 0 AND retention_fraction <= 1),
    CHECK (hot_temperature_k > cold_temperature_k)
);
