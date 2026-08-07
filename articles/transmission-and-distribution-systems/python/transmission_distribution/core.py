from __future__ import annotations

from math import isfinite, sqrt


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


def three_phase_current_a(
    power_mw: float,
    voltage_kv: float,
    power_factor: float = 1.0,
) -> float:
    p = _finite("power_mw", power_mw) * 1_000_000.0
    v = _positive("voltage_kv", voltage_kv) * 1_000.0
    pf = _finite("power_factor", power_factor)
    if not 0 < pf <= 1:
        raise ValueError("power_factor must be in (0,1]")
    return p / (sqrt(3.0) * v * pf)


def three_phase_loss_kw(
    current_a: float,
    resistance_ohm_per_phase: float,
) -> float:
    i = _finite("current_a", current_a)
    r = _finite("resistance_ohm_per_phase", resistance_ohm_per_phase)
    if r < 0:
        raise ValueError("resistance must be nonnegative")
    return 3.0 * i * i * r / 1000.0


def transformer_loading(load_kva: float, rating_kva: float) -> float:
    return _finite("load_kva", load_kva) / _positive("rating_kva", rating_kva)


def feeder_utilization(load_mva: float, rating_mva: float) -> float:
    return _finite("load_mva", load_mva) / _positive("rating_mva", rating_mva)


def voltage_drop_percent(
    current_a: float,
    resistance_ohm: float,
    reactance_ohm: float,
    voltage_v: float,
    power_factor: float,
) -> float:
    i = _finite("current_a", current_a)
    r = _finite("resistance_ohm", resistance_ohm)
    x = _finite("reactance_ohm", reactance_ohm)
    v = _positive("voltage_v", voltage_v)
    pf = _finite("power_factor", power_factor)

    if r < 0 or x < 0 or not 0 < pf <= 1:
        raise ValueError("invalid impedance or power factor")

    sin_phi = max(0.0, (1.0 - pf * pf) ** 0.5)
    drop_v = sqrt(3.0) * i * (r * pf + x * sin_phi)
    return 100.0 * drop_v / v


def congestion_cost(
    constrained_mwh: float,
    local_cost_per_mwh: float,
    remote_cost_per_mwh: float,
) -> float:
    energy = _finite("constrained_mwh", constrained_mwh)
    local = _finite("local_cost_per_mwh", local_cost_per_mwh)
    remote = _finite("remote_cost_per_mwh", remote_cost_per_mwh)
    if energy < 0:
        raise ValueError("constrained_mwh must be nonnegative")
    return energy * max(0.0, local - remote)
