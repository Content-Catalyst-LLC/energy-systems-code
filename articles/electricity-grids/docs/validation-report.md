# Validation report

The installer executes the complete article workflow before committing or pushing.

Acceptance conditions:

- Thirteen Python unit tests pass.
- Four buses and five synthetic branches are generated.
- Branch flows are finite.
- Branch limits are positive.
- Approximate branch losses are nonnegative.
- Reserve, frequency, and storage examples compute successfully.
- Monte Carlo uncertainty is deterministic for a fixed seed.
- CSV, JSON, and SVG outputs parse successfully.
- Optional R, Julia, C, and SQLite checks run when their executables are available.
