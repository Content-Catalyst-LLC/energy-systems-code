"""Deterministic uncertainty analysis for energy-accounting chains."""

from __future__ import annotations

import random
from statistics import fmean
from typing import Any

from .core import AccountingChain, chain_accounting


def _quantile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("values cannot be empty")
    index = (len(sorted_values) - 1) * probability
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = index - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def monte_carlo_chain(
    base: AccountingChain,
    *,
    samples: int = 2000,
    seed: int = 20260806,
    efficiency_relative_sd: float = 0.04,
) -> dict[str, Any]:
    if samples < 10:
        raise ValueError("samples must be at least 10")
    if efficiency_relative_sd < 0:
        raise ValueError("efficiency_relative_sd must be nonnegative")
    rng = random.Random(seed)
    useful_values: list[float] = []
    service_values: list[float] = []
    primary_to_useful: list[float] = []

    for _ in range(samples):
        def draw(value: float) -> float:
            sampled = rng.gauss(value, max(value * efficiency_relative_sd, 1e-12))
            return min(1.0, max(0.0, sampled))

        scenario = AccountingChain(
            name=base.name,
            primary_energy_mwh=base.primary_energy_mwh,
            conversion_efficiency=draw(base.conversion_efficiency),
            delivery_efficiency=draw(base.delivery_efficiency),
            end_use_efficiency=draw(base.end_use_efficiency),
            service_factor=draw(base.service_factor),
            energy_sector_own_use_fraction=base.energy_sector_own_use_fraction,
            non_energy_use_fraction=base.non_energy_use_fraction,
        )
        result = chain_accounting(scenario)
        useful_values.append(result.useful_energy_mwh)
        service_values.append(result.service_energy_equivalent_mwh)
        primary_to_useful.append(result.primary_to_useful_efficiency)

    useful_values.sort()
    service_values.sort()
    primary_to_useful.sort()
    return {
        "samples": samples,
        "seed": seed,
        "useful_energy_mwh": {
            "mean": fmean(useful_values),
            "p05": _quantile(useful_values, 0.05),
            "p50": _quantile(useful_values, 0.50),
            "p95": _quantile(useful_values, 0.95),
        },
        "service_energy_equivalent_mwh": {
            "mean": fmean(service_values),
            "p05": _quantile(service_values, 0.05),
            "p50": _quantile(service_values, 0.50),
            "p95": _quantile(service_values, 0.95),
        },
        "primary_to_useful_efficiency": {
            "mean": fmean(primary_to_useful),
            "p05": _quantile(primary_to_useful, 0.05),
            "p50": _quantile(primary_to_useful, 0.50),
            "p95": _quantile(primary_to_useful, 0.95),
        },
    }
