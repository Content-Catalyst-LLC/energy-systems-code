#!/usr/bin/env python3
"""Small executable examples for the article's central equations."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from energy_work import ConversionStage, gravitational_potential_energy_j, kinetic_energy_j, mechanical_work_j, run_conversion_chain
print(f"Mechanical work: {mechanical_work_j(420, 8, 25):.2f} J")
print(f"Kinetic energy: {kinetic_energy_j(1200, 22):,.2f} J")
print(f"Potential energy: {gravitational_potential_energy_j(85, 12):,.2f} J")
balance = run_conversion_chain(1000, [ConversionStage("inverter", .97), ConversionStage("motor", .94), ConversionStage("drive", .92)])
print(f"Useful output: {balance.useful_output_kwh:.2f} kWh; losses: {balance.losses_kwh:.2f} kWh")
