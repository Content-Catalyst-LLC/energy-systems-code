from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HostingCase:
    name: str
    feeder_rating_mva: float
    base_peak_mva: float
    added_load_mw: float
    added_generation_mw: float
    power_factor: float = 1.0

    def validate(self) -> "HostingCase":
        if not self.name.strip():
            raise ValueError("name must be non-empty")
        if self.feeder_rating_mva <= 0:
            raise ValueError("feeder rating must be positive")
        if self.base_peak_mva < 0:
            raise ValueError("base peak must be nonnegative")
        if self.added_load_mw < 0 or self.added_generation_mw < 0:
            raise ValueError("added values must be nonnegative")
        if not 0 < self.power_factor <= 1:
            raise ValueError("power_factor must be in (0,1]")
        return self


def hosting_headroom_mw(
    feeder_rating_mva: float,
    current_peak_mva: float,
    power_factor: float = 1.0,
) -> float:
    if feeder_rating_mva <= 0 or current_peak_mva < 0:
        raise ValueError("invalid feeder values")
    if not 0 < power_factor <= 1:
        raise ValueError("power_factor must be in (0,1]")
    return max(0.0, feeder_rating_mva * power_factor - current_peak_mva * power_factor)


def evaluate_hosting_case(case: HostingCase) -> dict[str, float | bool | str]:
    c = case.validate()
    net_peak_mw = c.base_peak_mva * c.power_factor + c.added_load_mw - c.added_generation_mw
    effective_capacity_mw = c.feeder_rating_mva * c.power_factor
    utilization = net_peak_mw / effective_capacity_mw
    return {
        "name": c.name,
        "net_peak_mw": net_peak_mw,
        "effective_capacity_mw": effective_capacity_mw,
        "utilization": utilization,
        "thermal_violation": utilization > 1.0,
        "headroom_mw": max(0.0, effective_capacity_mw - net_peak_mw),
    }
