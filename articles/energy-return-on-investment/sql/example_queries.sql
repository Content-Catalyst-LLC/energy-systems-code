.headers on
.mode csv

SELECT
    name,
    ROUND(gross_output_mwh, 3) AS gross_output_mwh,
    ROUND(
      construction_mwh + fuel_cycle_mwh + operations_mwh + maintenance_mwh +
      replacement_mwh + network_mwh + storage_mwh + retirement_mwh,
      3
    ) AS invested_mwh,
    ROUND(
      gross_output_mwh /
      (
        construction_mwh + fuel_cycle_mwh + operations_mwh + maintenance_mwh +
        replacement_mwh + network_mwh + storage_mwh + retirement_mwh
      ),
      6
    ) AS eroi
FROM eroi_projects
ORDER BY eroi DESC;
