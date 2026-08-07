.headers on
.mode csv

SELECT
    scenario,
    ROUND(annual_probability, 4) AS annual_probability,
    ROUND(consequence_million_usd, 3) AS consequence_million_usd,
    ROUND(service_retained_fraction, 3) AS service_retained_fraction,
    ROUND(annualized_risk_million_usd, 4) AS annualized_risk_million_usd
FROM resilience_scenarios
ORDER BY annualized_risk_million_usd ASC;
