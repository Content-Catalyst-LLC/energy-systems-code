# Method Notes: Energy, Power, and Work

This computational companion makes the article's central relationships inspectable and reproducible. It separates instantaneous power from accumulated energy, preserves explicit units, tracks conversion losses by stage, validates conservation, and reports uncertainty rather than presenting a single efficiency estimate as exact.

## Methods

- Constant-force work: `W = F d cos(theta)`
- Translational kinetic energy: `KE = 1/2 m v^2`
- Gravitational potential energy: `PE = m g h`
- Elastic potential energy: `E = 1/2 k x^2`
- Irregular power integration: trapezoidal rule
- Conversion accounting: output from each stage becomes input to the next
- Uncertainty: bounded Gaussian Monte Carlo with a fixed reproducibility seed

The included baseline, efficiency-retrofit, demand-growth, and managed-load cases are synthetic instructional scenarios, not engineering forecasts. `data/raw/hourly_power_profile.csv` is generated deterministically and contains no operational or personal data.

Real applications require calibrated measurements, engineering constraints, lifecycle boundaries, environmental context, institutional knowledge, and qualified review.
