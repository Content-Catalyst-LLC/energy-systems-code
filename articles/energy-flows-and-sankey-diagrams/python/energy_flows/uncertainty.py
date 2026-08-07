"""Deterministic uncertainty analysis for an energy-flow network."""

from __future__ import annotations

import random
from statistics import mean, pstdev
from typing import Iterable

from .core import Flow, FlowNetwork


def monte_carlo_network(
    flows: Iterable[Flow],
    *,
    relative_sigma: float = 0.03,
    draws: int = 1000,
    seed: int = 20260806,
) -> dict[str, float]:
    if relative_sigma < 0:
        raise ValueError("relative_sigma must be nonnegative")
    if draws <= 0:
        raise ValueError("draws must be positive")
    base = tuple(flow.validated() for flow in flows)
    rng = random.Random(seed)
    totals = []
    boundary_residuals = []
    for _ in range(draws):
        sampled = []
        for flow in base:
            sigma = flow.value_mwh * relative_sigma
            value = max(0.0, rng.gauss(flow.value_mwh, sigma))
            sampled.append(
                Flow(flow.source, flow.target, value, flow.category, flow.note)
            )
        network = FlowNetwork(sampled)
        totals.append(network.total_flow())
        boundary_residuals.append(network.boundary_residual())
    return {
        "draws": float(draws),
        "relative_sigma": float(relative_sigma),
        "mean_total_link_flow_mwh": mean(totals),
        "sd_total_link_flow_mwh": pstdev(totals),
        "mean_boundary_residual_mwh": mean(boundary_residuals),
        "sd_boundary_residual_mwh": pstdev(boundary_residuals),
    }
