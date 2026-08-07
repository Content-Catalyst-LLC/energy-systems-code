# Transmission and Distribution Systems

Status: computational companion implemented

This package provides reproducible transmission and distribution examples for the tenth article in the Sustainable Catalyst Energy Systems series.

## Included methods

- Three-phase current
- Resistive line losses
- Feeder utilization and headroom
- Transformer loading
- Simplified voltage-drop screening
- Congestion cost
- Hosting-capacity cases
- Expansion-option ranking
- Python, R, Julia, C, and SQL cross-checks
- Machine-readable CSV and JSON outputs
- Dependency-free SVG feeder visualization

## Run

```bash
./run_all.sh
```

The core workflow requires Python 3.10 or later and uses only the Python standard library. Optional R, Julia, C, and SQLite checks run when installed.

## Scope

All network data are synthetic teaching examples. Screening calculations do not replace AC power flow, protection, transient stability, detailed distribution hosting-capacity studies, or utility engineering review.
