#!/usr/bin/env python3
"""Dependency-light illustrative energy siting score model."""

from dataclasses import dataclass


@dataclass
class Site:
    name: str
    resource_quality: float
    grid_access: float
    land_conflict_risk: float
    environmental_sensitivity: float
    community_benefit: float


def score_site(site: Site) -> float:
    """Return a simple normalized siting score from 0 to 100."""
    positive = 0.35 * site.resource_quality + 0.25 * site.grid_access + 0.20 * site.community_benefit
    negative = 0.12 * site.land_conflict_risk + 0.08 * site.environmental_sensitivity
    return round(max(0.0, min(1.0, positive - negative)) * 100, 2)


if __name__ == "__main__":
    sites = [
        Site("Ridge A", 0.88, 0.72, 0.30, 0.35, 0.64),
        Site("Brownfield B", 0.62, 0.91, 0.12, 0.18, 0.80),
        Site("Prairie C", 0.79, 0.54, 0.61, 0.72, 0.42),
    ]
    for site in sites:
        print(f"{site.name}: {score_site(site)}")
