from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class Branch:
    name: str
    from_bus: str
    to_bus: str
    reactance_pu: float
    thermal_limit_mw: float
    resistance_pu: float = 0.0

    def validate(self) -> "Branch":
        if not self.name.strip() or not self.from_bus.strip() or not self.to_bus.strip():
            raise ValueError("branch identifiers must be non-empty")
        if self.from_bus == self.to_bus:
            raise ValueError("branch endpoints must differ")
        if self.reactance_pu <= 0:
            raise ValueError("reactance_pu must be positive")
        if self.thermal_limit_mw <= 0:
            raise ValueError("thermal_limit_mw must be positive")
        if self.resistance_pu < 0:
            raise ValueError("resistance_pu must be nonnegative")
        return self


@dataclass(frozen=True)
class BusInjection:
    bus: str
    generation_mw: float
    load_mw: float

    @property
    def net_mw(self) -> float:
        return _finite("generation_mw", self.generation_mw) - _finite("load_mw", self.load_mw)


def dc_line_flow_mw(angle_from_rad: float, angle_to_rad: float, reactance_pu: float, base_mva: float = 100.0) -> float:
    x = _finite("reactance_pu", reactance_pu)
    base = _finite("base_mva", base_mva)
    if x <= 0 or base <= 0:
        raise ValueError("reactance and base_mva must be positive")
    return (_finite("angle_from_rad", angle_from_rad) - _finite("angle_to_rad", angle_to_rad)) / x * base


def transmission_loss_mw(flow_mw: float, resistance_pu: float, voltage_pu: float = 1.0, base_mva: float = 100.0) -> float:
    flow = _finite("flow_mw", flow_mw)
    r = _finite("resistance_pu", resistance_pu)
    v = _finite("voltage_pu", voltage_pu)
    base = _finite("base_mva", base_mva)
    if r < 0 or v <= 0 or base <= 0:
        raise ValueError("invalid resistance, voltage, or base")
    current_pu = (flow / base) / v
    loss_pu = current_pu * current_pu * r
    return loss_pu * base


def reserve_margin(available_capacity_mw: float, peak_load_mw: float) -> float:
    available = _finite("available_capacity_mw", available_capacity_mw)
    peak = _finite("peak_load_mw", peak_load_mw)
    if peak <= 0:
        raise ValueError("peak_load_mw must be positive")
    return (available - peak) / peak


def frequency_deviation_hz(power_imbalance_mw: float, frequency_response_mw_per_hz: float) -> float:
    response = _finite("frequency_response_mw_per_hz", frequency_response_mw_per_hz)
    if response <= 0:
        raise ValueError("frequency_response_mw_per_hz must be positive")
    return -_finite("power_imbalance_mw", power_imbalance_mw) / response


def storage_dispatch(
    state_of_charge_mwh: float,
    net_load_mw: float,
    duration_hours: float,
    power_limit_mw: float,
    energy_capacity_mwh: float,
    round_trip_efficiency: float = 0.90,
) -> dict[str, float]:
    soc = _finite("state_of_charge_mwh", state_of_charge_mwh)
    net = _finite("net_load_mw", net_load_mw)
    dt = _finite("duration_hours", duration_hours)
    power = _finite("power_limit_mw", power_limit_mw)
    capacity = _finite("energy_capacity_mwh", energy_capacity_mwh)
    eta_rt = _finite("round_trip_efficiency", round_trip_efficiency)

    if dt <= 0 or power < 0 or capacity <= 0 or not 0 < eta_rt <= 1:
        raise ValueError("invalid storage parameters")
    soc = min(max(soc, 0.0), capacity)
    eta = eta_rt ** 0.5

    if net > 0:
        discharge_to_grid = min(power, net, soc * eta / dt)
        energy_removed = discharge_to_grid * dt / eta
        new_soc = soc - energy_removed
        return {"grid_mw": -discharge_to_grid, "new_soc_mwh": new_soc}

    charge_from_grid = min(power, -net, (capacity - soc) / (dt * eta))
    energy_stored = charge_from_grid * dt * eta
    new_soc = soc + energy_stored
    return {"grid_mw": charge_from_grid, "new_soc_mwh": new_soc}
