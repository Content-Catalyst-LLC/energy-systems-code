#!/usr/bin/env python3
"""Renewable-plus-storage dispatch model using only the Python standard library."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "synthetic" / "hourly_load_and_renewables.csv"
OUTPUT = ROOT / "outputs" / "tables" / "storage_dispatch_results.csv"


@dataclass
class DispatchState:
    hour: int
    demand_mwh: float
    renewable_mwh: float
    state_of_charge_mwh: float
    unmet_demand_mwh: float
    curtailed_mwh: float


def simulate_dispatch(
    rows: list[dict[str, float]],
    battery_capacity_mwh: float = 720.0,
    initial_soc_mwh: float = 300.0,
    charge_efficiency: float = 0.94,
    discharge_efficiency: float = 0.94,
) -> list[DispatchState]:
    soc = min(initial_soc_mwh, battery_capacity_mwh)
    results: list[DispatchState] = []

    for row in rows:
        demand = row["demand_mwh"]
        renewable = row["solar_mwh"] + row["wind_mwh"]
        net = renewable - demand
        unmet = 0.0
        curtailed = 0.0

        if net >= 0:
            available_space = battery_capacity_mwh - soc
            charged = min(net * charge_efficiency, available_space)
            soc += charged
            curtailed = max(0.0, net - charged / charge_efficiency)
        else:
            deficit = abs(net)
            discharge_needed = deficit / discharge_efficiency
            discharged = min(discharge_needed, soc)
            soc -= discharged
            unmet = max(0.0, deficit - discharged * discharge_efficiency)

        results.append(
            DispatchState(
                hour=int(row["hour"]),
                demand_mwh=demand,
                renewable_mwh=renewable,
                state_of_charge_mwh=round(soc, 3),
                unmet_demand_mwh=round(unmet, 3),
                curtailed_mwh=round(curtailed, 3),
            )
        )

    return results


def read_rows() -> list[dict[str, float]]:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def main() -> None:
    results = simulate_dispatch(read_rows())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=results[0].__dict__.keys())
        writer.writeheader()
        for row in results:
            writer.writerow(row.__dict__)

    total_unmet = sum(row.unmet_demand_mwh for row in results)
    total_curtailed = sum(row.curtailed_mwh for row in results)
    print(f"Wrote {OUTPUT}")
    print(f"Total unmet demand MWh: {total_unmet:.2f}")
    print(f"Total curtailed renewable MWh: {total_curtailed:.2f}")


if __name__ == "__main__":
    main()
