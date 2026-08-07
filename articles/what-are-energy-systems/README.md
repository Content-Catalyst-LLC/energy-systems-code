# What Are Energy Systems?

Status: computational companion implemented

This folder supports the first article in the Energy Systems series. It models energy systems as linked technical, economic, environmental, and social-service structures rather than as isolated technologies.

## Included workflows

- Directed energy-system graph with explicit node and link types
- Resource-to-service system-boundary accounting
- Conversion, network, storage, and end-use loss accounting
- Primary input, final energy, and useful-service metrics
- Emissions and variable-cost accounting
- Renewable-input and critical-service indicators
- Baseline, efficiency, electrification, and grid-stress scenarios
- Seeded Monte Carlo uncertainty analysis
- Reproducible CSV, JSON, SVG, SQL, R, Julia, and C outputs

## Run

```bash
bash run_all.sh
```

The default Python workflow uses only the standard library and requires Python 3.10 or newer.

## Main outputs

- `outputs/tables/scenario_summary.csv`
- `outputs/tables/node_flow_balance.csv`
- `outputs/tables/analysis_summary.json`
- `outputs/figures/useful_service_by_scenario.svg`

## Responsible use

The included data are synthetic and the model is educational. It does not replace validated engineering, operational, market, lifecycle, environmental-justice, or policy analysis.
