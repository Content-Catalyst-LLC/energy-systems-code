#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

"$PYTHON_BIN" "$ROOT/python/generate_synthetic_data.py"
PYTHONPATH="$ROOT/python" "$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
PYTHONPATH="$ROOT/python" "$PYTHON_BIN" "$ROOT/python/run_analysis.py"

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$ROOT/r/analyze_energy_levels.R"
else
  printf 'Rscript unavailable; R workflow skipped\n'
fi

if command -v julia >/dev/null 2>&1; then
  julia --startup-file=no "$ROOT/julia/energy_levels.jl"
else
  printf 'Julia unavailable; Julia workflow skipped\n'
fi

if command -v cc >/dev/null 2>&1; then
  tmp_bin="$(mktemp -t energy-chain.XXXXXX)"
  cc -std=c11 -Wall -Wextra -Werror "$ROOT/c/energy_chain.c" -o "$tmp_bin"
  "$tmp_bin" > "$ROOT/outputs/tables/c_energy_chain.csv"
  rm -f "$tmp_bin"
else
  printf 'C compiler unavailable; C workflow skipped\n'
fi

if command -v sqlite3 >/dev/null 2>&1; then
  db="$(mktemp -t energy-accounting.XXXXXX.db)"
  sqlite3 "$db" < "$ROOT/sql/schema.sql"
  "$PYTHON_BIN" - "$ROOT/data/raw/energy_pathways.csv" "$db" <<'PY'
import csv
import sqlite3
import sys

csv_path, db_path = sys.argv[1:]
with open(csv_path, newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
with sqlite3.connect(db_path) as connection:
    connection.executemany(
        """INSERT INTO energy_pathway VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                row["pathway"],
                float(row["primary_energy_mwh"]),
                float(row["conversion_efficiency"]),
                float(row["delivery_efficiency"]),
                float(row["end_use_efficiency"]),
                float(row["service_factor"]),
                float(row["energy_sector_own_use_fraction"]),
                float(row["non_energy_use_fraction"]),
            )
            for row in rows
        ],
    )
PY
  sqlite3 "$db" < "$ROOT/sql/example_queries.sql" > "$ROOT/outputs/tables/sql_energy_levels.csv"
  rm -f "$db"
else
  printf 'sqlite3 unavailable; SQL workflow skipped\n'
fi

"$PYTHON_BIN" - "$ROOT" <<'PY'
import csv
import json
import math
import sys
from pathlib import Path

root = Path(sys.argv[1])
summary_path = root / "outputs" / "tables" / "pathway_summary.csv"
method_path = root / "outputs" / "tables" / "methodology_comparison.csv"
json_path = root / "outputs" / "tables" / "analysis_summary.json"
svg_path = root / "outputs" / "figures" / "energy_accounting_pathways.svg"

for path in (summary_path, method_path, json_path, svg_path):
    assert path.exists() and path.stat().st_size > 0, path

with summary_path.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 5, len(rows)
for row in rows:
    primary = float(row["primary_energy_mwh"])
    final = float(row["final_energy_mwh"])
    useful = float(row["useful_energy_mwh"])
    service = float(row["service_energy_equivalent_mwh"])
    residual = float(row["residual_mwh"])
    assert 0 <= service <= useful <= final <= primary
    assert abs(residual) <= 1e-9
    assert all(math.isfinite(float(row[key])) for key in row if key != "pathway")

with method_path.open(newline="", encoding="utf-8") as handle:
    method_rows = list(csv.DictReader(handle))
assert len(method_rows) == 4
for row in method_rows:
    assert float(row["substitution_primary_mwh"]) >= float(row["direct_equivalent_primary_mwh"])

payload = json.loads(json_path.read_text(encoding="utf-8"))
assert payload["article"] == "Primary, Secondary, and Final Energy"
assert payload["series_position"] == 4
assert all(payload["validation"].values())
assert svg_path.read_text(encoding="utf-8").lstrip().startswith("<svg")
print("Machine-readable output validation passed")
PY

find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.py[co]' -delete
