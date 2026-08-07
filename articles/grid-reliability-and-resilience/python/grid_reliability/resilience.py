from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ResilienceScenario:
    name: str
    annual_probability: float
    consequence_million_usd: float
    service_retained_fraction: float

    def validate(self) -> "ResilienceScenario":
        if not self.name.strip():
            raise ValueError("name must be non-empty")
        if not 0 <= self.annual_probability <= 1:
            raise ValueError("annual_probability must be in [0,1]")
        if self.consequence_million_usd < 0:
            raise ValueError("consequence must be nonnegative")
        if not 0 <= self.service_retained_fraction <= 1:
            raise ValueError("service_retained_fraction must be in [0,1]")
        return self


def annualized_risk(probability: float, consequence: float) -> float:
    p = float(probability)
    c = float(consequence)
    if not isfinite(p) or not isfinite(c):
        raise ValueError("inputs must be finite")
    if not 0 <= p <= 1 or c < 0:
        raise ValueError("invalid probability or consequence")
    return p * c


def restoration_auc(hours: list[float] | tuple[float, ...], service_fraction: list[float] | tuple[float, ...]) -> float:
    if len(hours) != len(service_fraction) or len(hours) < 2:
        raise ValueError("hours and service_fraction must have equal length >= 2")
    area = 0.0
    for i in range(1, len(hours)):
        t0, t1 = float(hours[i - 1]), float(hours[i])
        s0, s1 = float(service_fraction[i - 1]), float(service_fraction[i])
        if t1 < t0:
            raise ValueError("hours must be nondecreasing")
        if not 0 <= s0 <= 1 or not 0 <= s1 <= 1:
            raise ValueError("service fractions must be in [0,1]")
        area += (t1 - t0) * (s0 + s1) / 2.0
    return area
