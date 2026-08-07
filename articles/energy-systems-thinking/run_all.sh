#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

"$PYTHON_BIN" -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
"$PYTHON_BIN" "$ROOT/python/run_analysis.py"

if command -v Rscript >/dev/null 2>&1; then Rscript "$ROOT/r/analyze_scenarios.R" "$ROOT"; else echo "Rscript unavailable; skipped"; fi
if command -v julia >/dev/null 2>&1; then julia "$ROOT/julia/analyze_scenarios.jl" "$ROOT"; else echo "Julia unavailable; skipped"; fi
if command -v cc >/dev/null 2>&1; then cc "$ROOT/c/stock_flow_example.c" -o "${TMPDIR:-/tmp}/stock_flow_$$" && "${TMPDIR:-/tmp}/stock_flow_$$" > "$ROOT/outputs/tables/c_stock_flow_example.csv" && rm -f "${TMPDIR:-/tmp}/stock_flow_$$"; else echo "C compiler unavailable; skipped"; fi

"$PYTHON_BIN" - "$ROOT" <<'PY'
import csv,json,sys
from pathlib import Path
root=Path(sys.argv[1])
summary=root/'outputs/tables/scenario_summary.csv'
traj=root/'outputs/tables/scenario_trajectories.csv'
payload=root/'outputs/tables/analysis_summary.json'
svg=root/'outputs/figures/scenario_capacity_comparison.svg'
for p in (summary,traj,payload,svg): assert p.exists() and p.stat().st_size>0,p
with summary.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
assert len(rows)==5
with traj.open(newline='',encoding='utf-8') as f: tr=list(csv.DictReader(f))
assert len(tr)==105
j=json.loads(payload.read_text(encoding='utf-8'))
assert j['article']=='Energy Systems Thinking' and j['series_position']==7 and all(j['validation'].values())
assert svg.read_text(encoding='utf-8').lstrip().startswith('<svg')
print('Machine-readable output validation passed')
PY

find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.py[co]' -delete
