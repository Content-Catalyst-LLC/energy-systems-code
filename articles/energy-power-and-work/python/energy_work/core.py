"""Physics, time-series integration, conversion chains, and scenarios."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime
from math import cos, radians
from typing import Iterable, Sequence

@dataclass(frozen=True, slots=True)
class PowerObservation:
    timestamp: datetime
    power_kw: float

@dataclass(frozen=True, slots=True)
class ConversionStage:
    name: str
    efficiency: float
    def __post_init__(self) -> None:
        if not self.name.strip(): raise ValueError("Stage name cannot be empty")
        if not 0.0 <= self.efficiency <= 1.0: raise ValueError("Efficiency must be in [0, 1]")

@dataclass(frozen=True, slots=True)
class EnergyBalance:
    input_kwh: float
    useful_output_kwh: float
    losses_kwh: float
    overall_efficiency: float
    stage_records: tuple[dict[str, float | str], ...]

@dataclass(frozen=True, slots=True)
class ScenarioResult:
    scenario: str
    energy_kwh: float
    mean_power_kw: float
    peak_power_kw: float
    load_factor: float
    useful_energy_kwh: float
    losses_kwh: float
    avoided_energy_kwh: float
    conservation_residual_kwh: float
    def to_dict(self) -> dict[str, float | str]: return asdict(self)

def mechanical_work_j(force_n: float, displacement_m: float, angle_deg: float = 0.0) -> float:
    return float(force_n) * float(displacement_m) * cos(radians(float(angle_deg)))

def kinetic_energy_j(mass_kg: float, velocity_m_s: float) -> float:
    if mass_kg < 0: raise ValueError("Mass cannot be negative")
    return 0.5 * mass_kg * velocity_m_s ** 2

def gravitational_potential_energy_j(mass_kg: float, height_m: float, gravity_m_s2: float = 9.80665) -> float:
    if mass_kg < 0: raise ValueError("Mass cannot be negative")
    return mass_kg * gravity_m_s2 * height_m

def elastic_potential_energy_j(spring_constant_n_m: float, displacement_m: float) -> float:
    if spring_constant_n_m < 0: raise ValueError("Spring constant cannot be negative")
    return 0.5 * spring_constant_n_m * displacement_m ** 2

def integrate_power_wh(observations: Sequence[PowerObservation]) -> float:
    if len(observations) < 2: raise ValueError("At least two observations are required")
    ordered = sorted(observations, key=lambda item: item.timestamp)
    energy_kwh = 0.0
    for left, right in zip(ordered, ordered[1:]):
        duration_h = (right.timestamp - left.timestamp).total_seconds() / 3600.0
        if duration_h <= 0: raise ValueError("Timestamps must be unique and increasing")
        energy_kwh += 0.5 * (left.power_kw + right.power_kw) * duration_h
    return energy_kwh * 1000.0

def load_statistics(observations: Sequence[PowerObservation]) -> dict[str, float]:
    ordered = sorted(observations, key=lambda item: item.timestamp)
    energy_kwh = integrate_power_wh(ordered) / 1000.0
    duration_h = (ordered[-1].timestamp - ordered[0].timestamp).total_seconds() / 3600.0
    mean_kw, peak_kw = energy_kwh / duration_h, max(item.power_kw for item in ordered)
    minimum_kw = min(item.power_kw for item in ordered)
    return {"duration_h": duration_h, "energy_kwh": energy_kwh, "mean_power_kw": mean_kw,
            "peak_power_kw": peak_kw, "minimum_power_kw": minimum_kw,
            "load_factor": mean_kw / peak_kw if peak_kw else 0.0}

def run_conversion_chain(input_kwh: float, stages: Iterable[ConversionStage]) -> EnergyBalance:
    if input_kwh < 0: raise ValueError("Input energy cannot be negative")
    records, current = [], float(input_kwh)
    for stage in stages:
        output = current * stage.efficiency
        records.append({"stage": stage.name, "input_kwh": current, "efficiency": stage.efficiency,
                        "output_kwh": output, "loss_kwh": current - output})
        current = output
    losses = input_kwh - current
    return EnergyBalance(float(input_kwh), current, losses,
                         current / input_kwh if input_kwh else 0.0, tuple(records))

def run_scenario(name: str, observations: Sequence[PowerObservation], demand_multiplier: float,
                 efficiency_stages: Iterable[ConversionStage], baseline_energy_kwh: float | None = None) -> ScenarioResult:
    if demand_multiplier <= 0: raise ValueError("Demand multiplier must be positive")
    scaled = [PowerObservation(item.timestamp, item.power_kw * demand_multiplier) for item in observations]
    stats = load_statistics(scaled)
    balance = run_conversion_chain(stats["energy_kwh"], efficiency_stages)
    avoided = 0.0 if baseline_energy_kwh is None else baseline_energy_kwh - stats["energy_kwh"]
    residual = balance.input_kwh - balance.useful_output_kwh - balance.losses_kwh
    return ScenarioResult(name, stats["energy_kwh"], stats["mean_power_kw"], stats["peak_power_kw"],
                          stats["load_factor"], balance.useful_output_kwh, balance.losses_kwh,
                          avoided, residual)
