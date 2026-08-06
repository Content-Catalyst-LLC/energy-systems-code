"""Deterministic Monte Carlo propagation of conversion uncertainty."""
from __future__ import annotations
import random
from dataclasses import asdict, dataclass
from statistics import fmean

@dataclass(frozen=True, slots=True)
class MonteCarloSummary:
    iterations: int
    mean_useful_energy_kwh: float
    p05_useful_energy_kwh: float
    p50_useful_energy_kwh: float
    p95_useful_energy_kwh: float
    mean_losses_kwh: float
    def to_dict(self): return asdict(self)

def _quantile(values: list[float], probability: float) -> float:
    position = (len(values) - 1) * probability
    lower, upper = int(position), min(int(position) + 1, len(values) - 1)
    fraction = position - lower
    return values[lower] * (1 - fraction) + values[upper] * fraction

def propagate_efficiency_uncertainty(input_energy_kwh: float, means: list[float], stddevs: list[float],
                                     iterations: int = 10000, seed: int = 20260806) -> MonteCarloSummary:
    if iterations < 100: raise ValueError("Use at least 100 iterations")
    if not means or len(means) != len(stddevs): raise ValueError("Invalid efficiency vectors")
    rng, useful_samples = random.Random(seed), []
    for _ in range(iterations):
        useful = float(input_energy_kwh)
        for mean, stddev in zip(means, stddevs):
            useful *= min(1.0, max(0.0, rng.gauss(mean, stddev)))
        useful_samples.append(useful)
    useful_samples.sort()
    losses = [input_energy_kwh - value for value in useful_samples]
    return MonteCarloSummary(iterations, fmean(useful_samples), _quantile(useful_samples, 0.05),
                             _quantile(useful_samples, 0.50), _quantile(useful_samples, 0.95), fmean(losses))
