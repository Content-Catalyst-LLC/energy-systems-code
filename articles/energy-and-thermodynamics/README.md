# Energy and Thermodynamics

Status: computational companion implemented

This article package provides reproducible, dependency-light workflows for the thermodynamic foundations of energy systems. It distinguishes energy conservation from conversion quality and makes system boundaries, reservoir temperatures, entropy generation, exergy, and conversion losses explicit.

## Included analysis

- First-law energy balances with a documented heat-in/work-out sign convention
- Carnot efficiency and temperature-bound conversion limits
- Actual heat-engine performance expressed as a fraction of the reversible limit
- Entropy generation and irreversibility checks
- Exergy of heat relative to an ambient reference state
- Heating coefficient of performance for heat pumps
- Multistage conversion efficiency
- Thermal-storage round-trip accounting
- Deterministic Monte Carlo uncertainty analysis
- Cross-language Python, R, Julia, C, and SQL examples
- Machine-readable CSV and JSON results plus an SVG publication figure

## Run

```bash
./run_all.sh
```

The core Python workflow requires Python 3.10 or later and uses only the standard library. R, Julia, C, and SQLite workflows run automatically when those tools are installed and otherwise skip cleanly.

## Important interpretation

The models are transparent teaching and diagnostic tools, not equipment-design software. Temperature levels, reservoir assumptions, property simplifications, reference states, and system boundaries must be documented before results are used for engineering or policy decisions.
