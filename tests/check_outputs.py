#!/usr/bin/env python3
"""Lightweight repository validation checks."""

from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "outputs" / "tables" / "energy_dispatch_summary.csv"

if not SUMMARY.exists():
    raise SystemExit("Missing energy dispatch summary. Run python/energy_balance.py first.")

with SUMMARY.open(newline="") as handle:
    rows = list(csv.DictReader(handle))

if not rows:
    raise SystemExit("Dispatch summary is empty.")

for row in rows:
    for field in ["demand_mwh", "renewable_mwh", "battery_state_mwh", "curtailed_mwh", "unmet_mwh", "emissions_tco2"]:
        value = float(row[field])
        if value < -1e-9:
            raise SystemExit(f"Negative value found in {field}: {value}")

print("Validation checks passed.")
