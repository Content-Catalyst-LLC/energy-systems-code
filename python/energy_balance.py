#!/usr/bin/env python3
"""Dependency-light energy balance and storage dispatch workflow."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "synthetic" / "hourly_energy_profile.csv"
OUTPUT_TABLE = ROOT / "outputs" / "tables" / "energy_dispatch_summary.csv"


@dataclass
class HourlyRow:
    hour: int
    demand_mwh: float
    solar_mwh: float
    wind_mwh: float
    thermal_mwh: float
    emissions_factor: float


@dataclass
class DispatchRow:
    hour: int
    demand_mwh: float
    renewable_mwh: float
    thermal_used_mwh: float
    battery_state_mwh: float
    curtailed_mwh: float
    unmet_mwh: float
    emissions_tco2: float


def read_profile(path: Path) -> List[HourlyRow]:
    rows: List[HourlyRow] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append(
                HourlyRow(
                    hour=int(raw["hour"]),
                    demand_mwh=float(raw["demand_mwh"]),
                    solar_mwh=float(raw["solar_mwh"]),
                    wind_mwh=float(raw["wind_mwh"]),
                    thermal_mwh=float(raw["thermal_mwh"]),
                    emissions_factor=float(raw["emissions_factor_tco2_per_mwh"]),
                )
            )
    return rows


def dispatch(
    rows: Iterable[HourlyRow],
    battery_capacity_mwh: float = 80.0,
    initial_battery_mwh: float = 20.0,
    charge_efficiency: float = 0.92,
    discharge_efficiency: float = 0.92,
) -> List[DispatchRow]:
    battery_state = max(0.0, min(initial_battery_mwh, battery_capacity_mwh))
    results: List[DispatchRow] = []

    for row in rows:
        renewable = row.solar_mwh + row.wind_mwh
        remaining_demand = row.demand_mwh
        thermal_used = 0.0
        curtailed = 0.0
        unmet = 0.0

        renewable_used = min(renewable, remaining_demand)
        remaining_demand -= renewable_used
        surplus_renewable = renewable - renewable_used

        if surplus_renewable > 0:
            available_storage = battery_capacity_mwh - battery_state
            charged = min(surplus_renewable * charge_efficiency, available_storage)
            battery_state += charged
            curtailed += max(0.0, surplus_renewable - charged / charge_efficiency)

        if remaining_demand > 0 and battery_state > 0:
            discharge_needed = remaining_demand / discharge_efficiency
            discharged = min(discharge_needed, battery_state)
            battery_state -= discharged
            remaining_demand -= discharged * discharge_efficiency

        if remaining_demand > 0:
            thermal_used = min(row.thermal_mwh, remaining_demand)
            remaining_demand -= thermal_used

        unmet = max(0.0, remaining_demand)
        emissions = thermal_used * row.emissions_factor

        results.append(
            DispatchRow(
                hour=row.hour,
                demand_mwh=round(row.demand_mwh, 3),
                renewable_mwh=round(renewable, 3),
                thermal_used_mwh=round(thermal_used, 3),
                battery_state_mwh=round(battery_state, 3),
                curtailed_mwh=round(curtailed, 3),
                unmet_mwh=round(unmet, 3),
                emissions_tco2=round(emissions, 3),
            )
        )
    return results


def capacity_factor(actual_generation_mwh: float, nameplate_mw: float, hours: float) -> float:
    if nameplate_mw <= 0 or hours <= 0:
        raise ValueError("Nameplate capacity and hours must be positive.")
    return actual_generation_mwh / (nameplate_mw * hours)


def write_results(rows: List[DispatchRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(DispatchRow.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def main() -> None:
    profile = read_profile(DATA_PATH)
    results = dispatch(profile)
    write_results(results, OUTPUT_TABLE)

    total_demand = sum(row.demand_mwh for row in results)
    total_unmet = sum(row.unmet_mwh for row in results)
    total_emissions = sum(row.emissions_tco2 for row in results)
    reliability = 1.0 - (total_unmet / total_demand if total_demand else 0.0)

    print("Energy Systems Dispatch Summary")
    print(f"Hours modeled: {len(results)}")
    print(f"Total demand: {total_demand:.2f} MWh")
    print(f"Unmet demand: {total_unmet:.2f} MWh")
    print(f"Reliability proxy: {reliability:.3f}")
    print(f"Thermal emissions: {total_emissions:.2f} tCO2")
    print(f"Output written to: {OUTPUT_TABLE}")


if __name__ == "__main__":
    main()
