DROP TABLE IF EXISTS feeder_summary;
CREATE TABLE feeder_summary (
    feeder TEXT NOT NULL,
    rating_mva REAL NOT NULL,
    peak_mva REAL NOT NULL,
    power_factor REAL NOT NULL,
    utilization REAL NOT NULL,
    headroom_mva REAL NOT NULL,
    current_a_at_13_8kv REAL NOT NULL,
    estimated_resistive_loss_kw REAL NOT NULL
);
