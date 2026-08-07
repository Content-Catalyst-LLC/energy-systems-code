.headers on
.mode csv

SELECT category, ROUND(SUM(value_mwh), 6) AS total_mwh
FROM energy_flows
GROUP BY category
ORDER BY total_mwh DESC;

SELECT source, ROUND(SUM(value_mwh), 6) AS total_outflow_mwh
FROM energy_flows
GROUP BY source
ORDER BY total_outflow_mwh DESC
LIMIT 10;
