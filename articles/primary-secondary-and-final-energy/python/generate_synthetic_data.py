#!/usr/bin/env python3
"""Generate deterministic pathway data used by the article workflow."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

rows = [
    {
        "pathway": "gas_to_building_heat",
        "label": "Natural gas to building heat",
        "primary_energy_mwh": 4200,
        "conversion_efficiency": 0.96,
        "delivery_efficiency": 0.98,
        "end_use_efficiency": 0.88,
        "service_factor": 0.92,
        "energy_sector_own_use_fraction": 0.025,
        "non_energy_use_fraction": 0.000,
    },
    {
        "pathway": "coal_to_electric_motor",
        "label": "Coal to electric motor service",
        "primary_energy_mwh": 3600,
        "conversion_efficiency": 0.38,
        "delivery_efficiency": 0.94,
        "end_use_efficiency": 0.91,
        "service_factor": 0.95,
        "energy_sector_own_use_fraction": 0.040,
        "non_energy_use_fraction": 0.000,
    },
    {
        "pathway": "wind_to_electric_motor",
        "label": "Wind electricity to motor service",
        "primary_energy_mwh": 1600,
        "conversion_efficiency": 1.00,
        "delivery_efficiency": 0.95,
        "end_use_efficiency": 0.92,
        "service_factor": 0.95,
        "energy_sector_own_use_fraction": 0.015,
        "non_energy_use_fraction": 0.000,
    },
    {
        "pathway": "oil_to_mobility",
        "label": "Oil products to mobility service",
        "primary_energy_mwh": 2800,
        "conversion_efficiency": 0.90,
        "delivery_efficiency": 0.97,
        "end_use_efficiency": 0.24,
        "service_factor": 0.82,
        "energy_sector_own_use_fraction": 0.035,
        "non_energy_use_fraction": 0.030,
    },
    {
        "pathway": "biomass_to_industrial_heat",
        "label": "Biomass to industrial heat",
        "primary_energy_mwh": 1100,
        "conversion_efficiency": 0.87,
        "delivery_efficiency": 0.96,
        "end_use_efficiency": 0.72,
        "service_factor": 0.90,
        "energy_sector_own_use_fraction": 0.030,
        "non_energy_use_fraction": 0.000,
    },
]

path = RAW / "energy_pathways.csv"
with path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {path}")

method_rows = [
    {"technology": "Wind", "electricity_mwh": 1000, "reference_efficiency": 0.40},
    {"technology": "Solar PV", "electricity_mwh": 1000, "reference_efficiency": 0.40},
    {"technology": "Hydropower", "electricity_mwh": 1000, "reference_efficiency": 0.40},
    {"technology": "Nuclear", "electricity_mwh": 1000, "reference_efficiency": 0.33},
]
method_path = RAW / "primary_energy_methods.csv"
with method_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(method_rows[0].keys()))
    writer.writeheader()
    writer.writerows(method_rows)
print(f"Wrote {method_path}")
