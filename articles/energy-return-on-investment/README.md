# Energy Return on Investment

Status: computational companion implemented

This package provides reproducible Energy Return on Investment (EROI) and net-energy analysis for the sixth article in the Sustainable Catalyst Energy Systems series.

## Included methods

- Gross and net energy accounting
- Lifecycle energy-investment decomposition
- Construction, fuel-cycle, operations, maintenance, replacement, network, storage, and retirement inputs
- EROI and net-energy fraction
- Energy-payback period
- Plant versus delivered boundary sensitivity
- Storage and network integration burdens
- Deterministic Monte Carlo uncertainty
- Multi-language cross-checks in Python, R, Julia, C, and SQL
- Machine-readable CSV and JSON outputs
- Dependency-free SVG comparison figure

## Run

```bash
./run_all.sh
```

The core workflow requires Python 3.10 or later and uses only the standard library. Optional R, Julia, C, and SQLite checks run when installed.

## Interpretation

EROI values are meaningful only when the output carrier, time horizon, lifecycle scope, boundary, storage treatment, network treatment, and allocation rules are explicit. This package intentionally keeps those components visible rather than reducing the analysis to one opaque ratio.
