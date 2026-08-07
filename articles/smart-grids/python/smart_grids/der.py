from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DERResource:
    name: str
    power_mw: float
    availability: float
    response_fraction: float

    def validate(self) -> "DERResource":
        if not self.name.strip():
            raise ValueError("name must be non-empty")
        if self.power_mw < 0:
            raise ValueError("power_mw must be nonnegative")
        if not 0 <= self.availability <= 1:
            raise ValueError("availability must be in [0,1]")
        if not 0 <= self.response_fraction <= 1:
            raise ValueError("response_fraction must be in [0,1]")
        return self


def aggregate_der_capacity(
    resources: list[DERResource] | tuple[DERResource, ...],
) -> float:
    return sum(r.validate().power_mw for r in resources)


def dispatch_available_der(
    resources: list[DERResource] | tuple[DERResource, ...],
) -> float:
    return sum(
        r.validate().power_mw * r.availability * r.response_fraction
        for r in resources
    )
