#!/usr/bin/env python3
"""Hydrogen production teaching model."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "synthetic" / "hydrogen_scenarios.csv"
OUTPUT = ROOT / "outputs" / "tables" / "hydrogen_model_results.csv"


def main() -> None:
    rows = []
    with INPUT.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            electricity_mwh = float(row["electricity_mwh"])
            kwh_per_kg = float(row["electrolyzer_efficiency_kwh_per_kg"])
            water_liters_per_kg = float(row["water_liters_per_kg"])
            hydrogen_kg = electricity_mwh * 1000 / kwh_per_kg
            water_liters = hydrogen_kg * water_liters_per_kg
            rows.append(
                {
                    "scenario": row["scenario"],
                    "hydrogen_kg_calculated": f"{hydrogen_kg:.2f}",
                    "water_liters_required": f"{water_liters:.2f}",
                    "capacity_factor": row["capacity_factor"],
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
