from __future__ import annotations

from collections import defaultdict

from .core import Branch, BusInjection, dc_line_flow_mw


class GridNetwork:
    def __init__(self, branches: list[Branch] | tuple[Branch, ...]):
        self.branches = tuple(branch.validate() for branch in branches)
        if not self.branches:
            raise ValueError("at least one branch is required")

    @property
    def buses(self) -> tuple[str, ...]:
        names = {b.from_bus for b in self.branches} | {b.to_bus for b in self.branches}
        return tuple(sorted(names))

    def flows_from_angles(self, angles_rad: dict[str, float], base_mva: float = 100.0) -> dict[str, float]:
        missing = [bus for bus in self.buses if bus not in angles_rad]
        if missing:
            raise ValueError(f"missing voltage angles for: {', '.join(missing)}")
        return {
            branch.name: dc_line_flow_mw(
                angles_rad[branch.from_bus],
                angles_rad[branch.to_bus],
                branch.reactance_pu,
                base_mva,
            )
            for branch in self.branches
        }

    def utilization(self, flows_mw: dict[str, float]) -> dict[str, float]:
        result = {}
        for branch in self.branches:
            if branch.name not in flows_mw:
                raise ValueError(f"missing flow for branch {branch.name}")
            result[branch.name] = abs(flows_mw[branch.name]) / branch.thermal_limit_mw
        return result

    def overloaded(self, flows_mw: dict[str, float]) -> tuple[str, ...]:
        util = self.utilization(flows_mw)
        return tuple(sorted(name for name, value in util.items() if value > 1.0))

    @staticmethod
    def system_balance(injections: list[BusInjection] | tuple[BusInjection, ...]) -> float:
        return sum(injection.net_mw for injection in injections)

    @staticmethod
    def aggregate_by_bus(injections: list[BusInjection] | tuple[BusInjection, ...]) -> dict[str, float]:
        totals: dict[str, float] = defaultdict(float)
        for injection in injections:
            if not injection.bus.strip():
                raise ValueError("bus name must be non-empty")
            totals[injection.bus] += injection.net_mw
        return dict(sorted(totals.items()))
