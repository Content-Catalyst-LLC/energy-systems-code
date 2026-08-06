# Validation Plan

Acceptance requires:

- successful Python syntax compilation;
- unit tests for equations, unit conversion, time integration, efficiency bounds, conservation, and deterministic uncertainty;
- end-to-end generation of synthetic data and scenario outputs;
- parseable nonempty CSV and JSON outputs;
- conservation residual below `1e-9 kWh` for every scenario;
- optional R, Julia, and C workflows when runtimes are installed;
- C compilation with `-Wall -Wextra -Werror`.
