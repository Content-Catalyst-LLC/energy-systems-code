"""Deterministic uncertainty analysis for heat-engine performance."""

from __future__ import annotations

from random import Random
from statistics import mean, pstdev

from .core import heat_engine


def _percentile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("No values supplied")
    position = probability * (len(sorted_values) - 1)
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction


def monte_carlo_heat_engine(
    *,
    heat_input: float,
    hot_temperature_k: float,
    cold_temperature_k: float,
    second_law_fraction: float,
    samples: int = 5000,
    seed: int = 20260806,
) -> dict[str, float | int]:
    if samples < 100:
        raise ValueError("samples must be at least 100")
    rng = Random(seed)
    efficiencies: list[float] = []
    work_outputs: list[float] = []
    entropy_generations: list[float] = []

    for _ in range(samples):
        hot = max(cold_temperature_k + 1.0, rng.gauss(hot_temperature_k, 0.02 * hot_temperature_k))
        cold = max(1.0, rng.gauss(cold_temperature_k, 0.01 * cold_temperature_k))
        if hot <= cold:
            hot = cold + 1.0
        fraction = min(1.0, max(0.05, rng.gauss(second_law_fraction, 0.05)))
        result = heat_engine(heat_input, hot, cold, fraction, ambient_temperature_k=cold)
        efficiencies.append(result.actual_efficiency)
        work_outputs.append(result.work_output)
        entropy_generations.append(result.entropy_generation)

    efficiencies.sort()
    work_outputs.sort()
    entropy_generations.sort()
    return {
        "samples": samples,
        "seed": seed,
        "efficiency_mean": mean(efficiencies),
        "efficiency_std": pstdev(efficiencies),
        "efficiency_p05": _percentile(efficiencies, 0.05),
        "efficiency_p50": _percentile(efficiencies, 0.50),
        "efficiency_p95": _percentile(efficiencies, 0.95),
        "work_output_p05": _percentile(work_outputs, 0.05),
        "work_output_p50": _percentile(work_outputs, 0.50),
        "work_output_p95": _percentile(work_outputs, 0.95),
        "entropy_generation_p50": _percentile(entropy_generations, 0.50),
    }
