PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS energy_nodes (
    node_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (
        kind IN ('resource', 'conversion', 'network', 'storage', 'end_use', 'service', 'loss')
    ),
    carrier TEXT NOT NULL,
    capacity_mw REAL,
    criticality REAL NOT NULL DEFAULT 0.0 CHECK (criticality BETWEEN 0.0 AND 1.0)
);

CREATE TABLE IF NOT EXISTS energy_links (
    link_id TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL REFERENCES energy_nodes(node_id),
    target_node_id TEXT NOT NULL REFERENCES energy_nodes(node_id),
    input_mwh REAL NOT NULL CHECK (input_mwh >= 0.0),
    efficiency REAL NOT NULL CHECK (efficiency BETWEEN 0.0 AND 1.0),
    emissions_kg_co2e_per_mwh_input REAL NOT NULL DEFAULT 0.0,
    variable_cost_usd_per_mwh_input REAL NOT NULL DEFAULT 0.0,
    availability REAL NOT NULL DEFAULT 1.0 CHECK (availability BETWEEN 0.0 AND 1.0)
);

CREATE VIEW IF NOT EXISTS energy_link_accounting AS
SELECT
    link_id,
    source_node_id,
    target_node_id,
    input_mwh,
    input_mwh * availability AS available_input_mwh,
    input_mwh * availability * efficiency AS output_mwh,
    input_mwh * availability * (1.0 - efficiency) AS loss_mwh,
    input_mwh * (1.0 - availability) AS unavailable_mwh,
    input_mwh * availability * emissions_kg_co2e_per_mwh_input AS emissions_kg_co2e,
    input_mwh * availability * variable_cost_usd_per_mwh_input AS variable_cost_usd
FROM energy_links;
