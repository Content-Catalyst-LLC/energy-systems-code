#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

"$PYTHON_BIN" "$ROOT/python/generate_synthetic_data.py"
"$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
"$PYTHON_BIN" "$ROOT/python/run_analysis.py"

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$ROOT/r/analyze_flows.R" "$ROOT"
else
  echo "Rscript unavailable; R cross-check skipped"
fi

if command -v julia >/dev/null 2>&1; then
  julia "$ROOT/julia/analyze_flows.jl" "$ROOT"
else
  echo "Julia unavailable; Julia cross-check skipped"
fi

if command -v cc >/dev/null 2>&1; then
  tmp_bin="${TMPDIR:-/tmp}/energy_flow_balance_$$"
  cc "$ROOT/c/flow_balance.c" -o "$tmp_bin"
  "$tmp_bin" > "$ROOT/outputs/tables/c_flow_balance.csv"
  rm -f "$tmp_bin"
else
  echo "C compiler unavailable; C cross-check skipped"
fi

if command -v sqlite3 >/dev/null 2>&1; then
  db="${TMPDIR:-/tmp}/energy_flows_$$.sqlite"
  rm -f "$db"
  sqlite3 "$db" < "$ROOT/sql/schema.sql"
  "$PYTHON_BIN" - "$db" "$ROOT/data/processed/energy_flows.csv" <<'PY'
import csv
import sqlite3
import sys
db, csv_path = sys.argv[1], sys.argv[2]
conn = sqlite3.connect(db)
with open(csv_path, newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
conn.executemany(
    "INSERT INTO energy_flows(source,target,value_mwh,category,note) VALUES (?,?,?,?,?)",
    [(r["source"], r["target"], float(r["value_mwh"]), r["category"], r["note"]) for r in rows],
)
conn.commit()
conn.close()
PY
  sqlite3 "$db" < "$ROOT/sql/example_queries.sql" > "$ROOT/outputs/tables/sql_queries.csv"
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
links = root / "outputs" / "tables" / "sankey_links.csv"
balances = root / "outputs" / "tables" / "node_balances.csv"
summary_path = root / "outputs" / "tables" / "analysis_summary.json"
svg_path = root / "outputs" / "figures" / "energy_flow_magnitudes.svg"

for path in (links, balances, summary_path, svg_path):
    assert path.exists() and path.stat().st_size > 0, path

with links.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 26
assert all(float(row["value_mwh"]) >= 0 for row in rows)
assert all(float(row["width_px"]) > 0 for row in rows if float(row["value_mwh"]) > 0)

payload = json.loads(summary_path.read_text(encoding="utf-8"))
assert payload["article"] == "Energy Flows and Sankey Diagrams"
assert payload["series_position"] == 5
assert payload["link_count"] == 26
assert all(payload["validation"].values())
assert payload["selected_balance_max_abs_residual_mwh"] <= 1e-9

with balances.open(newline="", encoding="utf-8") as handle:
    balance_rows = list(csv.DictReader(handle))
assert balance_rows
assert all(math.isfinite(float(r["residual_mwh"])) for r in balance_rows)

assert svg_path.read_text(encoding="utf-8").lstrip().startswith("<svg")
print("Machine-readable output validation passed")
PY

find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.py[co]' -delete
