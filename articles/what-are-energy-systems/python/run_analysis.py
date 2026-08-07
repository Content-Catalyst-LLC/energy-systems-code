#!/usr/bin/env python3
"""Run system-boundary, scenario, uncertainty, and publication-output analyses."""

from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from energy_systems_foundation.io import read_system, write_csv, write_json
from energy_systems_foundation.model import run_scenario
from energy_systems_foundation.scenarios import transform_system
from energy_systems_foundation.uncertainty import monte_carlo_system_efficiency

RAW = ROOT / "data" / "raw"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
RENEWABLES = {"solar_resource", "wind_resource"}


def write_svg(path: Path, rows: list[dict[str, float | str]]) -> None:
    width, height = 1000, 520
    margin_left, margin_top, chart_width, chart_height = 110, 80, 820, 330
    metric = "useful_service_mwh_equivalent"
    max_value = max(float(row[metric]) for row in rows) * 1.12
    bar_width = chart_width / max(1, len(rows)) * 0.58
    gap = chart_width / len(rows)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="500" y="38" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700">Useful energy service by scenario</text>',
        f'<line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="black"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="black"/>',
    ]
    for tick in range(6):
        value = max_value * tick / 5
        y = margin_top + chart_height - chart_height * tick / 5
        parts.append(f'<line x1="{margin_left - 6}" y1="{y:.1f}" x2="{margin_left}" y2="{y:.1f}" stroke="black"/>')
        parts.append(f'<text x="{margin_left - 12}" y="{y + 5:.1f}" text-anchor="end" font-family="Arial" font-size="13">{value:,.0f}</text>')
    for index, row in enumerate(rows):
        value = float(row[metric])
        x = margin_left + gap * index + (gap - bar_width) / 2
        bar_height = chart_height * value / max_value
        y = margin_top + chart_height - bar_height
        label = html.escape(str(row["scenario"]))
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="#222"/>')
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="5" fill="#ff0000"/>')
        parts.append(f'<text x="{x + bar_width / 2:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-family="Arial" font-size="13" font-weight="700">{value:,.0f}</text>')
        parts.append(f'<text x="{x + bar_width / 2:.1f}" y="{margin_top + chart_height + 26}" text-anchor="middle" font-family="Arial" font-size="13">{label}</text>')
    parts.append('<text x="24" y="260" transform="rotate(-90 24 260)" text-anchor="middle" font-family="Arial" font-size="15">MWh-equivalent service</text>')
    parts.append('</svg>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> None:
    system = read_system(RAW / "energy_nodes.csv", RAW / "energy_links.csv")

    baseline = run_scenario("Baseline", system, RENEWABLES)
    efficiency = run_scenario(
        "Efficiency",
        transform_system(system, efficiency_multiplier=1.035, demand_multiplier=1.0),
        RENEWABLES,
    )
    electrification = run_scenario(
        "Electrification",
        transform_system(
            system,
            efficiency_multiplier=1.02,
            demand_multiplier=1.08,
            input_overrides={"gas_to_plant": 3400, "solar_to_plant": 5100, "wind_to_plant": 4300},
        ),
        RENEWABLES,
    )
    resilience = run_scenario(
        "Grid stress",
        transform_system(
            system,
            availability_overrides={
                "gas_to_plant": 0.58,
                "grid_to_buildings": 0.82,
                "grid_to_industry": 0.86,
                "grid_to_transport": 0.90,
            },
        ),
        RENEWABLES,
    )

    results = [baseline, efficiency, electrification, resilience]
    rows = [result.to_dict() for result in results]
    uncertainty = monte_carlo_system_efficiency(system, RENEWABLES)

    write_csv(TABLES / "scenario_summary.csv", rows)
    write_csv(TABLES / "node_flow_balance.csv", system.flow_balance())
    write_json(
        TABLES / "analysis_summary.json",
        {
            "article": "What Are Energy Systems?",
            "boundary": "resource inputs through useful energy services",
            "scenarios": rows,
            "uncertainty": uncertainty,
            "interpretation": {
                "baseline_primary_to_service_efficiency": baseline.overall_primary_to_service_efficiency,
                "baseline_renewable_input_share": baseline.renewable_input_share,
                "grid_stress_critical_service_share": resilience.critical_service_served_share,
            },
        },
    )
    write_svg(FIGURES / "useful_service_by_scenario.svg", rows)

    print(f"Baseline primary input: {baseline.primary_input_mwh:.3f} MWh")
    print(f"Baseline useful service: {baseline.useful_service_mwh_equivalent:.3f} MWh-equivalent")
    print(f"Baseline efficiency: {baseline.overall_primary_to_service_efficiency:.6f}")
    print(f"Baseline emissions: {baseline.emissions_t_co2e:.3f} t CO2e")
    print(f"Outputs: {ROOT / 'outputs'}")


if __name__ == "__main__":
    main()
