DROP TABLE IF EXISTS resilience_scenarios;
CREATE TABLE resilience_scenarios (
    scenario TEXT NOT NULL,
    annual_probability REAL NOT NULL,
    consequence_million_usd REAL NOT NULL,
    service_retained_fraction REAL NOT NULL,
    annualized_risk_million_usd REAL NOT NULL
);
