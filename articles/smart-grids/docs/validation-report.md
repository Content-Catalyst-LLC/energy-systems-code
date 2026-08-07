# Validation report

The installer executes the complete workflow before committing or pushing.

Acceptance conditions:

- Thirteen Python unit tests pass.
- Twenty-four interval-demand observations are generated.
- Five DER resources are evaluated.
- Five automation scenarios are evaluated.
- Article charging, demand-response, Volt/VAR, load-factor, and FLISR examples are reproduced.
- Flexible-peak uncertainty is deterministic for a fixed seed.
- CSV and JSON outputs parse successfully.
- The generated SVG has a valid SVG root.
- Optional R, Julia, C, and SQLite checks run when their executables are available.
