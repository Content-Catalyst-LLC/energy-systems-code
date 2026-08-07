#!/usr/bin/env bash
set -euo pipefail

ARTICLE_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="$ARTICLE_DIR/python${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1

"$PYTHON_BIN" "$ARTICLE_DIR/python/generate_synthetic_data.py"
"$PYTHON_BIN" -m unittest discover -s "$ARTICLE_DIR/tests" -p 'test_*.py' -v
"$PYTHON_BIN" "$ARTICLE_DIR/python/run_analysis.py"

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$ARTICLE_DIR/r/analyze_cycles.R" "$ARTICLE_DIR"
else
  echo "Rscript unavailable; R workflow skipped"
fi

if command -v julia >/dev/null 2>&1; then
  julia "$ARTICLE_DIR/julia/thermodynamic_cycles.jl" "$ARTICLE_DIR"
else
  echo "Julia unavailable; Julia workflow skipped"
fi

if command -v cc >/dev/null 2>&1; then
  tmp_binary="$(mktemp -t thermodynamics-cycle.XXXXXX)"
  cc -std=c11 -Wall -Wextra -Werror "$ARTICLE_DIR/c/carnot_cycle.c" -o "$tmp_binary"
  "$tmp_binary" "$ARTICLE_DIR/outputs/tables/c_cycle_metrics.csv"
  rm -f "$tmp_binary"
else
  echo "C compiler unavailable; C workflow skipped"
fi

if command -v sqlite3 >/dev/null 2>&1; then
  db="$(mktemp -t thermodynamics.XXXXXX).sqlite"
  sqlite3 "$db" < "$ARTICLE_DIR/sql/schema.sql"
  {
    echo '.mode csv'
    echo ".import --skip 1 '$ARTICLE_DIR/data/raw/thermal_processes.csv' thermodynamic_scenarios"
    cat "$ARTICLE_DIR/sql/example_queries.sql"
  } | sqlite3 "$db" > "$ARTICLE_DIR/outputs/tables/sql_query_results.csv"
  rm -f "$db"
else
  echo "sqlite3 unavailable; SQL execution skipped"
fi

"$PYTHON_BIN" - "$ARTICLE_DIR" <<'PY'
import csv
import json
import math
import sys
from pathlib import Path

article = Path(sys.argv[1])
summary_path = article / "outputs" / "tables" / "scenario_summary.csv"
json_path = article / "outputs" / "tables" / "analysis_summary.json"
svg_path = article / "outputs" / "figures" / "scenario_efficiency.svg"

with summary_path.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 5, len(rows)
for row in rows:
    carnot = float(row["carnot_efficiency"])
    actual = float(row["actual_efficiency"])
    entropy = float(row["entropy_generation_mj_per_k"])
    residual = float(row["first_law_residual_mj"])
    assert 0 <= actual <= carnot < 1
    assert entropy >= -1e-12
    assert abs(residual) <= 1e-9
    assert all(math.isfinite(float(row[key])) for key in row if key != "scenario")

payload = json.loads(json_path.read_text(encoding="utf-8"))
assert payload["article"] == "Energy and Thermodynamics"
assert payload["validation"]["all_actual_efficiencies_below_carnot"] is True
assert svg_path.read_text(encoding="utf-8").lstrip().startswith("<svg")
print("Machine-readable output validation passed")
PY

find "$ARTICLE_DIR" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ARTICLE_DIR" -type f -name '*.py[co]' -delete
