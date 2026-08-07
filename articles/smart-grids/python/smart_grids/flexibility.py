from __future__ import annotations

from math import isfinite


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def charging_power_mw(
    vehicles: int,
    energy_kwh_each: float,
    charging_hours: float,
) -> float:
    if vehicles < 0:
        raise ValueError("vehicles must be nonnegative")
    energy = _finite("energy_kwh_each", energy_kwh_each)
    hours = _finite("charging_hours", charging_hours)
    if energy < 0 or hours <= 0:
        raise ValueError("energy must be nonnegative and hours positive")
    total_mwh = vehicles * energy / 1000.0
    return total_mwh / hours


def demand_response_net_load(
    baseline_mw: float,
    response_mw: float,
) -> float:
    baseline = _finite("baseline_mw", baseline_mw)
    response = _finite("response_mw", response_mw)
    if baseline < 0 or response < 0:
        raise ValueError("loads must be nonnegative")
    return max(0.0, baseline - response)


def annual_energy_reduction_mwh(
    average_load_mw: float,
    reduction_fraction: float,
    operating_hours: float,
) -> float:
    load = _finite("average_load_mw", average_load_mw)
    reduction = _finite("reduction_fraction", reduction_fraction)
    hours = _finite("operating_hours", operating_hours)
    if load < 0 or hours < 0 or not 0 <= reduction <= 1:
        raise ValueError("invalid reduction inputs")
    return load * reduction * hours


def load_factor(
    energy_mwh: float,
    hours: float,
    peak_mw: float,
) -> float:
    energy = _finite("energy_mwh", energy_mwh)
    h = _finite("hours", hours)
    peak = _finite("peak_mw", peak_mw)
    if energy < 0 or h <= 0 or peak <= 0:
        raise ValueError("invalid load-factor inputs")
    average = energy / h
    return average / peak
