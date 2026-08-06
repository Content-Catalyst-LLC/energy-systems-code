"""Auditable energy and power conversions using SI as the internal basis."""
from __future__ import annotations
from typing import Final

ENERGY_TO_J: Final = {"j": 1.0, "kj": 1e3, "mj": 1e6, "gj": 1e9,
    "wh": 3600.0, "kwh": 3.6e6, "mwh": 3.6e9, "gwh": 3.6e12,
    "btu_it": 1055.05585262, "therm_us": 105480400.0, "toe": 41868000000.0}
POWER_TO_W: Final = {"w": 1.0, "kw": 1e3, "mw": 1e6, "gw": 1e9,
    "hp_mechanical": 745.6998715822702}

def _key(unit: str) -> str:
    return unit.strip().lower().replace(" ", "_").replace("-", "_")

def _convert(value: float, source: str, target: str, factors: dict[str, float]) -> float:
    source_key, target_key = _key(source), _key(target)
    if source_key not in factors: raise ValueError(f"Unsupported source unit: {source}")
    if target_key not in factors: raise ValueError(f"Unsupported target unit: {target}")
    return float(value) * factors[source_key] / factors[target_key]

def convert_energy(value: float, from_unit: str, to_unit: str) -> float:
    return _convert(value, from_unit, to_unit, ENERGY_TO_J)

def convert_power(value: float, from_unit: str, to_unit: str) -> float:
    return _convert(value, from_unit, to_unit, POWER_TO_W)
