"""Minimal example for the Energy and Thermodynamics article."""

from thermodynamics import heat_engine

result = heat_engine(
    heat_input=1000.0,
    hot_temperature_k=823.15,
    cold_temperature_k=303.15,
    second_law_fraction=0.58,
)

print(f"Carnot limit: {result.carnot_efficiency:.3f}")
print(f"Actual efficiency: {result.actual_efficiency:.3f}")
print(f"Work output: {result.work_output:.1f} MJ")
print(f"Entropy generation: {result.entropy_generation:.4f} MJ/K")
