#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p outputs/tables outputs/figures

echo "Running Python workflows..."
python3 python/run_all.py

if command -v Rscript >/dev/null 2>&1; then
  echo "Running R workflows..."
  Rscript r/energy_summary.R
  Rscript r/energy_burden_summary.R
  Rscript r/lcoe_summary.R
else
  echo "Skipping R workflows: Rscript not found."
fi

if command -v julia >/dev/null 2>&1; then
  echo "Running Julia workflows..."
  julia julia/storage_state_model.jl
  julia julia/emissions_intensity.jl
else
  echo "Skipping Julia workflows: julia not found."
fi

if command -v gcc >/dev/null 2>&1; then
  echo "Compiling C example..."
  gcc c/energy_balance.c -o outputs/tables/energy_balance_c.out
  ./outputs/tables/energy_balance_c.out > outputs/tables/c_energy_balance_output.csv
else
  echo "Skipping C example: gcc not found."
fi

if command -v g++ >/dev/null 2>&1; then
  echo "Compiling C++ example..."
  g++ cpp/dispatch_merit_order.cpp -o outputs/tables/dispatch_merit_order_cpp.out
  ./outputs/tables/dispatch_merit_order_cpp.out > outputs/tables/cpp_dispatch_merit_order_output.csv
else
  echo "Skipping C++ example: g++ not found."
fi

if command -v gfortran >/dev/null 2>&1; then
  echo "Compiling Fortran example..."
  gfortran fortran/storage_balance.f90 -o outputs/tables/storage_balance_fortran.out
  ./outputs/tables/storage_balance_fortran.out > outputs/tables/fortran_storage_balance_output.txt
else
  echo "Skipping Fortran example: gfortran not found."
fi

if command -v go >/dev/null 2>&1; then
  echo "Running Go example..."
  go run go/energy_burden.go > outputs/tables/go_energy_burden.csv
else
  echo "Skipping Go example: go not found."
fi

if command -v rustc >/dev/null 2>&1; then
  echo "Compiling Rust example..."
  rustc rust/capacity_factor.rs -o outputs/tables/capacity_factor_rust.out
  ./outputs/tables/capacity_factor_rust.out > outputs/tables/rust_capacity_factor.csv
else
  echo "Skipping Rust example: rustc not found."
fi

if command -v octave >/dev/null 2>&1; then
  echo "Running Octave/MATLAB-compatible example..."
  octave --quiet matlab/demand_response_demo.m > outputs/tables/octave_demand_response_output.csv
else
  echo "Skipping Octave example: octave not found."
fi

echo "Smoke tests completed."
