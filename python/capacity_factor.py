#!/usr/bin/env python3
"""Capacity factor calculations for the synthetic generator fleet."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLEET = ROOT / "data" / "synthetic" / "generator_fleet.csv"
HOURLY = ROOT / "data" / "synthetic" / "hourly_load_and_renewables.csv"
OUTPUT = ROOT / "outputs" / "tables" / "capacity_factor_summary.csv"


def main() -> None:
    with FLEET.open(newline="", encoding="utf-8") as handle:
        fleet = list(csv.DictReader(handle))

    with HOURLY.open(newline="", encoding="utf-8") as handle:
        hourly = list(csv.DictReader(handle))

    solar_actual = sum(float(row["solar_mwh"]) for row in hourly)
    wind_actual = sum(float(row["wind_mwh"]) for row in hourly)
    hours = len(hourly)

    rows = []
    for plant in fleet:
        technology = plant["technology"]
        nameplate = float(plant["nameplate_mw"])

        if technology == "solar":
            actual = solar_actual
        elif technology == "wind":
            actual = wind_actual
        else:
            actual = nameplate * hours * float(plant["capacity_credit"])

        capacity_factor = actual / (nameplate * hours)
        rows.append(
            {
                "plant": plant["plant"],
                "technology": technology,
                "nameplate_mw": f"{nameplate:.1f}",
                "estimated_generation_mwh": f"{actual:.2f}",
                "capacity_factor": f"{capacity_factor:.3f}",
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
