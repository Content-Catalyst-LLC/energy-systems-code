"""Dependency-light flow accounting for energy Sankey datasets."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Flow:
    source: str
    target: str
    value_mwh: float
    category: str = "energy"
    note: str = ""

    def validated(self) -> "Flow":
        if not self.source.strip() or not self.target.strip():
            raise ValueError("source and target must be non-empty")
        if self.source == self.target:
            raise ValueError("self-links are not allowed")
        value = float(self.value_mwh)
        if not isfinite(value) or value < 0:
            raise ValueError("value_mwh must be finite and nonnegative")
        return Flow(self.source, self.target, value, self.category, self.note)


@dataclass(frozen=True)
class NodeBalance:
    node: str
    inflow_mwh: float
    outflow_mwh: float
    residual_mwh: float
    relative_residual: float

    @property
    def balanced(self) -> bool:
        return abs(self.residual_mwh) <= 1e-9


class FlowNetwork:
    def __init__(self, flows: Iterable[Flow]):
        self.flows = tuple(flow.validated() for flow in flows)
        if not self.flows:
            raise ValueError("at least one flow is required")

    @property
    def nodes(self) -> tuple[str, ...]:
        names = {f.source for f in self.flows} | {f.target for f in self.flows}
        return tuple(sorted(names))

    def total_flow(self) -> float:
        return sum(f.value_mwh for f in self.flows)

    def inflow(self, node: str) -> float:
        return sum(f.value_mwh for f in self.flows if f.target == node)

    def outflow(self, node: str) -> float:
        return sum(f.value_mwh for f in self.flows if f.source == node)

    def balance(self, node: str) -> NodeBalance:
        incoming = self.inflow(node)
        outgoing = self.outflow(node)
        residual = incoming - outgoing
        scale = max(incoming, outgoing, 1.0)
        return NodeBalance(
            node=node,
            inflow_mwh=incoming,
            outflow_mwh=outgoing,
            residual_mwh=residual,
            relative_residual=residual / scale,
        )

    def balances(self) -> tuple[NodeBalance, ...]:
        return tuple(self.balance(node) for node in self.nodes)

    def internal_nodes(self) -> tuple[str, ...]:
        return tuple(
            node for node in self.nodes
            if self.inflow(node) > 0 and self.outflow(node) > 0
        )

    def assert_balanced(self, tolerance_mwh: float = 1e-9) -> None:
        for node in self.internal_nodes():
            residual = self.balance(node).residual_mwh
            if abs(residual) > tolerance_mwh:
                raise ValueError(
                    f"node {node!r} is imbalanced by {residual:.12g} MWh"
                )

    def source_total(self) -> float:
        return sum(
            f.value_mwh for f in self.flows
            if self.inflow(f.source) == 0
        )

    def sink_total(self) -> float:
        return sum(
            f.value_mwh for f in self.flows
            if self.outflow(f.target) == 0
        )

    def boundary_residual(self) -> float:
        return self.source_total() - self.sink_total()


def aggregate_links(flows: Iterable[Flow]) -> tuple[Flow, ...]:
    bucket: dict[tuple[str, str, str], float] = defaultdict(float)
    notes: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for flow in flows:
        f = flow.validated()
        key = (f.source, f.target, f.category)
        bucket[key] += f.value_mwh
        if f.note:
            notes[key].append(f.note)
    result = []
    for (source, target, category), value in sorted(bucket.items()):
        note = "; ".join(dict.fromkeys(notes[(source, target, category)]))
        result.append(Flow(source, target, value, category, note))
    return tuple(result)


def normalize_widths(
    flows: Iterable[Flow],
    *,
    max_width: float = 28.0,
    min_visible_width: float = 0.0,
) -> dict[tuple[str, str], float]:
    validated = [f.validated() for f in flows]
    if max_width <= 0:
        raise ValueError("max_width must be positive")
    if min_visible_width < 0:
        raise ValueError("min_visible_width must be nonnegative")
    maximum = max((f.value_mwh for f in validated), default=0.0)
    if maximum == 0:
        return {(f.source, f.target): 0.0 for f in validated}
    return {
        (f.source, f.target): (
            0.0 if f.value_mwh == 0
            else max(min_visible_width, max_width * f.value_mwh / maximum)
        )
        for f in validated
    }


def reconcile_balanced_node(
    inflows: Mapping[str, float],
    outflows: Mapping[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    """Scale both sides toward their average total while preserving composition."""
    in_total = sum(float(v) for v in inflows.values())
    out_total = sum(float(v) for v in outflows.values())
    if in_total < 0 or out_total < 0:
        raise ValueError("totals must be nonnegative")
    target = (in_total + out_total) / 2.0

    def rescale(values: Mapping[str, float], total: float) -> dict[str, float]:
        if any(float(v) < 0 for v in values.values()):
            raise ValueError("flows must be nonnegative")
        if total == 0:
            return {k: 0.0 for k in values}
        factor = target / total
        return {k: float(v) * factor for k, v in values.items()}

    return rescale(inflows, in_total), rescale(outflows, out_total)
