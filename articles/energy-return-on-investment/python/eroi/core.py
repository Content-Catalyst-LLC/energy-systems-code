from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


def _nonnegative(name: str, value: float) -> float:
    value = float(value)
    if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


@dataclass(frozen=True)
class EnergyInvestment:
    construction_mwh: float = 0.0
    fuel_cycle_mwh: float = 0.0
    operations_mwh: float = 0.0
    maintenance_mwh: float = 0.0
    replacement_mwh: float = 0.0
    network_mwh: float = 0.0
    storage_mwh: float = 0.0
    retirement_mwh: float = 0.0

    def total_mwh(self) -> float:
        values = [
            ("construction_mwh", self.construction_mwh),
            ("fuel_cycle_mwh", self.fuel_cycle_mwh),
            ("operations_mwh", self.operations_mwh),
            ("maintenance_mwh", self.maintenance_mwh),
            ("replacement_mwh", self.replacement_mwh),
            ("network_mwh", self.network_mwh),
            ("storage_mwh", self.storage_mwh),
            ("retirement_mwh", self.retirement_mwh),
        ]
        return sum(_nonnegative(name, value) for name, value in values)


@dataclass(frozen=True)
class EnergyProject:
    name: str
    gross_output_mwh: float
    investment: EnergyInvestment

    def validated_output(self) -> float:
        if not self.name.strip():
            raise ValueError("name must be non-empty")
        return _nonnegative("gross_output_mwh", self.gross_output_mwh)

    def eroi(self) -> float:
        gross = self.validated_output()
        invested = self.investment.total_mwh()
        if invested <= 0:
            raise ValueError("total invested energy must be positive")
        return gross / invested

    def net_energy_mwh(self) -> float:
        return self.validated_output() - self.investment.total_mwh()

    def net_fraction(self) -> float:
        gross = self.validated_output()
        if gross <= 0:
            raise ValueError("gross output must be positive")
        return self.net_energy_mwh() / gross


def net_energy_fraction(eroi: float) -> float:
    eroi = float(eroi)
    if not isfinite(eroi) or eroi <= 0:
        raise ValueError("EROI must be finite and positive")
    return 1.0 - 1.0 / eroi


def energy_payback_years(upfront_mwh: float, annual_output_mwh: float, annual_operating_mwh: float = 0.0) -> float:
    upfront = _nonnegative("upfront_mwh", upfront_mwh)
    output = _nonnegative("annual_output_mwh", annual_output_mwh)
    operating = _nonnegative("annual_operating_mwh", annual_operating_mwh)
    annual_net = output - operating
    if annual_net <= 0:
        raise ValueError("annual net energy return must be positive")
    return upfront / annual_net


def delivered_eroi(
    direct_output_mwh: float,
    stored_output_input_mwh: float,
    storage_round_trip_efficiency: float,
    generation_investment_mwh: float,
    storage_investment_mwh: float,
    network_investment_mwh: float = 0.0,
) -> float:
    direct = _nonnegative("direct_output_mwh", direct_output_mwh)
    stored = _nonnegative("stored_output_input_mwh", stored_output_input_mwh)
    eta = float(storage_round_trip_efficiency)
    if not isfinite(eta) or not 0 < eta <= 1:
        raise ValueError("storage_round_trip_efficiency must be in (0, 1]")
    invested = (
        _nonnegative("generation_investment_mwh", generation_investment_mwh)
        + _nonnegative("storage_investment_mwh", storage_investment_mwh)
        + _nonnegative("network_investment_mwh", network_investment_mwh)
    )
    if invested <= 0:
        raise ValueError("total investment must be positive")
    delivered = direct + stored * eta
    return delivered / invested
