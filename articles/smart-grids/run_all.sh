#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

"$PYTHON_BIN" "$ROOT/python/generate_smart_grid_data.py"
"$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
"$PYTHON_BIN" "$ROOT/python/run_analysis.py"

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$ROOT/r/analyze_interval_demand.R" "$ROOT"
else
  echo "Rscript unavailable; R cross-check skipped"
fi

if command -v julia >/dev/null 2>&1; then
  julia "$ROOT/julia/analyze_smart_grid.jl" "$ROOT"
else
  echo "Julia unavailable; Julia cross-check skipped"
fi

if command -v cc >/dev/null 2>&1; then
  tmp_bin="${TMPDIR:-/tmp}/smart_grid_example_$$"
  cc "$ROOT/c/smart_grid_example.c" -o "$tmp_bin"
  "$tmp_bin" > "$ROOT/outputs/tables/c_smart_grid_example.csv"
  rm -f "$tmp_bin"
else
  echo "C compiler unavailable; C cross-check skipped"
fi

if command -v sqlite3 >/dev/null 2>&1; then
  db="${TMPDIR:-/tmp}/smart_grids_$$.sqlite"
  rm -f "$db"
  sqlite3 "$db" < "$ROOT/sql/schema.sql"

  "$PYTHON_BIN" - "$db" "$ROOT/data/raw/interval_demand.csv" <<'PY'
import csv
import sqlite3
import sys

db, csv_path = sys.argv[1], sys.argv[2]
conn = sqlite3.connect(db)

with open(csv_path, newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

conn.executemany(
    "INSERT INTO interval_demand VALUES (?,?)",
    [
        (int(row["hour"]), float(row["demand_mw"]))
        for row in rows
    ],
)
conn.commit()
conn.close()
PY

  sqlite3 "$db" < "$ROOT/sql/example_queries.sql" > "$ROOT/outputs/tables/sql_peak_intervals.csv"
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
interval_csv = root / "outputs" / "tables" / "interval_demand_summary.csv"
der_csv = root / "outputs" / "tables" / "der_summary.csv"
automation_csv = root / "outputs" / "tables" / "automation_summary.csv"
summary_json = root / "outputs" / "tables" / "analysis_summary.json"
svg = root / "outputs" / "figures" / "automation_restoration_benefit.svg"

for path in (interval_csv, der_csv, automation_csv, summary_json, svg):
    assert path.exists() and path.stat().st_size > 0, path

with automation_csv.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 5
assert all(float(row["customer_hours_avoided"]) >= 0 for row in rows)
assert all(0 <= float(row["restoration_fraction"]) <= 1 for row in rows)

payload = json.loads(summary_json.read_text(encoding="utf-8"))
assert payload["article"] == "Smart Grids"
assert payload["series_position"] == 11
assert payload["interval_count"] == 24
assert payload["der_resource_count"] == 5
assert payload["automation_scenario_count"] == 5
assert all(payload["validation"].values())
assert math.isfinite(payload["der_dispatchable_mw"])

assert svg.read_text(encoding="utf-8").lstrip().startswith("<svg")
print("Machine-readable output validation passed")
PY

find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.py[co]' -delete
