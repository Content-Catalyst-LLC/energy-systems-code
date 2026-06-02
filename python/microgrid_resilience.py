#!/usr/bin/env python3
"""Microgrid resilience scenario scoring."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "synthetic" / "outage_restoration_scenarios.csv"
OUTPUT = ROOT / "outputs" / "tables" / "microgrid_resilience_results.csv"


def main() -> None:
    rows = []
    with INPUT.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            critical_load = float(row["critical_load_mwh"])
            generation = float(row["available_generation_mwh"])
            storage = float(row["storage_initial_mwh"])
            restoration_hours = float(row["restoration_hours"])

            served = min(critical_load, generation + storage)
            unserved = max(0.0, critical_load - served)
            critical_load_served_fraction = served / critical_load
            resilience_score = critical_load_served_fraction * (1 / (1 + restoration_hours / 48))

            rows.append(
                {
                    "scenario": row["scenario"],
                    "critical_load_served_fraction": f"{critical_load_served_fraction:.3f}",
                    "unserved_critical_load_mwh": f"{unserved:.2f}",
                    "resilience_score": f"{resilience_score:.3f}",
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
