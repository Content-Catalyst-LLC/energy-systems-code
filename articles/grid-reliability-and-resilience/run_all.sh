#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

"$PYTHON_BIN" "$ROOT/python/generate_reliability_data.py"
"$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
"$PYTHON_BIN" "$ROOT/python/run_analysis.py"

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$ROOT/r/analyze_reliability.R" "$ROOT"
else
  echo "Rscript unavailable; R cross-check skipped"
fi

if command -v julia >/dev/null 2>&1; then
  julia "$ROOT/julia/analyze_reliability.jl" "$ROOT"
else
  echo "Julia unavailable; Julia cross-check skipped"
fi

if command -v cc >/dev/null 2>&1; then
  tmp_bin="${TMPDIR:-/tmp}/reliability_example_$$"
  cc "$ROOT/c/reliability_example.c" -o "$tmp_bin"
  "$tmp_bin" > "$ROOT/outputs/tables/c_reliability_example.csv"
  rm -f "$tmp_bin"
else
  echo "C compiler unavailable; C cross-check skipped"
fi

if command -v sqlite3 >/dev/null 2>&1; then
  db="${TMPDIR:-/tmp}/grid_reliability_$$.sqlite"
  rm -f "$db"
  sqlite3 "$db" < "$ROOT/sql/schema.sql"

  "$PYTHON_BIN" - "$db" "$ROOT/outputs/tables/resilience_scenarios.csv" <<'PY'
import csv
import sqlite3
import sys

db, csv_path = sys.argv[1], sys.argv[2]
conn = sqlite3.connect(db)

with open(csv_path, newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

conn.executemany(
    "INSERT INTO resilience_scenarios VALUES (?,?,?,?,?)",
    [
        (
            row["scenario"],
            float(row["annual_probability"]),
            float(row["consequence_million_usd"]),
            float(row["service_retained_fraction"]),
            float(row["annualized_risk_million_usd"]),
        )
        for row in rows
    ],
)
conn.commit()
conn.close()
PY

  sqlite3 "$db" < "$ROOT/sql/example_queries.sql" > "$ROOT/outputs/tables/sql_resilience_summary.csv"
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
reliability_csv = root / "outputs" / "tables" / "reliability_summary.csv"
resilience_csv = root / "outputs" / "tables" / "resilience_scenarios.csv"
summary_json = root / "outputs" / "tables" / "analysis_summary.json"
svg = root / "outputs" / "figures" / "resilience_risk_comparison.svg"

for path in (reliability_csv, resilience_csv, summary_json, svg):
    assert path.exists() and path.stat().st_size > 0, path

with resilience_csv.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 5
assert all(float(row["annualized_risk_million_usd"]) >= 0 for row in rows)
assert all(0 <= float(row["service_retained_fraction"]) <= 1 for row in rows)

payload = json.loads(summary_json.read_text(encoding="utf-8"))
assert payload["article"] == "Grid Reliability and Resilience"
assert payload["series_position"] == 9
assert payload["scenario_count"] == 5
assert all(payload["validation"].values())
assert math.isfinite(payload["restoration_service_hours"])

assert svg.read_text(encoding="utf-8").lstrip().startswith("<svg")
print("Machine-readable output validation passed")
PY

find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.py[co]' -delete
