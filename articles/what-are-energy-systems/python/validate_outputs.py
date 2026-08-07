#!/usr/bin/env python3
"""Validate generated machine-readable and publication outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"

required = [
    TABLES / "scenario_summary.csv",
    TABLES / "node_flow_balance.csv",
    TABLES / "analysis_summary.json",
    FIGURES / "useful_service_by_scenario.svg",
]
for path in required:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"Missing or empty output: {path}")

with (TABLES / "scenario_summary.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
if [row["scenario"] for row in rows] != ["Baseline", "Efficiency", "Electrification", "Grid stress"]:
    raise SystemExit("Unexpected scenario order")

for row in rows:
    efficiency = float(row["overall_primary_to_service_efficiency"])
    renewable_share = float(row["renewable_input_share"])
    critical_share = float(row["critical_service_served_share"])
    if not 0.0 <= efficiency <= 1.0:
        raise SystemExit("Efficiency outside [0, 1]")
    if not 0.0 <= renewable_share <= 1.0:
        raise SystemExit("Renewable share outside [0, 1]")
    if not 0.0 <= critical_share <= 1.0:
        raise SystemExit("Critical service share outside [0, 1]")

payload = json.loads((TABLES / "analysis_summary.json").read_text(encoding="utf-8"))
if payload["article"] != "What Are Energy Systems?":
    raise SystemExit("Incorrect article identifier")
if payload["uncertainty"]["iterations"] < 100:
    raise SystemExit("Uncertainty ensemble is too small")

svg = (FIGURES / "useful_service_by_scenario.svg").read_text(encoding="utf-8")
if "<svg" not in svg or "Useful energy service by scenario" not in svg:
    raise SystemExit("Invalid SVG output")

print("Machine-readable and publication output validation passed")
