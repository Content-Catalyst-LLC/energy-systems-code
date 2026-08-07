-- System totals across the declared boundary.
SELECT
    ROUND(SUM(available_input_mwh), 3) AS link_throughput_mwh,
    ROUND(SUM(loss_mwh), 3) AS conversion_and_network_losses_mwh,
    ROUND(SUM(unavailable_mwh), 3) AS unavailable_energy_mwh,
    ROUND(SUM(emissions_kg_co2e) / 1000.0, 3) AS emissions_t_co2e,
    ROUND(SUM(variable_cost_usd), 2) AS variable_cost_usd
FROM energy_link_accounting;

-- Most consequential losses by link.
SELECT
    link_id,
    ROUND(loss_mwh, 3) AS loss_mwh,
    ROUND(loss_mwh / NULLIF(available_input_mwh, 0), 4) AS loss_share
FROM energy_link_accounting
ORDER BY loss_mwh DESC
LIMIT 10;

-- Critical service nodes and their direct delivered output.
SELECT
    n.node_id,
    n.name,
    n.criticality,
    ROUND(SUM(a.output_mwh), 3) AS delivered_service_mwh_equivalent
FROM energy_nodes AS n
JOIN energy_link_accounting AS a ON a.target_node_id = n.node_id
WHERE n.kind = 'service'
GROUP BY n.node_id, n.name, n.criticality
ORDER BY n.criticality DESC, delivered_service_mwh_equivalent DESC;
