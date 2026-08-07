from __future__ import annotations
from dataclasses import dataclass
from math import log2
import random
from statistics import mean, pstdev

@dataclass(frozen=True)
class Scenario:
    name: str
    years: int = 20
    start_year: int = 2026
    initial_capacity_gw: float = 40.0
    initial_cumulative_gw: float = 80.0
    base_build_gw: float = 6.0
    retirement_rate: float = 0.025
    learning_rate: float = 0.18
    manufacturing_limit_gw: float = 14.0
    transmission_limit_gw: float = 14.0
    permitting_factor: float = 0.95
    demand_pull: float = 1.0

    def validate(self):
        if not self.name.strip() or self.years <= 0:
            raise ValueError("invalid scenario")
        if self.initial_capacity_gw < 0 or self.initial_cumulative_gw <= 0:
            raise ValueError("invalid stock values")
        if not 0 <= self.retirement_rate < 1:
            raise ValueError("invalid retirement rate")
        if not 0 <= self.learning_rate < 1:
            raise ValueError("invalid learning rate")
        if self.manufacturing_limit_gw < 0 or self.transmission_limit_gw < 0:
            raise ValueError("invalid constraint")
        if not 0 <= self.permitting_factor <= 1 or self.demand_pull <= 0:
            raise ValueError("invalid multiplier")
        return self


def learning_cost(cumulative_gw, reference_gw=80.0, reference_cost=100.0, learning_rate=0.18):
    if cumulative_gw <= 0 or reference_gw <= 0 or reference_cost <= 0:
        raise ValueError("positive values required")
    if not 0 <= learning_rate < 1:
        raise ValueError("invalid learning rate")
    exponent = log2(1.0 - learning_rate) if learning_rate else 0.0
    return reference_cost * (cumulative_gw / reference_gw) ** exponent


def simulate(s: Scenario):
    s.validate()
    capacity = float(s.initial_capacity_gw)
    cumulative = float(s.initial_cumulative_gw)
    history = [(s.start_year, capacity, cumulative, 100.0, 0.0, 0.0)]
    for i in range(1, s.years + 1):
        cost = learning_cost(cumulative, s.initial_cumulative_gw, 100.0, s.learning_rate)
        unconstrained = s.base_build_gw * (100.0 / cost) * s.permitting_factor * s.demand_pull
        build = min(unconstrained, s.manufacturing_limit_gw, s.transmission_limit_gw)
        retire = capacity * s.retirement_rate
        capacity = max(0.0, capacity + build - retire)
        cumulative += build
        cost = learning_cost(cumulative, s.initial_cumulative_gw, 100.0, s.learning_rate)
        history.append((s.start_year + i, capacity, cumulative, cost, build, retire))
    return history


def rebound(baseline, engineering_after, actual_after):
    expected = baseline - engineering_after
    realized = baseline - actual_after
    if expected <= 0:
        raise ValueError("expected savings must be positive")
    offset = expected - realized
    return {"expected": expected, "realized": realized, "offset": offset, "fraction": offset / expected}


def loop_type(polarities):
    if not polarities or any(p not in (-1, 1) for p in polarities):
        raise ValueError("polarities must be +/-1")
    product = 1
    for p in polarities:
        product *= p
    return "reinforcing" if product > 0 else "balancing"


def monte_carlo(s: Scenario, draws=1000, seed=20260806):
    if draws <= 0:
        raise ValueError("draws must be positive")
    rng = random.Random(seed)
    finals = []
    for _ in range(draws):
        sampled = Scenario(
            name=s.name,
            years=s.years,
            start_year=s.start_year,
            initial_capacity_gw=s.initial_capacity_gw,
            initial_cumulative_gw=s.initial_cumulative_gw,
            base_build_gw=max(0.0, rng.gauss(s.base_build_gw, s.base_build_gw * 0.10)),
            retirement_rate=s.retirement_rate,
            learning_rate=s.learning_rate,
            manufacturing_limit_gw=s.manufacturing_limit_gw,
            transmission_limit_gw=s.transmission_limit_gw,
            permitting_factor=min(1.0, max(0.0, rng.gauss(s.permitting_factor, 0.05))),
            demand_pull=s.demand_pull,
        )
        finals.append(simulate(sampled)[-1][1])
    ordered = sorted(finals)
    q = lambda p: ordered[round((len(ordered)-1)*p)]
    return {
        "draws": draws,
        "mean_final_capacity_gw": mean(finals),
        "sd_final_capacity_gw": pstdev(finals),
        "p05": q(0.05),
        "p50": q(0.50),
        "p95": q(0.95),
    }
