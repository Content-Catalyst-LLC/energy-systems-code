#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"; PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" "$ROOT/python/generate_synthetic_data.py"
"$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
"$PYTHON_BIN" "$ROOT/python/example.py"
"$PYTHON_BIN" "$ROOT/python/run_analysis.py"
if command -v Rscript >/dev/null 2>&1; then Rscript "$ROOT/r/analyze_scenarios.R"; else echo "NOTE: R skipped"; fi
if command -v julia >/dev/null 2>&1; then julia "$ROOT/julia/energy_balance.jl" > "$ROOT/outputs/tables/julia_energy_balance.csv"; else echo "NOTE: Julia skipped"; fi
if command -v cc >/dev/null 2>&1; then
  mkdir -p "$ROOT/outputs/tmp"; cc -std=c11 -Wall -Wextra -Werror -O2 "$ROOT/c/energy_balance.c" -lm -o "$ROOT/outputs/tmp/energy_balance"
  "$ROOT/outputs/tmp/energy_balance" > "$ROOT/outputs/tables/c_energy_balance.csv"
else echo "NOTE: C skipped"; fi
printf '\nValidation complete.\n'
