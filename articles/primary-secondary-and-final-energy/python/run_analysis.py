#!/usr/bin/env python3
"""Run the reproducible Primary, Secondary, and Final Energy analysis."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from energy_accounting.core import (  # noqa: E402
    AccountingChain,
    aggregate_results,
    chain_accounting,
    direct_equivalent_primary,
    energy_balance,
    substitution_primary,
)
from energy_accounting.io import write_csv, write_json  # noqa: E402
from energy_accounting.uncertainty import monte_carlo_chain  # noqa: E402

RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
for directory in (PROCESSED, TABLES, FIGURES):
    directory.mkdir(parents=True, exist_ok=True)


def load_pathways() -> list[AccountingChain]:
    with (RAW / "energy_pathways.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [
        AccountingChain(
            name=row["pathway"],
            primary_energy_mwh=float(row["primary_energy_mwh"]),
            conversion_efficiency=float(row["conversion_efficiency"]),
            delivery_efficiency=float(row["delivery_efficiency"]),
            end_use_efficiency=float(row["end_use_efficiency"]),
            service_factor=float(row["service_factor"]),
            energy_sector_own_use_fraction=float(row["energy_sector_own_use_fraction"]),
            non_energy_use_fraction=float(row["non_energy_use_fraction"]),
        )
        for row in rows
    ]


def compact_row(result):
    return {
        "pathway": result.name,
        "primary_energy_mwh": f"{result.primary_energy_mwh:.6f}",
        "secondary_energy_mwh": f"{result.secondary_energy_mwh:.6f}",
        "final_energy_mwh": f"{result.final_energy_mwh:.6f}",
        "useful_energy_mwh": f"{result.useful_energy_mwh:.6f}",
        "service_energy_equivalent_mwh": f"{result.service_energy_equivalent_mwh:.6f}",
        "conversion_loss_mwh": f"{result.conversion_loss_mwh:.6f}",
        "delivery_loss_mwh": f"{result.delivery_loss_mwh:.6f}",
        "end_use_loss_mwh": f"{result.end_use_loss_mwh:.6f}",
        "primary_to_final_efficiency": f"{result.primary_to_final_efficiency:.9f}",
        "primary_to_useful_efficiency": f"{result.primary_to_useful_efficiency:.9f}",
        "primary_to_service_efficiency": f"{result.primary_to_service_efficiency:.9f}",
        "residual_mwh": f"{result.residual_mwh:.12f}",
    }


def make_svg(results, path: Path) -> None:
    width, height = 980, 470
    left, top, chart_h = 95, 55, 320
    max_primary = max(result.primary_energy_mwh for result in results)
    colors = ["#4b5563", "#64748b", "#7c8a97", "#8f9aa5", "#a3acb5"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#faf9f6"/>',
        '<text x="40" y="30" font-family="Arial, sans-serif" font-size="19" fill="#20242a">Energy accounting by pathway</text>',
    ]
    bar_group = 150
    bar_w = 22
    for index, result in enumerate(results):
        x0 = left + index * bar_group
        values = [
            ("P", result.primary_energy_mwh),
            ("F", result.final_energy_mwh),
            ("U", result.useful_energy_mwh),
            ("S", result.service_energy_equivalent_mwh),
        ]
        for j, (label, value) in enumerate(values):
            h = chart_h * value / max_primary
            x = x0 + j * (bar_w + 6)
            y = top + chart_h - h
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" fill="{colors[index]}" opacity="{1.0 - j * 0.16:.2f}"/>')
            parts.append(f'<text x="{x + bar_w/2:.1f}" y="{top + chart_h + 18}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#30363d">{label}</text>')
        short = result.name.replace("_", " ")
        parts.append(f'<text x="{x0 + 48:.1f}" y="{top + chart_h + 43}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#30363d">{short[:20]}</text>')
    for tick in range(0, 5):
        value = max_primary * tick / 4
        y = top + chart_h - chart_h * tick / 4
        parts.append(f'<line x1="{left-8}" y1="{y:.1f}" x2="{width-40}" y2="{y:.1f}" stroke="#d8dadd" stroke-width="1"/>')
        parts.append(f'<text x="{left-15}" y="{y+4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="10" fill="#5a6068">{value:.0f}</text>')
    parts.append('<text x="40" y="445" font-family="Arial, sans-serif" font-size="11" fill="#5a6068">P = primary · F = final · U = useful · S = service-equivalent energy</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> None:
    chains = load_pathways()
    results = [chain_accounting(chain) for chain in chains]
    aggregate = dict(aggregate_results(results))
    write_csv(TABLES / "pathway_summary.csv", [compact_row(result) for result in results])

    with (RAW / "primary_energy_methods.csv").open(newline="", encoding="utf-8") as handle:
        method_input = list(csv.DictReader(handle))
    method_rows = []
    for row in method_input:
        electricity = float(row["electricity_mwh"])
        reference_efficiency = float(row["reference_efficiency"])
        direct = direct_equivalent_primary(electricity)
        substitution = substitution_primary(electricity, reference_efficiency)
        method_rows.append({
            "technology": row["technology"],
            "electricity_mwh": f"{electricity:.6f}",
            "direct_equivalent_primary_mwh": f"{direct:.6f}",
            "substitution_primary_mwh": f"{substitution:.6f}",
            "reference_efficiency": f"{reference_efficiency:.6f}",
            "method_ratio": f"{substitution / direct:.6f}",
        })
    write_csv(TABLES / "methodology_comparison.csv", method_rows)

    transformation_and_network = sum(
        row.conversion_loss_mwh + row.delivery_loss_mwh for row in results
    )
    own_use = sum(row.energy_sector_own_use_mwh for row in results)
    non_energy = sum(row.non_energy_use_mwh for row in results)
    final = sum(row.final_energy_mwh for row in results)
    balance = energy_balance(
        aggregate["primary_energy_mwh"],
        transformation_and_network,
        own_use,
        non_energy,
        final,
    )

    baseline_chain = next(chain for chain in chains if chain.name == "coal_to_electric_motor")
    uncertainty = monte_carlo_chain(baseline_chain, samples=2500, seed=20260806)
    payload = {
        "article": "Primary, Secondary, and Final Energy",
        "series_position": 4,
        "boundary": "resource input through service-equivalent output",
        "aggregate": aggregate,
        "balance": balance.as_dict(),
        "methodology_note": "Direct-equivalent and substitution accounting are reported separately and must not be mixed silently.",
        "uncertainty": uncertainty,
        "validation": {
            "pathway_residuals_within_tolerance": all(abs(row.residual_mwh) <= 1e-9 for row in results),
            "aggregate_residual_within_tolerance": abs(aggregate["residual_mwh"]) <= 1e-9,
            "balance_residual_within_tolerance": abs(balance.residual_mwh) <= 1e-9,
        },
    }
    write_json(TABLES / "analysis_summary.json", payload)
    make_svg(results, FIGURES / "energy_accounting_pathways.svg")

    print(f"Aggregate primary energy: {aggregate['primary_energy_mwh']:.3f} MWh")
    print(f"Aggregate final energy: {aggregate['final_energy_mwh']:.3f} MWh")
    print(f"Aggregate useful energy: {aggregate['useful_energy_mwh']:.3f} MWh")
    print(f"Aggregate service equivalent: {aggregate['service_energy_equivalent_mwh']:.3f} MWh")
    print(f"Primary-to-useful efficiency: {aggregate['primary_to_useful_efficiency']:.6f}")
    print(f"Outputs: {ROOT / 'outputs'}")


if __name__ == "__main__":
    main()
