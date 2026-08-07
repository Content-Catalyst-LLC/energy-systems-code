from __future__ import annotations

import random
from statistics import mean, pstdev

from .core import EnergyInvestment, EnergyProject


def monte_carlo_eroi(
    project: EnergyProject,
    *,
    output_sigma: float = 0.06,
    investment_sigma: float = 0.08,
    draws: int = 2000,
    seed: int = 20260806,
) -> dict[str, float]:
    if draws <= 0:
        raise ValueError("draws must be positive")
    if output_sigma < 0 or investment_sigma < 0:
        raise ValueError("sigma values must be nonnegative")

    gross = project.validated_output()
    invested = project.investment.total_mwh()
    if invested <= 0:
        raise ValueError("investment must be positive")

    rng = random.Random(seed)
    erois = []
    net_energies = []

    for _ in range(draws):
        sampled_output = max(0.0, rng.gauss(gross, gross * output_sigma))
        sampled_investment = max(1e-12, rng.gauss(invested, invested * investment_sigma))
        erois.append(sampled_output / sampled_investment)
        net_energies.append(sampled_output - sampled_investment)

    ordered = sorted(erois)

    def q(p: float) -> float:
        i = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * p)))
        return ordered[i]

    return {
        "draws": float(draws),
        "mean_eroi": mean(erois),
        "sd_eroi": pstdev(erois),
        "p05_eroi": q(0.05),
        "p50_eroi": q(0.50),
        "p95_eroi": q(0.95),
        "mean_net_energy_mwh": mean(net_energies),
    }
