from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _positive(name: str, value: float) -> float:
    value = _finite(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


@dataclass(frozen=True)
class OutageEvent:
    customers_affected: int
    duration_hours: float
    unserved_mw: float = 0.0
    probability: float = 1.0

    def validate(self) -> "OutageEvent":
        if self.customers_affected < 0:
            raise ValueError("customers_affected must be nonnegative")
        if self.duration_hours < 0:
            raise ValueError("duration_hours must be nonnegative")
        if self.unserved_mw < 0:
            raise ValueError("unserved_mw must be nonnegative")
        if not 0 <= self.probability <= 1:
            raise ValueError("probability must be in [0,1]")
        return self


def saidi(events: list[OutageEvent] | tuple[OutageEvent, ...], total_customers: int) -> float:
    if total_customers <= 0:
        raise ValueError("total_customers must be positive")
    customer_hours = sum(
        e.validate().customers_affected * e.duration_hours
        for e in events
    )
    return customer_hours / total_customers


def saifi(events: list[OutageEvent] | tuple[OutageEvent, ...], total_customers: int) -> float:
    if total_customers <= 0:
        raise ValueError("total_customers must be positive")
    interruptions = sum(e.validate().customers_affected for e in events)
    return interruptions / total_customers


def caidi(events: list[OutageEvent] | tuple[OutageEvent, ...], total_customers: int) -> float:
    frequency = saifi(events, total_customers)
    if frequency == 0:
        return 0.0
    return saidi(events, total_customers) / frequency


def reserve_margin(available_capacity_mw: float, peak_load_mw: float) -> float:
    available = _finite("available_capacity_mw", available_capacity_mw)
    peak = _positive("peak_load_mw", peak_load_mw)
    return (available - peak) / peak


def frequency_deviation_hz(power_imbalance_mw: float, frequency_response_mw_per_hz: float) -> float:
    response = _positive("frequency_response_mw_per_hz", frequency_response_mw_per_hz)
    return -_finite("power_imbalance_mw", power_imbalance_mw) / response


def expected_unserved_energy_mwh(events: list[OutageEvent] | tuple[OutageEvent, ...]) -> float:
    return sum(
        e.validate().probability * e.unserved_mw * e.duration_hours
        for e in events
    )
