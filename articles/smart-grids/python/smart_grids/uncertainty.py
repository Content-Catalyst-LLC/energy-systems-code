from __future__ import annotations

import random
from statistics import mean, pstdev


def monte_carlo_flexible_peak(
    *,
    baseline_peak_mw: float,
    flexible_capacity_mw: float,
    participation_mean: float = 0.75,
    participation_sigma: float = 0.10,
    forecast_sigma_fraction: float = 0.03,
    draws: int = 2500,
    seed: int = 20260806,
) -> dict[str, float]:
    if baseline_peak_mw <= 0 or flexible_capacity_mw < 0:
        raise ValueError("invalid baseline or flexible capacity")
    if not 0 <= participation_mean <= 1:
        raise ValueError("participation_mean must be in [0,1]")
    if participation_sigma < 0 or forecast_sigma_fraction < 0:
        raise ValueError("sigma values must be nonnegative")
    if draws <= 0:
        raise ValueError("draws must be positive")

    rng = random.Random(seed)
    net_peaks = []

    for _ in range(draws):
        baseline = max(
            0.0,
            rng.gauss(
                baseline_peak_mw,
                baseline_peak_mw * forecast_sigma_fraction,
            ),
        )
        participation = min(
            1.0,
            max(
                0.0,
                rng.gauss(
                    participation_mean,
                    participation_sigma,
                ),
            ),
        )
        response = flexible_capacity_mw * participation
        net_peaks.append(max(0.0, baseline - response))

    ordered = sorted(net_peaks)

    def q(p: float) -> float:
        i = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * p)))
        return ordered[i]

    return {
        "draws": float(draws),
        "mean_net_peak_mw": mean(net_peaks),
        "sd_net_peak_mw": pstdev(net_peaks),
        "p05_net_peak_mw": q(0.05),
        "p50_net_peak_mw": q(0.50),
        "p95_net_peak_mw": q(0.95),
    }
