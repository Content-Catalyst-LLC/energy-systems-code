DROP TABLE IF EXISTS branch_flows;
CREATE TABLE branch_flows (
    branch TEXT NOT NULL,
    from_bus TEXT NOT NULL,
    to_bus TEXT NOT NULL,
    flow_mw REAL NOT NULL,
    thermal_limit_mw REAL NOT NULL,
    utilization REAL NOT NULL,
    estimated_loss_mw REAL NOT NULL
);
