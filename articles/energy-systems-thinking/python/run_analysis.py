#!/usr/bin/env python3
from __future__ import annotations
import csv, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from systems_thinking import Scenario, simulate, rebound, loop_type, monte_carlo

TABLES = ROOT / "outputs" / "tables"
FIGS = ROOT / "outputs" / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

scenarios = [
    Scenario("Coordinated build"),
    Scenario("Transmission constrained", transmission_limit_gw=5.5),
    Scenario("Slow permitting", permitting_factor=.55),
    Scenario("Manufacturing constrained", manufacturing_limit_gw=5.0),
    Scenario("Rapid learning", learning_rate=.28, manufacturing_limit_gw=18, transmission_limit_gw=18, demand_pull=1.15),
]

summary=[]; trajectories=[]
for s in scenarios:
    h=simulate(s)
    summary.append({"scenario":s.name,"initial_capacity_gw":h[0][1],"final_capacity_gw":h[-1][1],"capacity_change_gw":h[-1][1]-h[0][1],"final_cost_index":h[-1][3]})
    for year,cap,cum,cost,build,retire in h:
        trajectories.append({"scenario":s.name,"year":year,"capacity_gw":cap,"cumulative_build_gw":cum,"cost_index":cost,"build_gw":build,"retirement_gw":retire})

for name, rows in [("scenario_summary.csv",summary),("scenario_trajectories.csv",trajectories)]:
    with (TABLES/name).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

rb = rebound(20,14,15.5)
mc = monte_carlo(scenarios[0], draws=1000, seed=20260806)
payload={
    "article":"Energy Systems Thinking",
    "series_position":7,
    "scenario_count":len(scenarios),
    "reinforcing_loop":loop_type([1,-1,-1]),
    "balancing_loop":loop_type([1,-1,1]),
    "rebound_fraction":rb["fraction"],
    "uncertainty":mc,
    "validation":{
        "five_scenarios":len(scenarios)==5,
        "reinforcing":loop_type([1,-1,-1])=="reinforcing",
        "balancing":loop_type([1,-1,1])=="balancing",
        "rebound_25_percent":abs(rb["fraction"]-.25)<1e-12,
        "uncertainty_ordered":mc["p05"]<=mc["p50"]<=mc["p95"],
    }
}
(TABLES/"analysis_summary.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

maxcap=max(r["final_capacity_gw"] for r in summary)
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="460" viewBox="0 0 1100 460">','<rect width="100%" height="100%" fill="white"/>','<text x="24" y="34" font-family="Arial" font-size="22" font-weight="700">Energy Systems Thinking — Scenario Outcomes</text>']
for i,r in enumerate(summary):
    y=80+i*70; width=650*r["final_capacity_gw"]/maxcap
    parts.append(f'<text x="24" y="{y+17}" font-family="Arial" font-size="13">{r["scenario"]}</text>')
    parts.append(f'<rect x="330" y="{y}" width="{width:.2f}" height="24" fill="currentColor" opacity="0.78"/>')
    parts.append(f'<text x="{338+width:.2f}" y="{y+17}" font-family="Arial" font-size="12">{r["final_capacity_gw"]:.1f} GW</text>')
parts.append('</svg>')
(FIGS/"scenario_capacity_comparison.svg").write_text("\n".join(parts)+"\n",encoding="utf-8")

print(f"Scenarios: {len(scenarios)}")
print(f"Rebound fraction: {rb['fraction']:.3f}")
print(f"Mean final capacity: {mc['mean_final_capacity_gw']:.3f} GW")
