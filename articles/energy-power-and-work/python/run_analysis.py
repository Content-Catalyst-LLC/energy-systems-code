#!/usr/bin/env python3
"""Run the Energy, Power, and Work computational companion."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from energy_work.core import ConversionStage, load_statistics, run_scenario
from energy_work.io import read_power_profile, scenario_rows, write_csv, write_json
from energy_work.uncertainty import propagate_efficiency_uncertainty

def args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw/hourly_power_profile.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs")
    parser.add_argument("--iterations", type=int, default=10000)
    return parser.parse_args()

def maybe_plot(observations, scenarios, output: Path) -> str:
    try: import matplotlib.pyplot as plt
    except ImportError: return "matplotlib unavailable; figures skipped"
    figure_dir = output / "figures"; figure_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot([x.timestamp for x in observations], [x.power_kw for x in observations], linewidth=1.8)
    ax.set(title="Synthetic facility power profile", xlabel="Time", ylabel="Power (kW)"); ax.grid(alpha=.25)
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(figure_dir / "power_profile.png", dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 5.5)); names = [x.scenario for x in scenarios]
    useful, losses = [x.useful_energy_kwh for x in scenarios], [x.losses_kwh for x in scenarios]
    positions = list(range(len(names))); ax.bar(positions, useful, label="Useful energy")
    ax.bar(positions, losses, bottom=useful, label="Losses")
    ax.set_xticks(positions, names, rotation=15, ha="right"); ax.set_ylabel("Energy (kWh)")
    ax.set_title("Scenario energy balance"); ax.legend(); fig.tight_layout()
    fig.savefig(figure_dir / "scenario_energy_balance.png", dpi=180); plt.close(fig)
    return "figures written"

def main() -> int:
    config = args(); observations = read_power_profile(config.input); baseline_stats = load_statistics(observations)
    stages = (ConversionStage("distribution", .975), ConversionStage("power electronics", .965),
              ConversionStage("motor", .925), ConversionStage("mechanical drive", .940))
    baseline = run_scenario("baseline", observations, 1.0, stages)
    scenarios = [baseline,
        run_scenario("efficiency retrofit", observations, .88,
            (ConversionStage("distribution", .982), ConversionStage("power electronics", .980),
             ConversionStage("premium motor", .955), ConversionStage("direct drive", .970)), baseline.energy_kwh),
        run_scenario("demand growth", observations, 1.18, stages, baseline.energy_kwh),
        run_scenario("managed load", observations, .95,
            (ConversionStage("distribution", .980), ConversionStage("power electronics", .975),
             ConversionStage("motor", .940), ConversionStage("mechanical drive", .955)), baseline.energy_kwh)]
    uncertainty = propagate_efficiency_uncertainty(baseline.energy_kwh,
        [x.efficiency for x in stages], [.004, .006, .008, .007], config.iterations)
    tables = config.output / "tables"
    write_csv(tables / "scenario_summary.csv", scenario_rows(scenarios))
    write_json(tables / "analysis_summary.json", {"input": str(config.input),
        "baseline_load_statistics": baseline_stats, "scenarios": scenario_rows(scenarios),
        "uncertainty": uncertainty.to_dict(), "method": {"integration": "trapezoidal rule",
        "uncertainty": "bounded Gaussian Monte Carlo", "seed": 20260806}})
    print(f"Baseline energy: {baseline.energy_kwh:.3f} kWh")
    print(f"Useful energy: {baseline.useful_energy_kwh:.3f} kWh; losses: {baseline.losses_kwh:.3f} kWh")
    print(maybe_plot(observations, scenarios, config.output)); print(f"Outputs: {config.output}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
