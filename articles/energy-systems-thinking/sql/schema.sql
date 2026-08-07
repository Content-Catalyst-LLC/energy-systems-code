DROP TABLE IF EXISTS scenario_summary;
CREATE TABLE scenario_summary (
  scenario TEXT NOT NULL,
  initial_capacity_gw REAL NOT NULL,
  final_capacity_gw REAL NOT NULL,
  capacity_change_gw REAL NOT NULL,
  final_cost_index REAL NOT NULL
);
