# Validation report

The installer executes the complete workflow before committing or pushing.

Acceptance conditions:

- Thirteen Python unit tests pass.
- Five outage events and five resilience scenarios are generated.
- SAIDI, SAIFI, CAIDI, reserve-margin, frequency-response, and EUE calculations succeed.
- Restoration-curve integration succeeds.
- Monte Carlo resource-adequacy uncertainty is deterministic.
- CSV, JSON, and SVG outputs parse successfully.
- Optional R, Julia, C, and SQLite checks run when their executables are available.
