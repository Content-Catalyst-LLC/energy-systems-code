#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

outages = [
    ["Storm-A", 10000, 2.0, 42, 0.06],
    ["Storm-B", 5000, 4.0, 28, 0.04],
    ["Equipment-C", 20000, 1.0, 35, 0.10],
    ["Vegetation-D", 3500, 0.75, 12, 0.18],
    ["Protection-E", 1800, 0.30, 5, 0.22],
]

with (RAW / "outages.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow([
        "event",
        "customers_affected",
        "duration_hours",
        "unserved_mw",
        "probability",
    ])
    writer.writerows(outages)

scenarios = [
    ["Baseline", 0.020, 80.0, 0.35],
    ["Flood hardening", 0.010, 55.0, 0.55],
    ["Automated switching", 0.020, 48.0, 0.65],
    ["Microgrid support", 0.020, 40.0, 0.78],
    ["Combined resilience", 0.008, 28.0, 0.86],
]

with (RAW / "resilience_scenarios.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow([
        "name",
        "annual_probability",
        "consequence_million_usd",
        "service_retained_fraction",
    ])
    writer.writerows(scenarios)

restoration = [
    [0, 0.35],
    [2, 0.48],
    [6, 0.70],
    [12, 0.88],
    [24, 0.97],
    [36, 1.00],
]

with (RAW / "restoration_curve.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["hours", "service_fraction"])
    writer.writerows(restoration)

print(f"Wrote reliability teaching data to {RAW}")
