#!/usr/bin/env python3
"""Energy affordability and energy burden metrics."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "synthetic" / "household_energy_burden.csv"
OUTPUT = ROOT / "outputs" / "tables" / "energy_burden_results.csv"


def category(burden: float) -> str:
    if burden >= 0.10:
        return "severe"
    if burden >= 0.06:
        return "high"
    if burden >= 0.03:
        return "moderate"
    return "low"


def main() -> None:
    rows = []
    with INPUT.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            income = float(row["income_usd_yr"])
            cost = float(row["annual_energy_cost_usd"])
            burden = cost / income
            rows.append(
                {
                    "household_id": row["household_id"],
                    "region": row["region"],
                    "housing_type": row["housing_type"],
                    "energy_burden": f"{burden:.3f}",
                    "burden_category": category(burden),
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
