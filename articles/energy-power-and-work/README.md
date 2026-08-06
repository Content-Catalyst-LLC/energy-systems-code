# Energy, Power, and Work

**Status:** computational companion implemented

Reproducible code, deterministic synthetic data, tests, and publication-support outputs for the Energy Systems article **Energy, Power, and Work**.

## Capabilities

- SI-based energy and power unit conversion;
- mechanical work and mechanical-energy equations;
- trapezoidal integration of irregular power observations;
- energy, peak-power, average-power, and load-factor metrics;
- multistage conversion chains with explicit loss accounting;
- baseline, retrofit, demand-growth, and managed-load scenarios;
- deterministic Monte Carlo efficiency uncertainty;
- Python tests and GitHub Actions validation;
- companion R, Julia, C, and SQL examples.

## Run

```bash
bash articles/energy-power-and-work/run_all.sh
```

Core Python requires Python 3.10+. Install `requirements.txt` only when PNG figures are desired.

## Principal outputs

- `outputs/tables/scenario_summary.csv`
- `outputs/tables/analysis_summary.json`
- `outputs/figures/power_profile.png` when Matplotlib is installed
- `outputs/figures/scenario_energy_balance.png` when Matplotlib is installed

All data and scenarios are synthetic educational assets, not engineering designs, forecasts, or investment recommendations.
