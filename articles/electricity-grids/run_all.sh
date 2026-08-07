#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

"$PYTHON_BIN" "$ROOT/python/generate_grid_data.py"
"$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
"$PYTHON_BIN" "$ROOT/python/run_analysis.py"

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$ROOT/r/analyze_grid.R" "$ROOT"
else
  echo "Rscript unavailable; R cross-check skipped"
fi

if command -v julia >/dev/null 2>&1; then
  julia "$ROOT/julia/analyze_grid.jl" "$ROOT"
else
  echo "Julia unavailable; Julia cross-check skipped"
fi

if command -v cc >/dev/null 2>&1; then
  tmp_bin="${TMPDIR:-/tmp}/grid_balance_example_$$"
  cc "$ROOT/c/grid_balance_example.c" -o "$tmp_bin"
  "$tmp_bin" > "$ROOT/outputs/tables/c_grid_balance_example.csv"
  rm -f "$tmp_bin"
else
  echo "C compiler unavailable; C cross-check skipped"
fi

if command -v sqlite3 >/dev/null 2>&1; then
  db="${TMPDIR:-/tmp}/electricity_grids_$$.sqlite"
  rm -f "$db"
  sqlite3 "$db" < "$ROOT/sql/schema.sql"

  "$PYTHON_BIN" - "$db" "$ROOT/outputs/tables/branch_flows.csv" <<'PY'
import csv
import sqlite3
import sys

db, csv_path = sys.argv[1], sys.argv[2]
conn = sqlite3.connect(db)

with open(csv_path, newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

conn.executemany(
    "INSERT INTO branch_flows VALUES (?,?,?,?,?,?,?)",
    [
        (
            row["branch"],
            row["from_bus"],
            row["to_bus"],
            float(row["flow_mw"]),
            float(row["thermal_limit_mw"]),
            float(row["utilization"]),
            float(row["estimated_loss_mw"]),
        )
        for row in rows
    ],
)
conn.commit()
conn.close()
PY

  sqlite3 "$db" < "$ROOT/sql/example_queries.sql" > "$ROOT/outputs/tables/sql_branch_summary.csv"
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
flows_csv = root / "outputs" / "tables" / "branch_flows.csv"
balance_csv = root / "outputs" / "tables" / "bus_balance.csv"
summary_json = root / "outputs" / "tables" / "analysis_summary.json"
svg = root / "outputs" / "figures" / "branch_utilization.svg"

for path in (flows_csv, balance_csv, summary_json, svg):
    assert path.exists() and path.stat().st_size > 0, path

with flows_csv.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 5
assert all(float(row["thermal_limit_mw"]) > 0 for row in rows)
assert all(float(row["estimated_loss_mw"]) >= 0 for row in rows)
assert all(math.isfinite(float(row["flow_mw"])) for row in rows)

with balance_csv.open(newline="", encoding="utf-8") as handle:
    buses = list(csv.DictReader(handle))
assert len(buses) == 4

payload = json.loads(summary_json.read_text(encoding="utf-8"))
assert payload["article"] == "Electricity Grids"
assert payload["series_position"] == 8
assert payload["bus_count"] == 4
assert payload["branch_count"] == 5
assert all(payload["validation"].values())

assert svg.read_text(encoding="utf-8").lstrip().startswith("<svg")
print("Machine-readable output validation passed")
PY

find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.py[co]' -delete
