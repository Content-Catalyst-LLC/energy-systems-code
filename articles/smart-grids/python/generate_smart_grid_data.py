#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

interval = [
    [0, 42], [1, 40], [2, 39], [3, 38], [4, 39], [5, 43],
    [6, 50], [7, 57], [8, 61], [9, 64], [10, 66], [11, 67],
    [12, 68], [13, 69], [14, 71], [15, 74], [16, 79], [17, 85],
    [18, 88], [19, 84], [20, 77], [21, 68], [22, 58], [23, 49],
]

with (RAW / "interval_demand.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["hour", "demand_mw"])
    writer.writerows(interval)

resources = [
    ["Community battery", 8.0, 0.96, 0.90],
    ["Managed EV charging", 12.0, 0.92, 0.78],
    ["Commercial demand response", 10.0, 0.88, 0.85],
    ["Smart thermostats", 6.0, 0.90, 0.70],
    ["Industrial flexibility", 9.0, 0.94, 0.82],
]

with (RAW / "der_resources.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["name", "power_mw", "availability", "response_fraction"])
    writer.writerows(resources)

automation = [
    ["Manual switching", 12000, 2200, 90, 90],
    ["FLISR basic", 12000, 9800, 90, 8],
    ["FLISR advanced", 12000, 9800, 90, 2],
    ["Automated alternate feeder", 12000, 10500, 90, 1],
    ["Microgrid-assisted restoration", 12000, 11000, 90, 1],
]

with (RAW / "automation_scenarios.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow([
        "scenario",
        "total_customers",
        "customers_restored",
        "manual_minutes",
        "automated_minutes",
    ])
    writer.writerows(automation)

print(f"Wrote smart-grid teaching data to {RAW}")
