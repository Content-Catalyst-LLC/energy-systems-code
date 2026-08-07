DROP TABLE IF EXISTS energy_flows;
CREATE TABLE energy_flows (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    value_mwh REAL NOT NULL CHECK (value_mwh >= 0),
    category TEXT NOT NULL,
    note TEXT
);
