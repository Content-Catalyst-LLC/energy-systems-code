#!/usr/bin/env python3
"""Run reproducible thermodynamic scenario and uncertainty analysis."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from thermodynamics import (  # noqa: E402
    heat_engine,
    heat_pump_cop_heating,
    monte_carlo_heat_engine,
    multistage_efficiency,
    thermal_storage_cycle,
)
from thermodynamics.io import read_processes, write_csv, write_json  # noqa: E402


def _svg_bar_chart(rows: list[dict[str, float | str]], output: Path) -> None:
    width, height = 960, 520
    margin_left, margin_bottom, margin_top = 90, 90, 50
    chart_width = width - margin_left - 40
    chart_height = height - margin_bottom - margin_top
    values = [float(row["actual_efficiency"]) for row in rows]
    max_value = max(0.7, max(values) * 1.15)
    bar_width = chart_width / max(1, len(rows)) * 0.62
    gap = chart_width / max(1, len(rows))

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="480" y="28" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">Thermodynamic Scenario Efficiency</text>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height-margin_bottom}" stroke="#111"/>',
        f'<line x1="{margin_left}" y1="{height-margin_bottom}" x2="{width-40}" y2="{height-margin_bottom}" stroke="#111"/>',
    ]
    for tick in range(0, 8):
        value = max_value * tick / 7
        y = margin_top + chart_height * (1 - tick / 7)
        elements.append(f'<line x1="{margin_left-5}" y1="{y:.2f}" x2="{width-40}" y2="{y:.2f}" stroke="#ddd"/>')
        elements.append(f'<text x="{margin_left-10}" y="{y+4:.2f}" text-anchor="end" font-family="Arial" font-size="12">{value:.2f}</text>')
    for index, row in enumerate(rows):
        value = float(row["actual_efficiency"])
        x = margin_left + gap * index + (gap - bar_width) / 2
        bar_height = chart_height * value / max_value
        y = height - margin_bottom - bar_height
        label = str(row["scenario"]).replace("_", " ")
        elements.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" fill="#222"/>')
        elements.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="5" fill="#ff0000"/>')
        elements.append(f'<text x="{x+bar_width/2:.2f}" y="{y-8:.2f}" text-anchor="middle" font-family="Arial" font-size="12">{value:.3f}</text>')
        elements.append(f'<text x="{x+bar_width/2:.2f}" y="{height-margin_bottom+18}" transform="rotate(28 {x+bar_width/2:.2f} {height-margin_bottom+18})" text-anchor="start" font-family="Arial" font-size="11">{label}</text>')
    elements.append('</svg>')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(elements) + "\n", encoding="utf-8")


def main() -> None:
    input_path = ROOT / "data" / "raw" / "thermal_processes.csv"
    process_rows = read_processes(input_path)
    summaries: list[dict[str, float | str]] = []

    for row in process_rows:
        hot = float(row["hot_temperature_k"])
        cold = float(row["cold_temperature_k"])
        heat_input = float(row["heat_input_mj"])
        fraction = float(row["second_law_fraction"])
        ambient = float(row["ambient_temperature_k"])
        hp_fraction = float(row["heat_pump_fraction"])
        engine = heat_engine(heat_input, hot, cold, fraction, ambient)
        storage = thermal_storage_cycle(
            heat_input,
            float(row["charge_efficiency"]),
            float(row["discharge_efficiency"]),
            float(row["retention_fraction"]),
        )
        cop_heating = heat_pump_cop_heating(hot, cold, hp_fraction)
        summaries.append(
            {
                "scenario": row["scenario"],
                "hot_temperature_k": hot,
                "cold_temperature_k": cold,
                "heat_input_mj": heat_input,
                "carnot_efficiency": engine.carnot_efficiency,
                "actual_efficiency": engine.actual_efficiency,
                "work_output_mj": engine.work_output,
                "heat_rejected_mj": engine.heat_rejected,
                "entropy_generation_mj_per_k": engine.entropy_generation,
                "exergy_input_mj": engine.exergy_input,
                "exergy_efficiency": engine.exergy_efficiency,
                "heat_pump_cop_heating": cop_heating,
                "storage_round_trip_efficiency": storage.round_trip_efficiency,
                "three_stage_delivery_efficiency": multistage_efficiency((0.94, 0.97, 0.90)),
                "first_law_residual_mj": engine.first_law_residual,
                "storage_residual_mj": storage.conservation_residual,
            }
        )

    baseline = summaries[0]
    uncertainty = monte_carlo_heat_engine(
        heat_input=float(baseline["heat_input_mj"]),
        hot_temperature_k=float(baseline["hot_temperature_k"]),
        cold_temperature_k=float(baseline["cold_temperature_k"]),
        second_law_fraction=0.58,
    )

    for row in summaries:
        numeric_values = [value for value in row.values() if isinstance(value, float)]
        if not all(math.isfinite(value) for value in numeric_values):
            raise RuntimeError(f"Non-finite output in {row['scenario']}")
        if abs(float(row["first_law_residual_mj"])) > 1e-9:
            raise RuntimeError(f"First-law residual in {row['scenario']}")
        if abs(float(row["storage_residual_mj"])) > 1e-9:
            raise RuntimeError(f"Storage residual in {row['scenario']}")
        if float(row["actual_efficiency"]) > float(row["carnot_efficiency"]) + 1e-12:
            raise RuntimeError(f"Actual efficiency exceeds Carnot limit in {row['scenario']}")
        if float(row["entropy_generation_mj_per_k"]) < -1e-12:
            raise RuntimeError(f"Negative entropy generation in {row['scenario']}")

    tables = ROOT / "outputs" / "tables"
    figures = ROOT / "outputs" / "figures"
    write_csv(tables / "scenario_summary.csv", summaries)
    write_json(
        tables / "analysis_summary.json",
        {
            "article": "Energy and Thermodynamics",
            "units": {"energy": "MJ", "temperature": "K", "entropy": "MJ/K"},
            "baseline": baseline,
            "uncertainty": uncertainty,
            "validation": {
                "scenario_count": len(summaries),
                "maximum_first_law_residual_mj": max(abs(float(row["first_law_residual_mj"])) for row in summaries),
                "minimum_entropy_generation_mj_per_k": min(float(row["entropy_generation_mj_per_k"]) for row in summaries),
                "all_actual_efficiencies_below_carnot": True,
            },
        },
    )
    _svg_bar_chart(summaries, figures / "scenario_efficiency.svg")

    print(f"Baseline Carnot efficiency: {float(baseline['carnot_efficiency']):.6f}")
    print(f"Baseline actual efficiency: {float(baseline['actual_efficiency']):.6f}")
    print(f"Baseline work output: {float(baseline['work_output_mj']):.3f} MJ")
    print(f"Baseline entropy generation: {float(baseline['entropy_generation_mj_per_k']):.6f} MJ/K")
    print(f"Outputs: {ROOT / 'outputs'}")


if __name__ == "__main__":
    main()
