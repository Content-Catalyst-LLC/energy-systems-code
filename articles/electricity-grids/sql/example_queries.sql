.headers on
.mode csv

SELECT
    branch,
    ROUND(flow_mw, 3) AS flow_mw,
    ROUND(thermal_limit_mw, 3) AS thermal_limit_mw,
    ROUND(100 * utilization, 2) AS utilization_percent,
    ROUND(estimated_loss_mw, 6) AS estimated_loss_mw
FROM branch_flows
ORDER BY utilization DESC;
