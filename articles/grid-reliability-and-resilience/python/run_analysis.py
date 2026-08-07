#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from grid_reliability import (
    OutageEvent,
    ResilienceScenario,
    annualized_risk,
    caidi,
    expected_unserved_energy_mwh,
    frequency_deviation_hz,
    monte_carlo_resource_adequacy,
    reserve_margin,
    restoration_auc,
    saidi,
    saifi,
)

RAW = ROOT / "data" / "raw"
OUT_TABLES = ROOT / "outputs" / "tables"
OUT_FIGURES = ROOT / "outputs" / "figures"
PROCESSED = ROOT / "data" / "processed"

for directory in (OUT_TABLES, OUT_FIGURES, PROCESSED):
    directory.mkdir(parents=True, exist_ok=True)

with (RAW / "outages.csv").open(newline="", encoding="utf-8") as handle:
    outage_rows = list(csv.DictReader(handle))

events = [
    OutageEvent(
        customers_affected=int(row["customers_affected"]),
        duration_hours=float(row["duration_hours"]),
        unserved_mw=float(row["unserved_mw"]),
        probability=float(row["probability"]),
    )
    for row in outage_rows
]

total_customers = 100000
saidi_value = saidi(events, total_customers)
saifi_value = saifi(events, total_customers)
caidi_value = caidi(events, total_customers)
eue_value = expected_unserved_energy_mwh(events)

with (RAW / "resilience_scenarios.csv").open(newline="", encoding="utf-8") as handle:
    scenario_rows = list(csv.DictReader(handle))

scenarios = [
    ResilienceScenario(
        name=row["name"],
        annual_probability=float(row["annual_probability"]),
        consequence_million_usd=float(row["consequence_million_usd"]),
        service_retained_fraction=float(row["service_retained_fraction"]),
    ).validate()
    for row in scenario_rows
]

risk_rows = []
for s in scenarios:
    risk_rows.append({
        "scenario": s.name,
        "annual_probability": s.annual_probability,
        "consequence_million_usd": s.consequence_million_usd,
        "service_retained_fraction": s.service_retained_fraction,
        "annualized_risk_million_usd": annualized_risk(
            s.annual_probability,
            s.consequence_million_usd,
        ),
    })

with (OUT_TABLES / "resilience_scenarios.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(risk_rows[0].keys()))
    writer.writeheader()
    writer.writerows(risk_rows)

with (RAW / "restoration_curve.csv").open(newline="", encoding="utf-8") as handle:
    restoration_rows = list(csv.DictReader(handle))

hours = [float(row["hours"]) for row in restoration_rows]
service = [float(row["service_fraction"]) for row in restoration_rows]
restoration_service_hours = restoration_auc(hours, service)

available_capacity = 42000.0
peak_load = 36000.0
reserve = reserve_margin(available_capacity, peak_load)
frequency_example = frequency_deviation_hz(600.0, 10000.0)

uncertainty = monte_carlo_resource_adequacy(
    dependable_capacity_mw=available_capacity,
    peak_load_mw=peak_load,
    capacity_sigma=0.05,
    load_sigma=0.04,
    draws=3000,
    seed=20260806,
)

reliability_summary = {
    "total_customers": total_customers,
    "event_count": len(events),
    "saidi_hours_per_customer": saidi_value,
    "saifi_interruptions_per_customer": saifi_value,
    "caidi_hours_per_interruption": caidi_value,
    "expected_unserved_energy_mwh": eue_value,
}

with (OUT_TABLES / "reliability_summary.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["metric", "value"])
    for key, value in reliability_summary.items():
        writer.writerow([key, value])

payload = {
    "article": "Grid Reliability and Resilience",
    "series_position": 9,
    "reliability": reliability_summary,
    "reserve_margin": reserve,
    "frequency_deviation_example_hz": frequency_example,
    "restoration_service_hours": restoration_service_hours,
    "scenario_count": len(scenarios),
    "uncertainty": uncertainty,
    "validation": {
        "five_outage_events": len(events) == 5,
        "five_resilience_scenarios": len(scenarios) == 5,
        "saidi_positive": saidi_value > 0,
        "saifi_positive": saifi_value > 0,
        "caidi_positive": caidi_value > 0,
        "eue_nonnegative": eue_value >= 0,
        "reserve_margin_positive": reserve > 0,
        "frequency_drop_negative": frequency_example < 0,
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

max_risk = max(row["annualized_risk_million_usd"] for row in risk_rows)
svg_w = 1100
row_h = 62
svg_h = 105 + row_h * len(risk_rows)
bar_x = 340
bar_max = 640

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="24" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700">Grid Resilience Scenario Risk</text>',
    '<text x="24" y="59" font-family="Arial, sans-serif" font-size="13">Synthetic teaching cases; annualized risk combines event probability and consequence.</text>',
]

for idx, row in enumerate(risk_rows):
    y = 98 + idx * row_h
    risk = row["annualized_risk_million_usd"]
    width = 0 if max_risk == 0 else bar_max * risk / max_risk
    label = html.escape(row["scenario"])
    value = html.escape(f'${risk:.3f}M/yr')
    parts.append(f'<text x="24" y="{y+18}" font-family="Arial, sans-serif" font-size="13">{label}</text>')
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{width:.2f}" height="24" fill="currentColor" opacity="0.78"/>')
    parts.append(f'<text x="{bar_x + width + 8:.2f}" y="{y+17}" font-family="Arial, sans-serif" font-size="12">{value}</text>')

parts.append("</svg>")
(OUT_FIGURES / "resilience_risk_comparison.svg").write_text(
    "\n".join(parts) + "\n",
    encoding="utf-8",
)

for name in ("outages.csv", "resilience_scenarios.csv", "restoration_curve.csv"):
    (PROCESSED / name).write_text(
        (RAW / name).read_text(encoding="utf-8"),
        encoding="utf-8",
    )

print(f"SAIDI: {saidi_value:.6f} h/customer")
print(f"SAIFI: {saifi_value:.6f} interruptions/customer")
print(f"CAIDI: {caidi_value:.6f} h/interruption")
print(f"EUE: {eue_value:.6f} MWh")
print(f"Reserve margin: {reserve:.6f}")
print(f"Frequency example: {frequency_example:.6f} Hz")
print(f"Outputs: {ROOT / 'outputs'}")
