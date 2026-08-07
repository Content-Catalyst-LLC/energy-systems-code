DROP TABLE IF EXISTS energy_pathway;
CREATE TABLE energy_pathway (
  pathway TEXT PRIMARY KEY,
  primary_energy_mwh REAL NOT NULL CHECK (primary_energy_mwh >= 0),
  conversion_efficiency REAL NOT NULL CHECK (conversion_efficiency BETWEEN 0 AND 1),
  delivery_efficiency REAL NOT NULL CHECK (delivery_efficiency BETWEEN 0 AND 1),
  end_use_efficiency REAL NOT NULL CHECK (end_use_efficiency BETWEEN 0 AND 1),
  service_factor REAL NOT NULL CHECK (service_factor BETWEEN 0 AND 1),
  energy_sector_own_use_fraction REAL NOT NULL CHECK (energy_sector_own_use_fraction BETWEEN 0 AND 1),
  non_energy_use_fraction REAL NOT NULL CHECK (non_energy_use_fraction BETWEEN 0 AND 1)
);
