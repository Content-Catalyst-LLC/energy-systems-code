.headers on
.mode csv

SELECT
    hour,
    ROUND(demand_mw, 3) AS demand_mw
FROM interval_demand
WHERE demand_mw > 75
ORDER BY demand_mw DESC;
