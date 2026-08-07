#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

"$PYTHON_BIN" "$ROOT/python/generate_synthetic_data.py"
"$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
"$PYTHON_BIN" "$ROOT/python/run_analysis.py"

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$ROOT/r/analyze_eroi.R" "$ROOT"
else
  echo "Rscript unavailable; R cross-check skipped"
fi

if command -v julia >/dev/null 2>&1; then
  julia "$ROOT/julia/analyze_eroi.jl" "$ROOT"
else
  echo "Julia unavailable; Julia cross-check skipped"
fi

if command -v cc >/dev/null 2>&1; then
  tmp_bin="${TMPDIR:-/tmp}/eroi_example_$$"
  cc "$ROOT/c/eroi_example.c" -o "$tmp_bin"
  "$tmp_bin" > "$ROOT/outputs/tables/c_eroi_example.csv"
  rm -f "$tmp_bin"
else
  echo "C compiler unavailable; C cross-check skipped"
fi

if command -v sqlite3 >/dev/null 2>&1; then
  db="${TMPDIR:-/tmp}/eroi_$$.sqlite"
  rm -f "$db"
  sqlite3 "$db" < "$ROOT/sql/schema.sql"

  "$PYTHON_BIN" - "$db" "$ROOT/data/processed/eroi_projects.csv" <<'PY'
import csv
import sqlite3
import sys

db, csv_path = sys.argv[1], sys.argv[2]
conn = sqlite3.connect(db)

with open(csv_path, newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

cols = [
    "name",
    "gross_output_mwh",
    "construction_mwh",
    "fuel_cycle_mwh",
    "operations_mwh",
    "maintenance_mwh",
    "replacement_mwh",
    "network_mwh",
    "storage_mwh",
    "retirement_mwh",
]

conn.executemany(
    "INSERT INTO eroi_projects VALUES (?,?,?,?,?,?,?,?,?,?)",
    [
        tuple([row["name"]] + [float(row[c]) for c in cols[1:]])
        for row in rows
    ],
)
conn.commit()
conn.close()
PY

  sqlite3 "$db" < "$ROOT/sql/example_queries.sql" > "$ROOT/outputs/tables/sql_eroi_summary.csv"
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
summary_csv = root / "outputs" / "tables" / "eroi_summary.csv"
boundary_csv = root / "outputs" / "tables" / "boundary_sensitivity.csv"
summary_json = root / "outputs" / "tables" / "analysis_summary.json"
svg = root / "outputs" / "figures" / "eroi_comparison.svg"

for path in (summary_csv, boundary_csv, summary_json, svg):
    assert path.exists() and path.stat().st_size > 0, path

with summary_csv.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 7
assert all(float(row["eroi"]) > 0 for row in rows)
assert all(math.isfinite(float(row["net_energy_mwh"])) for row in rows)

with boundary_csv.open(newline="", encoding="utf-8") as handle:
    boundaries = list(csv.DictReader(handle))
assert {row["boundary"] for row in boundaries} == {"plant", "delivered"}

payload = json.loads(summary_json.read_text(encoding="utf-8"))
assert payload["article"] == "Energy Return on Investment"
assert payload["series_position"] == 6
assert payload["project_count"] == 7
assert all(payload["validation"].values())
assert payload["uncertainty"]["p05_eroi"] <= payload["uncertainty"]["p50_eroi"] <= payload["uncertainty"]["p95_eroi"]

assert svg.read_text(encoding="utf-8").lstrip().startswith("<svg")
print("Machine-readable output validation passed")
PY

find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.py[co]' -delete
