DROP TABLE IF EXISTS eroi_projects;
CREATE TABLE eroi_projects (
    name TEXT NOT NULL,
    gross_output_mwh REAL NOT NULL CHECK (gross_output_mwh >= 0),
    construction_mwh REAL NOT NULL CHECK (construction_mwh >= 0),
    fuel_cycle_mwh REAL NOT NULL CHECK (fuel_cycle_mwh >= 0),
    operations_mwh REAL NOT NULL CHECK (operations_mwh >= 0),
    maintenance_mwh REAL NOT NULL CHECK (maintenance_mwh >= 0),
    replacement_mwh REAL NOT NULL CHECK (replacement_mwh >= 0),
    network_mwh REAL NOT NULL CHECK (network_mwh >= 0),
    storage_mwh REAL NOT NULL CHECK (storage_mwh >= 0),
    retirement_mwh REAL NOT NULL CHECK (retirement_mwh >= 0)
);
