# Energy Systems Code

Companion repository for the Energy Systems knowledge series. The repository is designed for reproducible energy systems learning, scenario analysis, grid and storage modeling, emissions accounting, synthetic data workflows, and multi-language computational examples.

## Purpose

This repository supports practical and transparent analysis of energy systems as technical, institutional, ecological, economic, and social systems. It includes examples for energy balance, power and energy conversion, storage dispatch, renewable variability, grid reliability, emissions intensity, lifecycle thinking, scenario comparison, and policy-facing interpretation.

## Languages and tools

The repository includes examples in:

- Python
- R
- Julia
- C
- C++
- Rust
- Go
- Fortran
- SQL
- Bash
- Modelica
- GNU Octave / MATLAB-compatible scripts
- Jupyter notebooks

The default workflows are intentionally dependency-light. Optional advanced workflows can use pandas, matplotlib, numpy, and related tools when available.

## Repository structure

```text
energy-systems-code/
├── articles/              # Per-article scaffolds and local examples
├── bash/                  # Run scripts and smoke tests
├── c/                     # C examples
├── cpp/                   # C++ examples
├── data/                  # Raw, processed, and synthetic data
├── docs/                  # Method notes, data dictionary, validation plan
├── fortran/               # Fortran examples
├── go/                    # Go examples
├── julia/                 # Julia examples
├── modelica/              # Modelica system models
├── notebooks/             # Jupyter notebooks
├── octave/                # GNU Octave / MATLAB-compatible scripts
├── outputs/               # Generated figures, tables, and logs
├── python/                # Python workflows
├── r/                     # R workflows
├── rust/                  # Rust examples
├── sql/                   # SQL schema and example queries
└── tests/                 # Lightweight validation checks
```

## Run the default smoke test

```bash
bash bash/run_smoke_tests.sh
```

The smoke test runs the Python default workflow and then attempts to run or compile examples in other languages when the required interpreters or compilers are installed. Missing optional languages are skipped with a clear message.

## Optional advanced Python setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-advanced.txt
python python/advanced_energy_plots.py
```

## Data notes

All included data are synthetic demonstration data unless explicitly documented otherwise. They are designed for reproducible modeling, teaching, scenario exploration, and methods demonstration.

## Responsible use

These workflows are for energy systems learning, public-interest analysis, reproducible modeling, and scenario exploration. They should not be used as authoritative operational tools for real-time grid dispatch, safety-critical engineering decisions, financial trading, regulatory compliance, or emergency management without professional validation and domain-specific review.
