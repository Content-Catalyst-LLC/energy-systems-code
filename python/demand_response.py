#!/usr/bin/env python3
"""Demand response teaching model."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "synthetic" / "hourly_load_and_renewables.csv"
OUTPUT = ROOT / "outputs" / "tables" / "demand_response_results.csv"


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    threshold = 700.0
    max_shift_fraction = 0.08
    shifted_energy = 0.0
    adjusted = []

    for row in rows:
        demand = float(row["demand_mwh"])
        reduction = 0.0
        if demand > threshold:
            reduction = min(demand - threshold, demand * max_shift_fraction)
            shifted_energy += reduction
        adjusted.append(
            {
                "hour": row["hour"],
                "original_demand_mwh": f"{demand:.2f}",
                "demand_response_reduction_mwh": f"{reduction:.2f}",
                "adjusted_demand_mwh": f"{demand - reduction:.2f}",
            }
        )

    off_peak_hours = [row for row in adjusted if float(row["adjusted_demand_mwh"]) < 500]
    if off_peak_hours:
        add_back = shifted_energy / len(off_peak_hours)
        for row in off_peak_hours:
            row["adjusted_demand_mwh"] = f"{float(row['adjusted_demand_mwh']) + add_back:.2f}"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=adjusted[0].keys())
        writer.writeheader()
        writer.writerows(adjusted)

    print(f"Wrote {OUTPUT}")
    print(f"Shifted energy MWh: {shifted_energy:.2f}")


if __name__ == "__main__":
    main()
