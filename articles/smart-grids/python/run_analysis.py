#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from smart_grids import (
    DERResource,
    aggregate_der_capacity,
    annual_energy_reduction_mwh,
    charging_power_mw,
    communications_availability,
    demand_response_net_load,
    dispatch_available_der,
    flisr_customer_hours_avoided,
    load_factor,
    monte_carlo_flexible_peak,
    restoration_fraction,
)

RAW = ROOT / "data" / "raw"
OUT_TABLES = ROOT / "outputs" / "tables"
OUT_FIGURES = ROOT / "outputs" / "figures"
PROCESSED = ROOT / "data" / "processed"

for directory in (OUT_TABLES, OUT_FIGURES, PROCESSED):
    directory.mkdir(parents=True, exist_ok=True)

with (RAW / "interval_demand.csv").open(newline="", encoding="utf-8") as handle:
    interval_rows = list(csv.DictReader(handle))

demand = [float(row["demand_mw"]) for row in interval_rows]
peak = max(demand)
average = sum(demand) / len(demand)
daily_energy = sum(demand)
daily_load_factor = load_factor(
    energy_mwh=daily_energy,
    hours=24.0,
    peak_mw=peak,
)

with (OUT_TABLES / "interval_demand_summary.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["metric", "value"])
    writer.writerow(["peak_mw", peak])
    writer.writerow(["average_mw", average])
    writer.writerow(["daily_energy_mwh", daily_energy])
    writer.writerow(["load_factor", daily_load_factor])

with (RAW / "der_resources.csv").open(newline="", encoding="utf-8") as handle:
    resource_rows = list(csv.DictReader(handle))

resources = [
    DERResource(
        name=row["name"],
        power_mw=float(row["power_mw"]),
        availability=float(row["availability"]),
        response_fraction=float(row["response_fraction"]),
    )
    for row in resource_rows
]

der_nameplate = aggregate_der_capacity(resources)
der_dispatchable = dispatch_available_der(resources)

with (OUT_TABLES / "der_summary.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["metric", "value"])
    writer.writerow(["nameplate_mw", der_nameplate])
    writer.writerow(["expected_dispatchable_mw", der_dispatchable])

with (RAW / "automation_scenarios.csv").open(newline="", encoding="utf-8") as handle:
    automation_rows = list(csv.DictReader(handle))

automation_results = []
for row in automation_rows:
    total = int(row["total_customers"])
    restored = int(row["customers_restored"])
    manual = float(row["manual_minutes"])
    automated = float(row["automated_minutes"])
    automation_results.append({
        "scenario": row["scenario"],
        "restoration_fraction": restoration_fraction(total, restored),
        "customer_hours_avoided": flisr_customer_hours_avoided(
            restored,
            manual,
            automated,
        ),
    })

with (OUT_TABLES / "automation_summary.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(automation_results[0].keys()))
    writer.writeheader()
    writer.writerows(automation_results)

unmanaged_ev = charging_power_mw(10000, 14, 2)
managed_ev = charging_power_mw(10000, 14, 7)
dr_net = demand_response_net_load(85, 12)
volt_var_savings = annual_energy_reduction_mwh(10, 0.012, 4000)
flisr_example = flisr_customer_hours_avoided(9800, 90, 2)
communications = communications_availability(0.995, 0.98)

uncertainty = monte_carlo_flexible_peak(
    baseline_peak_mw=peak,
    flexible_capacity_mw=der_dispatchable,
    participation_mean=0.75,
    participation_sigma=0.10,
    forecast_sigma_fraction=0.03,
    draws=2500,
    seed=20260806,
)

payload = {
    "article": "Smart Grids",
    "series_position": 11,
    "interval_count": len(interval_rows),
    "der_resource_count": len(resources),
    "automation_scenario_count": len(automation_results),
    "daily_peak_mw": peak,
    "daily_load_factor": daily_load_factor,
    "der_nameplate_mw": der_nameplate,
    "der_dispatchable_mw": der_dispatchable,
    "article_examples": {
        "unmanaged_ev_mw": unmanaged_ev,
        "managed_ev_mw": managed_ev,
        "demand_response_net_mw": dr_net,
        "volt_var_savings_mwh": volt_var_savings,
        "flisr_customer_hours_avoided": flisr_example,
        "communications_availability": communications,
    },
    "uncertainty": uncertainty,
    "validation": {
        "twenty_four_intervals": len(interval_rows) == 24,
        "five_der_resources": len(resources) == 5,
        "five_automation_scenarios": len(automation_results) == 5,
        "managed_ev_below_unmanaged": managed_ev < unmanaged_ev,
        "demand_response_73mw": abs(dr_net - 73.0) < 1e-12,
        "volt_var_480mwh": abs(volt_var_savings - 480.0) < 1e-12,
        "flisr_example_matches_article": abs(flirs := flisr_example - (9800 * 88 / 60)) < 1e-9,
        "communications_valid": 0 <= communications <= 1,
        "uncertainty_ordered": (
            uncertainty["p05_net_peak_mw"]
            <= uncertainty["p50_net_peak_mw"]
            <= uncertainty["p95_net_peak_mw"]
        ),
    },
}

(OUT_TABLES / "analysis_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

max_hours = max(row["customer_hours_avoided"] for row in automation_results)
svg_w = 1100
row_h = 62
svg_h = 105 + row_h * len(automation_results)
bar_x = 350
bar_max = 620

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="24" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700">Smart-Grid Restoration Benefit</text>',
    '<text x="24" y="59" font-family="Arial, sans-serif" font-size="13">Synthetic automation scenarios; bar length represents customer interruption-hours avoided.</text>',
]

for idx, row in enumerate(automation_results):
    y = 98 + idx * row_h
    value_num = row["customer_hours_avoided"]
    width = 0 if max_hours == 0 else bar_max * value_num / max_hours
    label = html.escape(row["scenario"])
    value = html.escape(f'{value_num:,.0f} customer-hours')
    parts.append(f'<text x="24" y="{y+18}" font-family="Arial, sans-serif" font-size="13">{label}</text>')
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{width:.2f}" height="24" fill="currentColor" opacity="0.78"/>')
    parts.append(f'<text x="{bar_x + width + 8:.2f}" y="{y+17}" font-family="Arial, sans-serif" font-size="12">{value}</text>')

parts.append("</svg>")
(OUT_FIGURES / "automation_restoration_benefit.svg").write_text(
    "\n".join(parts) + "\n",
    encoding="utf-8",
)

for name in ("interval_demand.csv", "der_resources.csv", "automation_scenarios.csv"):
    (PROCESSED / name).write_text(
        (RAW / name).read_text(encoding="utf-8"),
        encoding="utf-8",
    )

print(f"Intervals: {len(interval_rows)}")
print(f"Daily peak: {peak:.3f} MW")
print(f"DER nameplate: {der_nameplate:.3f} MW")
print(f"Expected dispatchable DER: {der_dispatchable:.3f} MW")
print(f"Managed EV charging: {managed_ev:.3f} MW")
print(f"FLISR customer-hours avoided: {flisr_example:.3f}")
print(f"Outputs: {ROOT / 'outputs'}")
