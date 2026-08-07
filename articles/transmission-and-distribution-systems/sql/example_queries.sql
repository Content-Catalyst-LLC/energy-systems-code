.headers on
.mode csv

SELECT
    feeder,
    ROUND(100 * utilization, 2) AS utilization_percent,
    ROUND(headroom_mva, 3) AS headroom_mva,
    ROUND(estimated_resistive_loss_kw, 3) AS estimated_resistive_loss_kw
FROM feeder_summary
ORDER BY utilization DESC;
