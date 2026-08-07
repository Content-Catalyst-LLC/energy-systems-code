# Energy Flows and Sankey Diagrams

Status: computational companion implemented

This package turns an energy balance into a transparent flow-network dataset suitable for Sankey analysis. The objective is not decorative visualization; it is conservation-aware accounting in which every link has an explicit value, category, source, target, and documented boundary.

## Included analysis

- Directed energy-flow networks
- Sankey link tables with proportional width calculations
- Node inflow, outflow, and residual accounting
- Conservation checks for transformation, storage, and end-use nodes
- Aggregation of duplicate links
- Simple balance reconciliation
- Transformation and end-use loss accounting
- Storage feedback and round-trip losses
- Imports/exports-compatible flow categories
- Deterministic uncertainty analysis
- Dependency-free SVG magnitude visualization
- Python, R, Julia, C, and SQL cross-checks
- Machine-readable CSV and JSON outputs

## Run

```bash
./run_all.sh
```

The core workflow requires Python 3.10 or later and uses only the Python standard library. Optional R, Julia, C, and SQLite checks run when the corresponding executables are installed and otherwise skip cleanly.

## Interpretation requirement

A Sankey diagram is only as defensible as the energy balance beneath it. Every publication should document units, time period, spatial boundary, aggregation rules, treatment of storage, imports and exports, primary-energy conventions, and the method used to reconcile residuals.
