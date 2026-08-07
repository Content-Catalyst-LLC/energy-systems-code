"""Dependency-light thermodynamic models with explicit sign conventions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import prod
from typing import Iterable

R_UNIVERSAL = 8.31446261815324  # J mol^-1 K^-1


def _positive(value: float, name: str) -> float:
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return float(value)


def _fraction(value: float, name: str, *, allow_zero: bool = True) -> float:
    lower = 0.0 if allow_zero else 0.0
    if value < lower or value > 1.0 or (not allow_zero and value == 0.0):
        raise ValueError(f"{name} must be in {'(0, 1]' if not allow_zero else '[0, 1]'}")
    return float(value)


def celsius_to_kelvin(temperature_c: float) -> float:
    temperature_k = float(temperature_c) + 273.15
    if temperature_k <= 0:
        raise ValueError("Temperature must be above absolute zero")
    return temperature_k


def first_law_delta_u(heat_into_system: float, work_by_system: float) -> float:
    """Return ΔU = Q - W using heat-in/work-out sign convention."""
    return float(heat_into_system) - float(work_by_system)


def ideal_gas_temperature(pressure_pa: float, volume_m3: float, amount_mol: float) -> float:
    pressure = _positive(pressure_pa, "pressure_pa")
    volume = _positive(volume_m3, "volume_m3")
    amount = _positive(amount_mol, "amount_mol")
    return pressure * volume / (amount * R_UNIVERSAL)


def carnot_efficiency(hot_temperature_k: float, cold_temperature_k: float) -> float:
    hot = _positive(hot_temperature_k, "hot_temperature_k")
    cold = _positive(cold_temperature_k, "cold_temperature_k")
    if hot <= cold:
        raise ValueError("Hot-reservoir temperature must exceed cold-reservoir temperature")
    return 1.0 - cold / hot


def heat_pump_cop_heating(
    hot_temperature_k: float,
    cold_temperature_k: float,
    second_law_fraction: float = 1.0,
) -> float:
    hot = _positive(hot_temperature_k, "hot_temperature_k")
    cold = _positive(cold_temperature_k, "cold_temperature_k")
    if hot <= cold:
        raise ValueError("Hot-side temperature must exceed cold-side temperature")
    fraction = _fraction(second_law_fraction, "second_law_fraction", allow_zero=False)
    return fraction * hot / (hot - cold)


def exergy_of_heat(heat: float, source_temperature_k: float, ambient_temperature_k: float) -> float:
    source = _positive(source_temperature_k, "source_temperature_k")
    ambient = _positive(ambient_temperature_k, "ambient_temperature_k")
    if source < ambient:
        raise ValueError("Heat-source temperature cannot be below ambient for this model")
    return float(heat) * (1.0 - ambient / source)


def entropy_generation_heat_engine(
    heat_input: float,
    heat_rejected: float,
    hot_temperature_k: float,
    cold_temperature_k: float,
) -> float:
    hot = _positive(hot_temperature_k, "hot_temperature_k")
    cold = _positive(cold_temperature_k, "cold_temperature_k")
    q_hot = _positive(heat_input, "heat_input")
    q_cold = _positive(heat_rejected, "heat_rejected")
    entropy_generation = q_cold / cold - q_hot / hot
    if entropy_generation < -1e-10:
        raise ValueError("Inputs imply negative entropy generation")
    return max(0.0, entropy_generation)


@dataclass(frozen=True, slots=True)
class HeatEngineResult:
    heat_input: float
    work_output: float
    heat_rejected: float
    actual_efficiency: float
    carnot_efficiency: float
    second_law_fraction: float
    entropy_generation: float
    exergy_input: float
    exergy_efficiency: float
    first_law_residual: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def heat_engine(
    heat_input: float,
    hot_temperature_k: float,
    cold_temperature_k: float,
    second_law_fraction: float,
    ambient_temperature_k: float | None = None,
) -> HeatEngineResult:
    q_hot = _positive(heat_input, "heat_input")
    eta_carnot = carnot_efficiency(hot_temperature_k, cold_temperature_k)
    fraction = _fraction(second_law_fraction, "second_law_fraction", allow_zero=False)
    actual_efficiency = eta_carnot * fraction
    work = q_hot * actual_efficiency
    q_cold = q_hot - work
    entropy_generation = entropy_generation_heat_engine(
        q_hot, q_cold, hot_temperature_k, cold_temperature_k
    )
    ambient = cold_temperature_k if ambient_temperature_k is None else ambient_temperature_k
    exergy_input = exergy_of_heat(q_hot, hot_temperature_k, ambient)
    exergy_efficiency = work / exergy_input if exergy_input > 0 else 0.0
    residual = q_hot - work - q_cold
    return HeatEngineResult(
        heat_input=q_hot,
        work_output=work,
        heat_rejected=q_cold,
        actual_efficiency=actual_efficiency,
        carnot_efficiency=eta_carnot,
        second_law_fraction=fraction,
        entropy_generation=entropy_generation,
        exergy_input=exergy_input,
        exergy_efficiency=exergy_efficiency,
        first_law_residual=residual,
    )


def multistage_efficiency(stage_efficiencies: Iterable[float]) -> float:
    values = tuple(_fraction(value, "stage_efficiency") for value in stage_efficiencies)
    if not values:
        raise ValueError("At least one stage efficiency is required")
    return prod(values)


@dataclass(frozen=True, slots=True)
class ThermalStorageResult:
    energy_charged: float
    energy_stored_after_charge: float
    energy_after_standby: float
    useful_discharge: float
    total_loss: float
    round_trip_efficiency: float
    conservation_residual: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def thermal_storage_cycle(
    energy_charged: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    retention_fraction: float,
) -> ThermalStorageResult:
    charged = _positive(energy_charged, "energy_charged")
    eta_charge = _fraction(charge_efficiency, "charge_efficiency")
    eta_discharge = _fraction(discharge_efficiency, "discharge_efficiency")
    retention = _fraction(retention_fraction, "retention_fraction")
    stored = charged * eta_charge
    after_standby = stored * retention
    useful = after_standby * eta_discharge
    loss = charged - useful
    residual = charged - useful - loss
    return ThermalStorageResult(
        energy_charged=charged,
        energy_stored_after_charge=stored,
        energy_after_standby=after_standby,
        useful_discharge=useful,
        total_loss=loss,
        round_trip_efficiency=useful / charged,
        conservation_residual=residual,
    )
