#!/usr/bin/env python3
"""Validate the Sankey network and create publication-ready outputs."""

from __future__ import annotations

import csv
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from energy_flows import Flow, FlowNetwork, normalize_widths, monte_carlo_network

RAW = ROOT / "data" / "raw" / "energy_flows.csv"
OUT_TABLES = ROOT / "outputs" / "tables"
OUT_FIGURES = ROOT / "outputs" / "figures"
PROCESSED = ROOT / "data" / "processed"
for directory in (OUT_TABLES, OUT_FIGURES, PROCESSED):
    directory.mkdir(parents=True, exist_ok=True)


def read_flows(path: Path) -> list[Flow]:
    result = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            result.append(
                Flow(
                    row["source"],
                    row["target"],
                    float(row["value_mwh"]),
                    row["category"],
                    row["note"],
                )
            )
    return result


flows = read_flows(RAW)
network = FlowNetwork(flows)

# The teaching network intentionally includes storage feedback. Validate selected
# accounting nodes rather than requiring an acyclic topology.
balanced_nodes = ["Thermal generation", "Electric generation", "Storage charge", "Buildings", "Industry", "Transport"]
for node in balanced_nodes:
    residual = network.balance(node).residual_mwh
    if abs(residual) > 1e-9:
        raise SystemExit(f"Node {node} failed conservation: {residual}")

widths = normalize_widths(flows, max_width=26.0, min_visible_width=1.0)

link_path = OUT_TABLES / "sankey_links.csv"
with link_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["source", "target", "value_mwh", "category", "width_px", "note"])
    for flow in flows:
        writer.writerow([
            flow.source,
            flow.target,
            f"{flow.value_mwh:.6f}",
            flow.category,
            f"{widths[(flow.source, flow.target)]:.6f}",
            flow.note,
        ])

balance_path = OUT_TABLES / "node_balances.csv"
with balance_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["node", "inflow_mwh", "outflow_mwh", "residual_mwh", "relative_residual"])
    for balance in network.balances():
        writer.writerow([
            balance.node,
            f"{balance.inflow_mwh:.6f}",
            f"{balance.outflow_mwh:.6f}",
            f"{balance.residual_mwh:.12f}",
            f"{balance.relative_residual:.12f}",
        ])

uncertainty = monte_carlo_network(flows, relative_sigma=0.025, draws=1000, seed=20260806)

summary = {
    "article": "Energy Flows and Sankey Diagrams",
    "series_position": 5,
    "link_count": len(flows),
    "node_count": len(network.nodes),
    "total_link_flow_mwh": network.total_flow(),
    "selected_balanced_nodes": balanced_nodes,
    "selected_balance_max_abs_residual_mwh": max(
        abs(network.balance(node).residual_mwh) for node in balanced_nodes
    ),
    "uncertainty": uncertainty,
    "validation": {
        "nonnegative_flows": all(flow.value_mwh >= 0 for flow in flows),
        "selected_nodes_conserve": all(abs(network.balance(node).residual_mwh) <= 1e-9 for node in balanced_nodes),
        "widths_positive_for_positive_flows": all(
            widths[(flow.source, flow.target)] > 0 for flow in flows if flow.value_mwh > 0
        ),
    },
}
(OUT_TABLES / "analysis_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

# Dependency-free SVG: left-aligned flow bars proportional to value.
max_value = max(flow.value_mwh for flow in flows)
svg_w = 1200
row_h = 34
svg_h = 80 + row_h * len(flows)
bar_x = 430
bar_max = 650
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="24" y="36" font-family="Arial, sans-serif" font-size="22" font-weight="700">Energy-flow link magnitudes</text>',
    '<text x="24" y="58" font-family="Arial, sans-serif" font-size="13">Width is proportional to annual energy flow in the synthetic teaching dataset.</text>',
]
for idx, flow in enumerate(flows):
    y = 82 + idx * row_h
    width = 0 if max_value == 0 else bar_max * flow.value_mwh / max_value
    label = html.escape(f"{flow.source} → {flow.target}")
    value = html.escape(f"{flow.value_mwh:,.0f} MWh")
    parts.append(f'<text x="24" y="{y+15}" font-family="Arial, sans-serif" font-size="12">{label}</text>')
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{width:.2f}" height="16" fill="currentColor" opacity="0.78"/>')
    parts.append(f'<text x="{bar_x + width + 8:.2f}" y="{y+13}" font-family="Arial, sans-serif" font-size="11">{value}</text>')
parts.append("</svg>")
(OUT_FIGURES / "energy_flow_magnitudes.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")

# Processed copy used by SQL/R/Julia/C cross-checks.
processed = PROCESSED / "energy_flows.csv"
processed.write_text(RAW.read_text(encoding="utf-8"), encoding="utf-8")

print(f"Links: {len(flows)}")
print(f"Nodes: {len(network.nodes)}")
print(f"Max selected-node residual: {summary['selected_balance_max_abs_residual_mwh']:.12f} MWh")
print(f"Outputs: {ROOT / 'outputs'}")
