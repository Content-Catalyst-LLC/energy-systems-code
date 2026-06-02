#!/usr/bin/env python3
"""Simplified emissions accounting for synthetic generation scenarios."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLEET = ROOT / "data" / "synthetic" / "generator_fleet.csv"
OUTPUT = ROOT / "outputs" / "tables" / "emissions_accounting_results.csv"


def main() -> None:
    rows = []
    total_generation = 0.0
    total_emissions = 0.0

    with FLEET.open(newline="", encoding="utf-8") as handle:
        for plant in csv.DictReader(handle):
            nameplate = float(plant["nameplate_mw"])
            capacity_credit = float(plant["capacity_credit"])
            emissions_factor = float(plant["emissions_kg_co2_mwh"])
            generation = nameplate * 24 * capacity_credit
            emissions = generation * emissions_factor

            rows.append(
                {
                    "plant": plant["plant"],
                    "technology": plant["technology"],
                    "generation_mwh": f"{generation:.2f}",
                    "emissions_kg_co2": f"{emissions:.2f}",
                }
            )
            total_generation += generation
            total_emissions += emissions

    rows.append(
        {
            "plant": "TOTAL",
            "technology": "fleet",
            "generation_mwh": f"{total_generation:.2f}",
            "emissions_kg_co2": f"{total_emissions:.2f}",
        }
    )
    rows.append(
        {
            "plant": "FLEET_INTENSITY",
            "technology": "kg_co2_per_mwh",
            "generation_mwh": "",
            "emissions_kg_co2": f"{total_emissions / total_generation:.2f}",
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
