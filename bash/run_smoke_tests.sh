#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

printf "\n==> Running default Python workflow\n"
python3 python/energy_balance.py
python3 tests/check_outputs.py

printf "\n==> Running optional language checks when tools are installed\n"

if command -v Rscript >/dev/null 2>&1; then
  Rscript r/energy_balance.R
else
  echo "Skipping R: Rscript not installed."
fi

if command -v julia >/dev/null 2>&1; then
  julia julia/energy_dispatch.jl
else
  echo "Skipping Julia: julia not installed."
fi

if command -v cc >/dev/null 2>&1; then
  cc c/energy_balance.c -o outputs/logs/energy_balance_c.out
  outputs/logs/energy_balance_c.out
else
  echo "Skipping C: cc compiler not installed."
fi

if command -v c++ >/dev/null 2>&1; then
  c++ -std=c++17 cpp/energy_balance.cpp -o outputs/logs/energy_balance_cpp.out
  outputs/logs/energy_balance_cpp.out
else
  echo "Skipping C++: c++ compiler not installed."
fi

if command -v rustc >/dev/null 2>&1; then
  rustc rust/energy_balance.rs -o outputs/logs/energy_balance_rust.out
  outputs/logs/energy_balance_rust.out
else
  echo "Skipping Rust: rustc not installed."
fi

if command -v go >/dev/null 2>&1; then
  go run go/energy_balance.go
else
  echo "Skipping Go: go not installed."
fi

if command -v gfortran >/dev/null 2>&1; then
  gfortran fortran/energy_balance.f90 -o outputs/logs/energy_balance_fortran.out
  outputs/logs/energy_balance_fortran.out
else
  echo "Skipping Fortran: gfortran not installed."
fi

if command -v octave >/dev/null 2>&1; then
  octave --quiet octave/simple_energy_balance.m
else
  echo "Skipping Octave: octave not installed."
fi

printf "\nSmoke tests complete.\n"
