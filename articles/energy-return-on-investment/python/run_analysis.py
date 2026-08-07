#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from eroi import (
    EnergyInvestment,
    EnergyProject,
    delivered_eroi,
    energy_payback_years,
    monte_carlo_eroi,
)

RAW = ROOT / "data" / "raw" / "eroi_projects.csv"
OUT_TABLES = ROOT / "outputs" / "tables"
OUT_FIGURES = ROOT / "outputs" / "figures"
PROCESSED = ROOT / "data" / "processed"

for directory in (OUT_TABLES, OUT_FIGURES, PROCESSED):
    directory.mkdir(parents=True, exist_ok=True)


def project_from_row(row: dict[str, str]) -> EnergyProject:
    investment = EnergyInvestment(
        construction_mwh=float(row["construction_mwh"]),
        fuel_cycle_mwh=float(row["fuel_cycle_mwh"]),
        operations_mwh=float(row["operations_mwh"]),
        maintenance_mwh=float(row["maintenance_mwh"]),
        replacement_mwh=float(row["replacement_mwh"]),
        network_mwh=float(row["network_mwh"]),
        storage_mwh=float(row["storage_mwh"]),
        retirement_mwh=float(row["retirement_mwh"]),
    )
    return EnergyProject(row["name"], float(row["gross_output_mwh"]), investment)


with RAW.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

projects = [project_from_row(row) for row in rows]

summary_rows = []
for project in projects:
    summary_rows.append({
        "name": project.name,
        "gross_output_mwh": project.gross_output_mwh,
        "invested_mwh": project.investment.total_mwh(),
        "eroi": project.eroi(),
        "net_energy_mwh": project.net_energy_mwh(),
        "net_fraction": project.net_fraction(),
    })

with (OUT_TABLES / "eroi_summary.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
    writer.writeheader()
    writer.writerows(summary_rows)

baseline = next(project for project in projects if project.name == "Onshore wind")
uncertainty = monte_carlo_eroi(
    baseline,
    output_sigma=0.06,
    investment_sigma=0.08,
    draws=2000,
    seed=20260806,
)

boundary_cases = [
    {
        "boundary": "plant",
        "eroi": baseline.gross_output_mwh / (
            baseline.investment.construction_mwh
            + baseline.investment.operations_mwh
            + baseline.investment.maintenance_mwh
            + baseline.investment.replacement_mwh
            + baseline.investment.retirement_mwh
        ),
    },
    {
        "boundary": "delivered",
        "eroi": baseline.eroi(),
    },
]

with (OUT_TABLES / "boundary_sensitivity.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=["boundary", "eroi"])
    writer.writeheader()
    writer.writerows(boundary_cases)

storage_example = delivered_eroi(
    direct_output_mwh=700000,
    stored_output_input_mwh=300000,
    storage_round_trip_efficiency=0.85,
    generation_investment_mwh=70000,
    storage_investment_mwh=15000,
    network_investment_mwh=5000,
)

payback_example = energy_payback_years(
    upfront_mwh=1500,
    annual_output_mwh=600,
    annual_operating_mwh=30,
)

payload = {
    "article": "Energy Return on Investment",
    "series_position": 6,
    "project_count": len(projects),
    "baseline_project": baseline.name,
    "baseline_eroi": baseline.eroi(),
    "baseline_net_energy_mwh": baseline.net_energy_mwh(),
    "baseline_net_fraction": baseline.net_fraction(),
    "storage_delivered_eroi_example": storage_example,
    "energy_payback_years_example": payback_example,
    "uncertainty": uncertainty,
    "validation": {
        "all_eroi_positive": all(project.eroi() > 0 for project in projects),
        "all_investments_positive": all(project.investment.total_mwh() > 0 for project in projects),
        "all_outputs_positive": all(project.gross_output_mwh > 0 for project in projects),
        "uncertainty_ordered": uncertainty["p05_eroi"] <= uncertainty["p50_eroi"] <= uncertainty["p95_eroi"],
    },
}

(OUT_TABLES / "analysis_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

# Dependency-free SVG bar chart.
max_eroi = max(row["eroi"] for row in summary_rows)
svg_w = 1100
row_h = 58
svg_h = 90 + row_h * len(summary_rows)
bar_x = 310
bar_max = 650

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="24" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700">Energy Return on Investment</text>',
    '<text x="24" y="58" font-family="Arial, sans-serif" font-size="13">Synthetic teaching cases; boundary assumptions determine the reported ratio.</text>',
]

for idx, row in enumerate(summary_rows):
    y = 90 + idx * row_h
    width = bar_max * row["eroi"] / max_eroi
    label = html.escape(row["name"])
    value = html.escape(f'{row["eroi"]:.2f}:1')
    parts.append(f'<text x="24" y="{y+17}" font-family="Arial, sans-serif" font-size="13">{label}</text>')
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{width:.2f}" height="22" fill="currentColor" opacity="0.78"/>')
    parts.append(f'<text x="{bar_x + width + 8:.2f}" y="{y+16}" font-family="Arial, sans-serif" font-size="12">{value}</text>')

parts.append("</svg>")
(OUT_FIGURES / "eroi_comparison.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")

(PROCESSED / "eroi_projects.csv").write_text(RAW.read_text(encoding="utf-8"), encoding="utf-8")

print(f"Projects: {len(projects)}")
print(f"Baseline EROI: {baseline.eroi():.6f}")
print(f"Baseline net energy: {baseline.net_energy_mwh():.3f} MWh")
print(f"Storage delivered EROI example: {storage_example:.6f}")
print(f"Energy payback example: {payback_example:.6f} years")
print(f"Outputs: {ROOT / 'outputs'}")
