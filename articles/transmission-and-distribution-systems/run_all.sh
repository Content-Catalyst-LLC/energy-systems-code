#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

"$PYTHON_BIN" "$ROOT/python/generate_network_data.py"
"$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
"$PYTHON_BIN" "$ROOT/python/run_analysis.py"

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$ROOT/r/analyze_feeders.R" "$ROOT"
else
  echo "Rscript unavailable; R cross-check skipped"
fi

if command -v julia >/dev/null 2>&1; then
  julia "$ROOT/julia/analyze_feeders.jl" "$ROOT"
else
  echo "Julia unavailable; Julia cross-check skipped"
fi

if command -v cc >/dev/null 2>&1; then
  tmp_bin="${TMPDIR:-/tmp}/three_phase_example_$$"
  cc "$ROOT/c/three_phase_example.c" -lm -o "$tmp_bin"
  "$tmp_bin" > "$ROOT/outputs/tables/c_three_phase_example.csv"
  rm -f "$tmp_bin"
else
  echo "C compiler unavailable; C cross-check skipped"
fi

if command -v sqlite3 >/dev/null 2>&1; then
  db="${TMPDIR:-/tmp}/transmission_distribution_$$.sqlite"
  rm -f "$db"
  sqlite3 "$db" < "$ROOT/sql/schema.sql"

  "$PYTHON_BIN" - "$db" "$ROOT/outputs/tables/feeder_summary.csv" <<'PY'
import csv
import sqlite3
import sys

db, csv_path = sys.argv[1], sys.argv[2]
conn = sqlite3.connect(db)

with open(csv_path, newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

conn.executemany(
    "INSERT INTO feeder_summary VALUES (?,?,?,?,?,?,?,?)",
    [
        (
            row["feeder"],
            float(row["rating_mva"]),
            float(row["peak_mva"]),
            float(row["power_factor"]),
            float(row["utilization"]),
            float(row["headroom_mva"]),
            float(row["current_a_at_13_8kv"]),
            float(row["estimated_resistive_loss_kw"]),
        )
        for row in rows
    ],
)
conn.commit()
conn.close()
PY

  sqlite3 "$db" < "$ROOT/sql/example_queries.sql" > "$ROOT/outputs/tables/sql_feeder_summary.csv"
  rm -f "$db"
else
  echo "sqlite3 unavailable; SQL cross-check skipped"
fi

"$PYTHON_BIN" - "$ROOT" <<'PY'
import csv
import json
import math
import sys
from pathlib import Path

root = Path(sys.argv[1])
feeder_csv = root / "outputs" / "tables" / "feeder_summary.csv"
hosting_csv = root / "outputs" / "tables" / "hosting_capacity_cases.csv"
ranking_csv = root / "outputs" / "tables" / "expansion_ranking.csv"
summary_json = root / "outputs" / "tables" / "analysis_summary.json"
svg = root / "outputs" / "figures" / "feeder_utilization.svg"

for path in (feeder_csv, hosting_csv, ranking_csv, summary_json, svg):
    assert path.exists() and path.stat().st_size > 0, path

with feeder_csv.open(newline="", encoding="utf-8") as handle:
    feeders = list(csv.DictReader(handle))
assert len(feeders) == 5
assert all(float(row["rating_mva"]) > 0 for row in feeders)
assert all(float(row["estimated_resistive_loss_kw"]) >= 0 for row in feeders)
assert all(math.isfinite(float(row["current_a_at_13_8kv"])) for row in feeders)

with hosting_csv.open(newline="", encoding="utf-8") as handle:
    hosting = list(csv.DictReader(handle))
assert len(hosting) == 5

with ranking_csv.open(newline="", encoding="utf-8") as handle:
    ranking = list(csv.DictReader(handle))
assert len(ranking) == 5

payload = json.loads(summary_json.read_text(encoding="utf-8"))
assert payload["article"] == "Transmission and Distribution Systems"
assert payload["series_position"] == 10
assert all(payload["validation"].values())

assert svg.read_text(encoding="utf-8").lstrip().startswith("<svg")
print("Machine-readable output validation passed")
PY

find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.py[co]' -delete
