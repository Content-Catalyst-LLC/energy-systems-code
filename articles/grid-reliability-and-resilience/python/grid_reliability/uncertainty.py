from __future__ import annotations

import random
from statistics import mean, pstdev


def monte_carlo_resource_adequacy(
    *,
    dependable_capacity_mw: float,
    peak_load_mw: float,
    capacity_sigma: float = 0.05,
    load_sigma: float = 0.04,
    draws: int = 3000,
    seed: int = 20260806,
) -> dict[str, float]:
    if dependable_capacity_mw <= 0 or peak_load_mw <= 0:
        raise ValueError("capacity and peak load must be positive")
    if capacity_sigma < 0 or load_sigma < 0:
        raise ValueError("sigma values must be nonnegative")
    if draws <= 0:
        raise ValueError("draws must be positive")

    rng = random.Random(seed)
    margins = []
    shortfall_mwh = []

    for _ in range(draws):
        capacity = max(
            0.0,
            rng.gauss(
                dependable_capacity_mw,
                dependable_capacity_mw * capacity_sigma,
            ),
        )
        load = max(
            1e-9,
            rng.gauss(
                peak_load_mw,
                peak_load_mw * load_sigma,
            ),
        )
        margin = capacity - load
        margins.append(margin)
        shortfall_mwh.append(max(0.0, -margin))

    ordered = sorted(margins)

    def q(p: float) -> float:
        i = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * p)))
        return ordered[i]

    return {
        "draws": float(draws),
        "mean_margin_mw": mean(margins),
        "sd_margin_mw": pstdev(margins),
        "p05_margin_mw": q(0.05),
        "p50_margin_mw": q(0.50),
        "p95_margin_mw": q(0.95),
        "shortfall_probability": sum(1 for x in margins if x < 0) / draws,
        "mean_shortfall_mw": mean(shortfall_mwh),
    }
