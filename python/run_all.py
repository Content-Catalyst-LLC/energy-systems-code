#!/usr/bin/env python3
"""Run default Python workflows."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    ROOT / "python" / "storage_dispatch.py",
    ROOT / "python" / "capacity_factor.py",
    ROOT / "python" / "emissions_accounting.py",
    ROOT / "python" / "lcoe_model.py",
    ROOT / "python" / "demand_response.py",
    ROOT / "python" / "energy_burden.py",
    ROOT / "python" / "microgrid_resilience.py",
    ROOT / "python" / "hydrogen_model.py",
    ROOT / "python" / "climate_risk_stress.py",
]


def main() -> None:
    for script in SCRIPTS:
        print(f"\nRunning {script.relative_to(ROOT)}")
        subprocess.run([sys.executable, str(script)], check=True)


if __name__ == "__main__":
    main()
