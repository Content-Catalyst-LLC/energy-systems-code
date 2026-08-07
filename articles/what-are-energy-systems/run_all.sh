#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONDONTWRITEBYTECODE=1
PYTHON_BIN="${PYTHON_BIN:-python3}"

"$PYTHON_BIN" "$ROOT/python/generate_synthetic_data.py"
PYTHONPATH="$ROOT/python" "$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -v
PYTHONPATH="$ROOT/python" "$PYTHON_BIN" "$ROOT/python/run_analysis.py"

if command -v sqlite3 >/dev/null 2>&1; then
  db="$(mktemp -t what-are-energy-systems.XXXXXX).sqlite"
  trap 'rm -f "$db"' EXIT
  sqlite3 "$db" < "$ROOT/sql/schema.sql"
  sqlite3 "$db" <<SQL
.mode csv
.import --skip 1 "$ROOT/data/raw/energy_nodes.csv" energy_nodes
.import --skip 1 "$ROOT/data/raw/energy_links.csv" energy_links
SQL
  sqlite3 -header -csv "$db" < "$ROOT/sql/example_queries.sql" > "$ROOT/outputs/tables/sql_query_results.csv"
fi

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$ROOT/r/analyze_system.R"
fi

if command -v julia >/dev/null 2>&1; then
  julia "$ROOT/julia/system_balance.jl"
fi

if command -v cc >/dev/null 2>&1; then
  binary="$(mktemp -t what-are-energy-systems-c.XXXXXX)"
  cc -std=c11 -Wall -Wextra -Werror "$ROOT/c/system_balance.c" -o "$binary"
  "$binary" > "$ROOT/outputs/tables/c_system_balance.csv"
  rm -f "$binary"
fi

"$PYTHON_BIN" "$ROOT/python/validate_outputs.py"
