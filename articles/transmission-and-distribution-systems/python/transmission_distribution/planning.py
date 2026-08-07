from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExpansionOption:
    name: str
    capital_cost_million: float
    added_capacity_mw: float
    annual_loss_reduction_mwh: float
    congestion_savings_million_per_year: float
    implementation_years: float

    def validate(self) -> "ExpansionOption":
        if not self.name.strip():
            raise ValueError("name must be non-empty")
        values = (
            self.capital_cost_million,
            self.added_capacity_mw,
            self.annual_loss_reduction_mwh,
            self.congestion_savings_million_per_year,
            self.implementation_years,
        )
        if any(v < 0 for v in values):
            raise ValueError("planning values must be nonnegative")
        if self.implementation_years <= 0:
            raise ValueError("implementation_years must be positive")
        return self


def rank_expansion_options(
    options: list[ExpansionOption] | tuple[ExpansionOption, ...],
) -> list[dict[str, float | str]]:
    ranked = []
    for option in options:
        o = option.validate()
        capacity_per_cost = (
            o.added_capacity_mw / o.capital_cost_million
            if o.capital_cost_million > 0
            else float("inf")
        )
        score = (
            0.45 * capacity_per_cost
            + 0.35 * o.congestion_savings_million_per_year
            + 0.0002 * o.annual_loss_reduction_mwh
            - 0.20 * o.implementation_years
        )
        ranked.append({
            "name": o.name,
            "score": score,
            "capacity_per_cost": capacity_per_cost,
            "implementation_years": o.implementation_years,
        })
    return sorted(ranked, key=lambda x: (-float(x["score"]), str(x["name"])))
