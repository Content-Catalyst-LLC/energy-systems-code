"""Seeded Monte Carlo uncertainty for system efficiency and emissions."""

from __future__ import annotations

import random
from dataclasses import replace
from statistics import mean

from .model import EnergySystem, build_system, run_scenario


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def monte_carlo_system_efficiency(
    system: EnergySystem,
    renewable_resource_ids: set[str],
    iterations: int = 2000,
    seed: int = 20260806,
    efficiency_sigma: float = 0.02,
    availability_sigma: float = 0.025,
) -> dict[str, float | int]:
    if iterations < 100:
        raise ValueError("Use at least 100 iterations")
    rng = random.Random(seed)
    efficiencies: list[float] = []
    emissions: list[float] = []

    for index in range(iterations):
        links = []
        for link in system.links:
            sampled_efficiency = min(
                1.0,
                max(0.0, rng.gauss(link.efficiency, efficiency_sigma)),
            )
            sampled_availability = min(
                1.0,
                max(0.0, rng.gauss(link.availability, availability_sigma)),
            )
            links.append(
                replace(
                    link,
                    efficiency=sampled_efficiency,
                    availability=sampled_availability,
                )
            )
        sampled = build_system(system.nodes, links)
        result = run_scenario(f"sample-{index}", sampled, renewable_resource_ids)
        efficiencies.append(result.overall_primary_to_service_efficiency)
        emissions.append(result.emissions_t_co2e)

    return {
        "iterations": iterations,
        "seed": seed,
        "efficiency_mean": mean(efficiencies),
        "efficiency_p05": _quantile(efficiencies, 0.05),
        "efficiency_p50": _quantile(efficiencies, 0.50),
        "efficiency_p95": _quantile(efficiencies, 0.95),
        "emissions_t_co2e_mean": mean(emissions),
        "emissions_t_co2e_p05": _quantile(emissions, 0.05),
        "emissions_t_co2e_p95": _quantile(emissions, 0.95),
    }
