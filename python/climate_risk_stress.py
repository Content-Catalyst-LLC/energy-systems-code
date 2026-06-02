#!/usr/bin/env python3
"""Climate risk stress testing for energy infrastructure."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "synthetic" / "climate_stressors.csv"
OUTPUT = ROOT / "outputs" / "tables" / "climate_risk_stress_results.csv"


def main() -> None:
    rows = []
    with INPUT.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            baseline = float(row["baseline_risk_score"])
            midcentury = float(row["midcentury_risk_score"])
            increase = midcentury - baseline
            rows.append(
                {
                    "asset": row["asset"],
                    "stressor": row["stressor"],
                    "baseline_risk_score": f"{baseline:.2f}",
                    "midcentury_risk_score": f"{midcentury:.2f}",
                    "risk_increase": f"{increase:.2f}",
                    "adaptation_priority": row["adaptation_priority"],
                }
            )

    rows.sort(key=lambda item: float(item["midcentury_risk_score"]), reverse=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
