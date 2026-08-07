#!/usr/bin/env python3
"""Generate deterministic thermodynamic process scenarios."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "thermal_processes.csv"

ROWS = [
    {
        "scenario": "baseline_steam_cycle",
        "hot_temperature_k": 823.15,
        "cold_temperature_k": 303.15,
        "heat_input_mj": 1000.0,
        "second_law_fraction": 0.58,
        "ambient_temperature_k": 303.15,
        "heat_pump_fraction": 0.45,
        "charge_efficiency": 0.94,
        "discharge_efficiency": 0.90,
        "retention_fraction": 0.98,
    },
    {
        "scenario": "higher_temperature_source",
        "hot_temperature_k": 973.15,
        "cold_temperature_k": 303.15,
        "heat_input_mj": 1000.0,
        "second_law_fraction": 0.58,
        "ambient_temperature_k": 303.15,
        "heat_pump_fraction": 0.45,
        "charge_efficiency": 0.94,
        "discharge_efficiency": 0.90,
        "retention_fraction": 0.98,
    },
    {
        "scenario": "improved_cycle_design",
        "hot_temperature_k": 823.15,
        "cold_temperature_k": 303.15,
        "heat_input_mj": 1000.0,
        "second_law_fraction": 0.70,
        "ambient_temperature_k": 303.15,
        "heat_pump_fraction": 0.50,
        "charge_efficiency": 0.96,
        "discharge_efficiency": 0.92,
        "retention_fraction": 0.99,
    },
    {
        "scenario": "hot_weather_sink",
        "hot_temperature_k": 823.15,
        "cold_temperature_k": 318.15,
        "heat_input_mj": 1000.0,
        "second_law_fraction": 0.58,
        "ambient_temperature_k": 318.15,
        "heat_pump_fraction": 0.45,
        "charge_efficiency": 0.94,
        "discharge_efficiency": 0.90,
        "retention_fraction": 0.97,
    },
    {
        "scenario": "low_temperature_heat_pump",
        "hot_temperature_k": 323.15,
        "cold_temperature_k": 278.15,
        "heat_input_mj": 500.0,
        "second_law_fraction": 0.45,
        "ambient_temperature_k": 278.15,
        "heat_pump_fraction": 0.48,
        "charge_efficiency": 0.96,
        "discharge_efficiency": 0.93,
        "retention_fraction": 0.99,
    },
]


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(ROWS)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
