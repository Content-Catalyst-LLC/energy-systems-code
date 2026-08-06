PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS power_observation (
    timestamp TEXT PRIMARY KEY, power_kw REAL NOT NULL CHECK (power_kw >= 0), source TEXT NOT NULL DEFAULT 'synthetic');
CREATE TABLE IF NOT EXISTS conversion_stage (
    scenario TEXT NOT NULL, stage_order INTEGER NOT NULL CHECK (stage_order >= 1), stage_name TEXT NOT NULL,
    efficiency REAL NOT NULL CHECK (efficiency >= 0 AND efficiency <= 1), PRIMARY KEY (scenario, stage_order));
CREATE TABLE IF NOT EXISTS scenario_result (
    scenario TEXT PRIMARY KEY, energy_kwh REAL NOT NULL CHECK (energy_kwh >= 0),
    mean_power_kw REAL NOT NULL CHECK (mean_power_kw >= 0), peak_power_kw REAL NOT NULL CHECK (peak_power_kw >= 0),
    useful_energy_kwh REAL NOT NULL CHECK (useful_energy_kwh >= 0), losses_kwh REAL NOT NULL CHECK (losses_kwh >= 0),
    conservation_residual_kwh REAL NOT NULL);
CREATE VIEW IF NOT EXISTS scenario_efficiency AS
SELECT scenario, energy_kwh, useful_energy_kwh, losses_kwh,
       CASE WHEN energy_kwh = 0 THEN 0 ELSE useful_energy_kwh / energy_kwh END AS overall_efficiency
FROM scenario_result;
