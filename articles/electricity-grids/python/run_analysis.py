#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from electricity_grids import (
    Branch,
    BusInjection,
    GridNetwork,
    frequency_deviation_hz,
    monte_carlo_peak_balance,
    reserve_margin,
    storage_dispatch,
    transmission_loss_mw,
)

RAW = ROOT / "data" / "raw"
OUT_TABLES = ROOT / "outputs" / "tables"
OUT_FIGURES = ROOT / "outputs" / "figures"
PROCESSED = ROOT / "data" / "processed"

for directory in (OUT_TABLES, OUT_FIGURES, PROCESSED):
    directory.mkdir(parents=True, exist_ok=True)

with (RAW / "branches.csv").open(newline="", encoding="utf-8") as handle:
    branches = [
        Branch(
            row["name"],
            row["from_bus"],
            row["to_bus"],
            float(row["reactance_pu"]),
            float(row["thermal_limit_mw"]),
            float(row["resistance_pu"]),
        )
        for row in csv.DictReader(handle)
    ]

with (RAW / "bus_angles.csv").open(newline="", encoding="utf-8") as handle:
    angles = {row["bus"]: float(row["angle_rad"]) for row in csv.DictReader(handle)}

with (RAW / "bus_injections.csv").open(newline="", encoding="utf-8") as handle:
    injections = [
        BusInjection(row["bus"], float(row["generation_mw"]), float(row["load_mw"]))
        for row in csv.DictReader(handle)
    ]

network = GridNetwork(branches)
flows = network.flows_from_angles(angles, base_mva=100.0)
util = network.utilization(flows)

flow_rows = []
for branch in branches:
    flow = flows[branch.name]
    loss = transmission_loss_mw(
        flow,
        branch.resistance_pu,
        voltage_pu=1.0,
        base_mva=100.0,
    )
    flow_rows.append({
        "branch": branch.name,
        "from_bus": branch.from_bus,
        "to_bus": branch.to_bus,
        "flow_mw": flow,
        "thermal_limit_mw": branch.thermal_limit_mw,
        "utilization": util[branch.name],
        "estimated_loss_mw": loss,
    })

with (OUT_TABLES / "branch_flows.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(flow_rows[0].keys()))
    writer.writeheader()
    writer.writerows(flow_rows)

balance = network.system_balance(injections)
by_bus = network.aggregate_by_bus(injections)

with (OUT_TABLES / "bus_balance.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["bus", "net_injection_mw"])
    for bus, net in by_bus.items():
        writer.writerow([bus, f"{net:.6f}"])

available_capacity = 3350.0
peak_load = 3000.0
margin = reserve_margin(available_capacity, peak_load)
frequency_example = frequency_deviation_hz(
    power_imbalance_mw=450.0,
    frequency_response_mw_per_hz=7500.0,
)
storage_example = storage_dispatch(
    state_of_charge_mwh=900.0,
    net_load_mw=250.0,
    duration_hours=1.0,
    power_limit_mw=300.0,
    energy_capacity_mwh=1200.0,
    round_trip_efficiency=0.90,
)
uncertainty = monte_carlo_peak_balance(
    available_capacity_mw=available_capacity,
    peak_load_mw=peak_load,
    capacity_sigma=0.04,
    load_sigma=0.03,
    draws=2000,
    seed=20260806,
)

payload = {
    "article": "Electricity Grids",
    "series_position": 8,
    "bus_count": len(network.buses),
    "branch_count": len(branches),
    "system_net_injection_mw": balance,
    "reserve_margin": margin,
    "frequency_deviation_example_hz": frequency_example,
    "storage_example": storage_example,
    "overloaded_branches": network.overloaded(flows),
    "uncertainty": uncertainty,
    "validation": {
        "four_buses": len(network.buses) == 4,
        "five_branches": len(branches) == 5,
        "finite_flows": all(abs(row["flow_mw"]) < 1e9 for row in flow_rows),
        "positive_limits": all(row["thermal_limit_mw"] > 0 for row in flow_rows),
        "nonnegative_losses": all(row["estimated_loss_mw"] >= 0 for row in flow_rows),
        "uncertainty_ordered": (
            uncertainty["p05_margin_mw"]
            <= uncertainty["p50_margin_mw"]
            <= uncertainty["p95_margin_mw"]
        ),
    },
}

(OUT_TABLES / "analysis_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

# Dependency-free SVG: branch utilization bars.
max_util = max(row["utilization"] for row in flow_rows)
svg_w = 1100
row_h = 62
svg_h = 105 + row_h * len(flow_rows)
bar_x = 330
bar_max = 650

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="24" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700">Electricity Grid Branch Utilization</text>',
    '<text x="24" y="59" font-family="Arial, sans-serif" font-size="13">Synthetic DC power-flow example; bar length represents absolute loading relative to branch limits.</text>',
]

for idx, row in enumerate(flow_rows):
    y = 98 + idx * row_h
    width = 0 if max_util == 0 else bar_max * row["utilization"] / max_util
    label = html.escape(row["branch"])
    value = html.escape(f'{100 * row["utilization"]:.1f}%')
    parts.append(f'<text x="24" y="{y+18}" font-family="Arial, sans-serif" font-size="13">{label}</text>')
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{width:.2f}" height="24" fill="currentColor" opacity="0.78"/>')
    parts.append(f'<text x="{bar_x + width + 8:.2f}" y="{y+17}" font-family="Arial, sans-serif" font-size="12">{value}</text>')

parts.append("</svg>")
(OUT_FIGURES / "branch_utilization.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")

for name in ("branches.csv", "bus_angles.csv", "bus_injections.csv"):
    (PROCESSED / name).write_text((RAW / name).read_text(encoding="utf-8"), encoding="utf-8")

print(f"Buses: {len(network.buses)}")
print(f"Branches: {len(branches)}")
print(f"System injection balance: {balance:.3f} MW")
print(f"Reserve margin: {margin:.6f}")
print(f"Frequency example: {frequency_example:.6f} Hz")
print(f"Outputs: {ROOT / 'outputs'}")
