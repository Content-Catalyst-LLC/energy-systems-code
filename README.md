# Energy Systems Code

Companion repository for the Energy Systems knowledge series.

This repository supports reproducible scientific, engineering, and policy-oriented examples for energy systems, including grid dispatch, renewable variability, storage, capacity factors, emissions accounting, demand response, microgrid resilience, energy affordability, industrial decarbonization, hydrogen systems, and climate-risk stress scenarios.

The repository is designed to be useful for engineers, scientists, policy analysts, infrastructure planners, students, technical writers, and public-interest researchers. It includes dependency-light teaching examples, synthetic datasets, technical notes, notebooks, and optional advanced workflows.

## Scope

The repository supports articles on:

- Energy, power, work, and thermodynamics
- Electricity grids, transmission, distribution, microgrids, and reliability
- Renewable energy systems and variability
- Energy storage and dispatch
- Fossil-fuel transition, electrification, hydrogen, nuclear, and industrial decarbonization
- Energy markets, public utilities, policy, security, and geopolitics
- Energy justice, energy poverty, affordability, and resilience
- Lifecycle assessment, emissions accounting, and critical materials
- Digital energy infrastructure, AI, and future energy systems

## Language Coverage

Included languages and tools:

- Python
- R
- Julia
- C
- C++
- Rust
- Go
- Fortran
- SQL
- MATLAB/Octave
- Modelica
- Bash
- Jupyter notebooks
- LaTeX documentation

## Quick Start

Run the lightweight smoke tests:

```bash
bash bash/run_smoke_tests.sh
```

Run all default Python workflows:

```bash
python3 python/run_all.py
```

Optional advanced Python setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-advanced.txt
python3 python/advanced_energy_dashboard.py
```

## Repository Design

Default scripts avoid fragile dependency chains. Advanced scripts are optional and clearly separated. Synthetic data is included for reproducibility, teaching, validation, and article support.

## Scientific and Engineering Use

This repository provides educational and exploratory workflows. Engineering planning, grid operations, procurement decisions, safety-critical design, and public policy should rely on validated datasets, appropriate standards, professional review, and domain-specific modeling.
