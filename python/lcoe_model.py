#!/usr/bin/env python3
"""Simplified levelized cost of energy model."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "synthetic" / "lcoe_assumptions.csv"
OUTPUT = ROOT / "outputs" / "tables" / "lcoe_results.csv"


def capital_recovery_factor(rate: float, years: float) -> float:
    if rate == 0:
        return 1 / years
    return rate * (1 + rate) ** years / ((1 + rate) ** years - 1)


def main() -> None:
    rows = []
    with INPUT.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            capex = float(row["capex_usd_kw"])
            fixed_om = float(row["fixed_om_usd_kw_yr"])
            variable_om = float(row["variable_om_usd_mwh"])
            fuel = float(row["fuel_usd_mwh"])
            cf = float(row["capacity_factor"])
            life = float(row["asset_life_years"])
            rate = float(row["discount_rate"])

            annual_mwh_per_kw = 8.760 * cf
            crf = capital_recovery_factor(rate, life)
            capital_component = capex * crf / annual_mwh_per_kw
            fixed_component = fixed_om / annual_mwh_per_kw
            lcoe = capital_component + fixed_component + variable_om + fuel

            rows.append(
                {
                    "technology": row["technology"],
                    "capital_component_usd_mwh": f"{capital_component:.2f}",
                    "fixed_om_component_usd_mwh": f"{fixed_component:.2f}",
                    "variable_plus_fuel_usd_mwh": f"{variable_om + fuel:.2f}",
                    "simplified_lcoe_usd_mwh": f"{lcoe:.2f}",
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
