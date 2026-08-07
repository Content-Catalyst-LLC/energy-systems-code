# Validation report

The installer executes the complete workflow before committing or pushing.

Acceptance conditions:

- Twelve Python unit tests pass.
- Twenty-six deterministic energy-flow links are generated.
- Selected internal nodes conserve energy to within `1e-9 MWh`.
- All positive energy flows receive positive proportional widths.
- The analysis summary reports all validation flags as true.
- The uncertainty workflow is deterministic for a fixed seed.
- CSV, JSON, and SVG publication outputs parse successfully.
- Optional R, Julia, C, and SQLite workflows run when their executables are available.
