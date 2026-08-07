#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from transmission_distribution import (
    ExpansionOption,
    HostingCase,
    congestion_cost,
    evaluate_hosting_case,
    feeder_utilization,
    rank_expansion_options,
    three_phase_current_a,
    three_phase_loss_kw,
    transformer_loading,
)

RAW = ROOT / "data" / "raw"
OUT_TABLES = ROOT / "outputs" / "tables"
OUT_FIGURES = ROOT / "outputs" / "figures"
PROCESSED = ROOT / "data" / "processed"

for directory in (OUT_TABLES, OUT_FIGURES, PROCESSED):
    directory.mkdir(parents=True, exist_ok=True)

with (RAW / "feeders.csv").open(newline="", encoding="utf-8") as handle:
    feeders = list(csv.DictReader(handle))

feeder_rows = []
for row in feeders:
    rating = float(row["rating_mva"])
    peak = float(row["peak_mva"])
    pf = float(row["power_factor"])
    utilization = feeder_utilization(peak, rating)
    current = three_phase_current_a(
        power_mw=peak * pf,
        voltage_kv=13.8,
        power_factor=pf,
    )
    loss_kw = three_phase_loss_kw(
        current_a=current,
        resistance_ohm_per_phase=float(row["resistance_ohm"]),
    )
    feeder_rows.append({
        "feeder": row["feeder"],
        "rating_mva": rating,
        "peak_mva": peak,
        "power_factor": pf,
        "utilization": utilization,
        "headroom_mva": max(0.0, rating - peak),
        "current_a_at_13_8kv": current,
        "estimated_resistive_loss_kw": loss_kw,
    })

with (OUT_TABLES / "feeder_summary.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(feeder_rows[0].keys()))
    writer.writeheader()
    writer.writerows(feeder_rows)

with (RAW / "hosting_cases.csv").open(newline="", encoding="utf-8") as handle:
    hosting_rows = list(csv.DictReader(handle))

hosting_results = []
for row in hosting_rows:
    case = HostingCase(
        name=row["name"],
        feeder_rating_mva=float(row["feeder_rating_mva"]),
        base_peak_mva=float(row["base_peak_mva"]),
        added_load_mw=float(row["added_load_mw"]),
        added_generation_mw=float(row["added_generation_mw"]),
        power_factor=float(row["power_factor"]),
    )
    hosting_results.append(evaluate_hosting_case(case))

with (OUT_TABLES / "hosting_capacity_cases.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(hosting_results[0].keys()))
    writer.writeheader()
    writer.writerows(hosting_results)

with (RAW / "expansion_options.csv").open(newline="", encoding="utf-8") as handle:
    option_rows = list(csv.DictReader(handle))

options = [
    ExpansionOption(
        name=row["name"],
        capital_cost_million=float(row["capital_cost_million"]),
        added_capacity_mw=float(row["added_capacity_mw"]),
        annual_loss_reduction_mwh=float(row["annual_loss_reduction_mwh"]),
        congestion_savings_million_per_year=float(row["congestion_savings_million_per_year"]),
        implementation_years=float(row["implementation_years"]),
    )
    for row in option_rows
]

ranking = rank_expansion_options(options)

with (OUT_TABLES / "expansion_ranking.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(ranking[0].keys()))
    writer.writeheader()
    writer.writerows(ranking)

article_current_115 = three_phase_current_a(500, 115, 1.0)
article_current_345 = three_phase_current_a(500, 345, 1.0)
article_loss = three_phase_loss_kw(800, 0.08)
article_transformer_loading = transformer_loading(510, 500)
article_congestion_cost = congestion_cost(200, 85, 30)

payload = {
    "article": "Transmission and Distribution Systems",
    "series_position": 10,
    "feeder_count": len(feeder_rows),
    "hosting_case_count": len(hosting_results),
    "expansion_option_count": len(options),
    "article_examples": {
        "current_500mw_115kv_a": article_current_115,
        "current_500mw_345kv_a": article_current_345,
        "three_phase_loss_800a_0_08ohm_kw": article_loss,
        "transformer_loading_510_on_500": article_transformer_loading,
        "congestion_cost_200mwh_usd": article_congestion_cost,
    },
    "validation": {
        "five_feeders": len(feeder_rows) == 5,
        "five_hosting_cases": len(hosting_results) == 5,
        "five_expansion_options": len(options) == 5,
        "high_voltage_reduces_current": article_current_345 < article_current_115,
        "article_loss_153_6kw": abs(article_loss - 153.6) < 1e-9,
        "transformer_loading_102_percent": abs(article_transformer_loading - 1.02) < 1e-12,
        "congestion_cost_11000": abs(article_congestion_cost - 11000.0) < 1e-9,
        "all_feeder_losses_nonnegative": all(
            row["estimated_resistive_loss_kw"] >= 0 for row in feeder_rows
        ),
    },
}

(OUT_TABLES / "analysis_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

max_util = max(row["utilization"] for row in feeder_rows)
svg_w = 1100
row_h = 62
svg_h = 105 + row_h * len(feeder_rows)
bar_x = 330
bar_max = 650

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="24" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700">Distribution Feeder Peak Utilization</text>',
    '<text x="24" y="59" font-family="Arial, sans-serif" font-size="13">Synthetic teaching feeders; bar length represents peak apparent-power loading relative to feeder rating.</text>',
]

for idx, row in enumerate(feeder_rows):
    y = 98 + idx * row_h
    width = 0 if max_util == 0 else bar_max * row["utilization"] / max_util
    label = html.escape(row["feeder"])
    value = html.escape(f'{100 * row["utilization"]:.1f}%')
    parts.append(f'<text x="24" y="{y+18}" font-family="Arial, sans-serif" font-size="13">{label}</text>')
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{width:.2f}" height="24" fill="currentColor" opacity="0.78"/>')
    parts.append(f'<text x="{bar_x + width + 8:.2f}" y="{y+17}" font-family="Arial, sans-serif" font-size="12">{value}</text>')

parts.append("</svg>")
(OUT_FIGURES / "feeder_utilization.svg").write_text(
    "\n".join(parts) + "\n",
    encoding="utf-8",
)

for name in ("feeders.csv", "hosting_cases.csv", "expansion_options.csv"):
    (PROCESSED / name).write_text(
        (RAW / name).read_text(encoding="utf-8"),
        encoding="utf-8",
    )

print(f"Feeders: {len(feeder_rows)}")
print(f"Hosting cases: {len(hosting_results)}")
print(f"Expansion options: {len(options)}")
print(f"500 MW current at 115 kV: {article_current_115:.3f} A")
print(f"500 MW current at 345 kV: {article_current_345:.3f} A")
print(f"Article loss example: {article_loss:.3f} kW")
print(f"Outputs: {ROOT / 'outputs'}")
