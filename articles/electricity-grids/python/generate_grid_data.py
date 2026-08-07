#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

branches = [
    ["North-Central", "North", "Central", 0.12, 900, 0.012],
    ["North-East", "North", "East", 0.18, 650, 0.015],
    ["Central-East", "Central", "East", 0.10, 850, 0.010],
    ["Central-South", "Central", "South", 0.14, 700, 0.014],
    ["East-South", "East", "South", 0.11, 750, 0.011],
]

with (RAW / "branches.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["name", "from_bus", "to_bus", "reactance_pu", "thermal_limit_mw", "resistance_pu"])
    writer.writerows(branches)

angles = [
    ["North", 0.050],
    ["Central", 0.020],
    ["East", -0.010],
    ["South", -0.035],
]

with (RAW / "bus_angles.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["bus", "angle_rad"])
    writer.writerows(angles)

loads = [
    ["North", 820, 400],
    ["Central", 900, 1050],
    ["East", 520, 760],
    ["South", 300, 510],
]

with (RAW / "bus_injections.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["bus", "generation_mw", "load_mw"])
    writer.writerows(loads)

print(f"Wrote synthetic grid data to {RAW}")
