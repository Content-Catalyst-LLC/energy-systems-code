# Electricity Grids

Status: computational companion implemented

This package provides reproducible grid-analysis examples for the eighth article in the Sustainable Catalyst Energy Systems series.

## Included methods

- Supply-demand balance
- DC power-flow approximation
- Branch thermal utilization
- Approximate transmission losses
- Reserve margin
- Frequency-response example
- Storage charging and discharging
- Bus-level injections
- Congestion and overload detection
- Peak-balance uncertainty
- Python, R, Julia, C, and SQL cross-checks
- Machine-readable CSV and JSON outputs
- Dependency-free SVG branch visualization

## Run

```bash
./run_all.sh
```

The core workflow requires Python 3.10 or later and uses only the Python standard library. Optional R, Julia, C, and SQLite checks run when installed.

## Scope

The network is a synthetic teaching system. The DC approximation is useful for illustrating active-power flows and congestion but does not replace AC power-flow, transient-stability, protection, or production dispatch studies.
