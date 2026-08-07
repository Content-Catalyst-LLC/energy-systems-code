"""Dependency-light energy accounting with explicit boundaries and conventions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import prod
from typing import Iterable, Mapping


def _nonnegative(value: float, name: str) -> float:
    value = float(value)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def _fraction(value: float, name: str, *, allow_zero: bool = True) -> float:
    value = float(value)
    if value < 0 or value > 1 or (not allow_zero and value == 0):
        interval = "[0, 1]" if allow_zero else "(0, 1]"
        raise ValueError(f"{name} must be in {interval}")
    return value


@dataclass(frozen=True)
class AccountingChain:
    name: str
    primary_energy_mwh: float
    conversion_efficiency: float
    delivery_efficiency: float
    end_use_efficiency: float
    service_factor: float = 1.0
    energy_sector_own_use_fraction: float = 0.0
    non_energy_use_fraction: float = 0.0

    def validated(self) -> "AccountingChain":
        _nonnegative(self.primary_energy_mwh, "primary_energy_mwh")
        _fraction(self.conversion_efficiency, "conversion_efficiency")
        _fraction(self.delivery_efficiency, "delivery_efficiency")
        _fraction(self.end_use_efficiency, "end_use_efficiency")
        _fraction(self.service_factor, "service_factor")
        _fraction(self.energy_sector_own_use_fraction, "energy_sector_own_use_fraction")
        _fraction(self.non_energy_use_fraction, "non_energy_use_fraction")
        if self.energy_sector_own_use_fraction + self.non_energy_use_fraction > 1:
            raise ValueError("own use plus non-energy use cannot exceed primary energy")
        return self


@dataclass(frozen=True)
class AccountingResult:
    name: str
    primary_energy_mwh: float
    energy_sector_own_use_mwh: float
    non_energy_use_mwh: float
    transformation_input_mwh: float
    secondary_energy_mwh: float
    conversion_loss_mwh: float
    final_energy_mwh: float
    delivery_loss_mwh: float
    useful_energy_mwh: float
    end_use_loss_mwh: float
    service_energy_equivalent_mwh: float
    service_loss_mwh: float
    primary_to_final_efficiency: float
    primary_to_useful_efficiency: float
    primary_to_service_efficiency: float
    residual_mwh: float

    def as_dict(self) -> dict[str, float | str]:
        return asdict(self)


@dataclass(frozen=True)
class EnergyBalance:
    supply_mwh: float
    transformation_and_network_loss_mwh: float
    energy_sector_own_use_mwh: float
    non_energy_use_mwh: float
    final_energy_mwh: float
    residual_mwh: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def chain_accounting(chain: AccountingChain) -> AccountingResult:
    c = chain.validated()
    primary = c.primary_energy_mwh
    own_use = primary * c.energy_sector_own_use_fraction
    non_energy = primary * c.non_energy_use_fraction
    transformation_input = primary - own_use - non_energy
    secondary = transformation_input * c.conversion_efficiency
    conversion_loss = transformation_input - secondary
    final = secondary * c.delivery_efficiency
    delivery_loss = secondary - final
    useful = final * c.end_use_efficiency
    end_use_loss = final - useful
    service = useful * c.service_factor
    service_loss = useful - service
    residual = primary - (
        own_use
        + non_energy
        + conversion_loss
        + delivery_loss
        + end_use_loss
        + service_loss
        + service
    )
    return AccountingResult(
        name=c.name,
        primary_energy_mwh=primary,
        energy_sector_own_use_mwh=own_use,
        non_energy_use_mwh=non_energy,
        transformation_input_mwh=transformation_input,
        secondary_energy_mwh=secondary,
        conversion_loss_mwh=conversion_loss,
        final_energy_mwh=final,
        delivery_loss_mwh=delivery_loss,
        useful_energy_mwh=useful,
        end_use_loss_mwh=end_use_loss,
        service_energy_equivalent_mwh=service,
        service_loss_mwh=service_loss,
        primary_to_final_efficiency=(final / primary if primary else 0.0),
        primary_to_useful_efficiency=(useful / primary if primary else 0.0),
        primary_to_service_efficiency=(service / primary if primary else 0.0),
        residual_mwh=residual,
    )


def final_to_useful(final_energy_mwh: float, end_use_efficiency: float) -> float:
    final = _nonnegative(final_energy_mwh, "final_energy_mwh")
    efficiency = _fraction(end_use_efficiency, "end_use_efficiency")
    return final * efficiency


def site_to_source(site_energy_mwh: float, source_factor: float) -> float:
    site = _nonnegative(site_energy_mwh, "site_energy_mwh")
    factor = float(source_factor)
    if factor <= 0:
        raise ValueError("source_factor must be positive")
    return site * factor


def direct_equivalent_primary(generated_electricity_mwh: float) -> float:
    """Count non-combustible electricity at its generated electricity value."""
    return _nonnegative(generated_electricity_mwh, "generated_electricity_mwh")


def substitution_primary(
    generated_electricity_mwh: float,
    reference_thermal_efficiency: float,
) -> float:
    """Estimate displaced thermal primary energy using a stated reference efficiency."""
    electricity = _nonnegative(generated_electricity_mwh, "generated_electricity_mwh")
    efficiency = _fraction(reference_thermal_efficiency, "reference_thermal_efficiency", allow_zero=False)
    return electricity / efficiency


def energy_balance(
    supply_mwh: float,
    transformation_and_network_loss_mwh: float,
    energy_sector_own_use_mwh: float,
    non_energy_use_mwh: float,
    final_energy_mwh: float,
) -> EnergyBalance:
    values = {
        "supply_mwh": supply_mwh,
        "transformation_and_network_loss_mwh": transformation_and_network_loss_mwh,
        "energy_sector_own_use_mwh": energy_sector_own_use_mwh,
        "non_energy_use_mwh": non_energy_use_mwh,
        "final_energy_mwh": final_energy_mwh,
    }
    checked = {name: _nonnegative(value, name) for name, value in values.items()}
    residual = checked["supply_mwh"] - sum(
        checked[name]
        for name in (
            "transformation_and_network_loss_mwh",
            "energy_sector_own_use_mwh",
            "non_energy_use_mwh",
            "final_energy_mwh",
        )
    )
    return EnergyBalance(residual_mwh=residual, **checked)


def weighted_efficiency(values: Iterable[tuple[float, float]]) -> float:
    pairs = [(float(weight), _fraction(eff, "efficiency")) for weight, eff in values]
    total = sum(weight for weight, _ in pairs)
    if total <= 0:
        raise ValueError("total weight must be positive")
    return sum(weight * eff for weight, eff in pairs) / total


def aggregate_results(results: Iterable[AccountingResult]) -> Mapping[str, float]:
    rows = list(results)
    primary = sum(row.primary_energy_mwh for row in rows)
    final = sum(row.final_energy_mwh for row in rows)
    useful = sum(row.useful_energy_mwh for row in rows)
    service = sum(row.service_energy_equivalent_mwh for row in rows)
    residual = sum(row.residual_mwh for row in rows)
    return {
        "primary_energy_mwh": primary,
        "final_energy_mwh": final,
        "useful_energy_mwh": useful,
        "service_energy_equivalent_mwh": service,
        "primary_to_final_efficiency": final / primary if primary else 0.0,
        "primary_to_useful_efficiency": useful / primary if primary else 0.0,
        "primary_to_service_efficiency": service / primary if primary else 0.0,
        "residual_mwh": residual,
    }


def multistage_efficiency(efficiencies: Iterable[float]) -> float:
    values = [_fraction(value, "efficiency") for value in efficiencies]
    return prod(values)
