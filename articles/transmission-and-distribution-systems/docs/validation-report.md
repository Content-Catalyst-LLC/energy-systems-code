# Validation report

The installer executes the complete workflow before committing or pushing.

Acceptance conditions:

- Thirteen Python unit tests pass.
- Five feeder cases are generated.
- Five hosting-capacity cases are generated.
- Five expansion options are evaluated.
- Article numerical examples are reproduced.
- Feeder losses are finite and nonnegative.
- CSV and JSON outputs parse successfully.
- The generated SVG has a valid SVG root.
- Optional R, Julia, C, and SQLite checks run when their executables are available.
