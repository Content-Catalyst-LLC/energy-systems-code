# Validation report

The installer executes the complete validation workflow before committing or pushing.

Acceptance conditions:

- Twelve Python unit tests pass.
- Five deterministic energy pathways are generated.
- Four accounting-method comparison rows are generated.
- Every pathway residual is no greater than `1e-9 MWh` in magnitude.
- The aggregate and economy-style balance residuals remain within tolerance.
- Energy levels remain ordered as service ≤ useful ≤ final ≤ primary.
- Monte Carlo results repeat exactly for a fixed seed.
- Machine-readable CSV and JSON outputs parse successfully.
- The publication SVG is generated without a plotting dependency.
- Optional R, Julia, C, and SQLite workflows run when their executables are available.
