#!/usr/bin/env python3
from transmission_distribution import (
    congestion_cost,
    feeder_utilization,
    three_phase_current_a,
    three_phase_loss_kw,
    transformer_loading,
)

print("500 MW at 115 kV:", round(three_phase_current_a(500, 115), 1), "A")
print("500 MW at 345 kV:", round(three_phase_current_a(500, 345), 1), "A")
print("Three-phase loss:", round(three_phase_loss_kw(800, 0.08), 1), "kW")
print("Feeder utilization:", feeder_utilization(9.6, 12.0))
print("Transformer loading:", transformer_loading(510, 500))
print("Congestion cost:", congestion_cost(200, 85, 30))
