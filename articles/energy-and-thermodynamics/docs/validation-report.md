# Validation report

The installer executes the complete validation workflow before committing or pushing.

Acceptance conditions:

- Python unit tests pass.
- Five deterministic scenarios are generated.
- First-law and storage residuals are no greater than `1e-9 MJ` in magnitude.
- No actual heat-engine efficiency exceeds the corresponding Carnot efficiency.
- No scenario produces negative entropy generation.
- Monte Carlo results repeat exactly for a fixed seed.
- Machine-readable CSV and JSON outputs parse successfully.
- The publication SVG is generated without a plotting dependency.
- Optional R, Julia, C, and SQLite workflows run when their executables are available.
