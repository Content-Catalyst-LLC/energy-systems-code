#!/usr/bin/env python3
from eroi import EnergyInvestment, EnergyProject

project = EnergyProject(
    "Example project",
    2400.0,
    EnergyInvestment(
        construction_mwh=95.0,
        operations_mwh=24.0,
        maintenance_mwh=28.0,
        replacement_mwh=18.0,
        retirement_mwh=10.0,
    ),
)

print(f"EROI={project.eroi():.2f}")
print(f"net_energy_mwh={project.net_energy_mwh():.2f}")
