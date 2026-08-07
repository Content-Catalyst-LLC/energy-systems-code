#!/usr/bin/env python3
"""Generate a deterministic regional energy-system teaching dataset."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

NODES = [
    ("solar_resource", "Solar resource", "resource", "solar radiation", "", 0.00),
    ("wind_resource", "Wind resource", "resource", "wind", "", 0.00),
    ("gas_resource", "Natural gas supply", "resource", "natural gas", "", 0.00),
    ("solar_plant", "Solar photovoltaic fleet", "conversion", "electricity", 420, 0.25),
    ("wind_plant", "Wind generation fleet", "conversion", "electricity", 360, 0.25),
    ("gas_plant", "Combined-cycle gas fleet", "conversion", "electricity", 520, 0.55),
    ("grid", "Transmission and distribution network", "network", "electricity", 1100, 0.90),
    ("battery", "Grid battery", "storage", "electricity", 180, 0.70),
    ("buildings", "Building end-use systems", "end_use", "electricity", 480, 0.75),
    ("industry", "Industrial end-use systems", "end_use", "electricity", 430, 0.80),
    ("transport", "Electric mobility systems", "end_use", "electricity", 210, 0.65),
    ("building_service", "Thermal comfort and building services", "service", "energy service", "", 0.95),
    ("industrial_service", "Industrial production service", "service", "energy service", "", 0.85),
    ("mobility_service", "Mobility service", "service", "energy service", "", 0.80),
]

# Baseline link inputs are balanced: each intermediate node's declared outgoing
# input equals the energy delivered to that node by upstream links.
LINKS = [
    ("solar_to_plant", "solar_resource", "solar_plant", 4300.0, 0.225, 40, 6, 1.0),
    ("wind_to_plant", "wind_resource", "wind_plant", 3600.0, 0.420, 15, 9, 1.0),
    ("gas_to_plant", "gas_resource", "gas_plant", 4200.0, 0.560, 415, 48, 1.0),
    ("solar_to_grid", "solar_plant", "grid", 967.5, 0.985, 0, 2, 1.0),
    ("wind_to_grid", "wind_plant", "grid", 1512.0, 0.985, 0, 3, 1.0),
    ("gas_to_grid", "gas_plant", "grid", 2352.0, 0.985, 0, 4, 1.0),
    ("grid_to_battery", "grid", "battery", 520.0, 0.940, 0, 7, 1.0),
    ("battery_to_buildings", "battery", "buildings", 488.8, 0.940, 0, 6, 1.0),
    ("grid_to_buildings", "grid", "buildings", 1700.0, 0.935, 0, 15, 1.0),
    ("grid_to_industry", "grid", "industry", 1600.0, 0.945, 0, 14, 1.0),
    ("grid_to_transport", "grid", "transport", 939.0275, 0.930, 0, 16, 1.0),
    ("buildings_to_service", "buildings", "building_service", 2048.972, 0.860, 0, 8, 1.0),
    ("industry_to_service", "industry", "industrial_service", 1512.0, 0.780, 0, 10, 1.0),
    ("transport_to_service", "transport", "mobility_service", 873.295575, 0.820, 0, 9, 1.0),
]


def write_csv(path: Path, fieldnames: list[str], rows: list[tuple[object, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(fieldnames)
        writer.writerows(rows)


def main() -> None:
    write_csv(
        RAW / "energy_nodes.csv",
        ["node_id", "name", "kind", "carrier", "capacity_mw", "criticality"],
        NODES,
    )
    write_csv(
        RAW / "energy_links.csv",
        [
            "link_id",
            "source",
            "target",
            "input_mwh",
            "efficiency",
            "emissions_kg_co2e_per_mwh_input",
            "variable_cost_usd_per_mwh_input",
            "availability",
        ],
        LINKS,
    )
    print(f"Wrote {RAW / 'energy_nodes.csv'}")
    print(f"Wrote {RAW / 'energy_links.csv'}")


if __name__ == "__main__":
    main()
