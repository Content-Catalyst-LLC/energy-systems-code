"""Dependency-light directed energy-system model with explicit boundaries."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from enum import Enum
from math import isclose
from typing import Iterable


class NodeKind(str, Enum):
    RESOURCE = "resource"
    CONVERSION = "conversion"
    NETWORK = "network"
    STORAGE = "storage"
    END_USE = "end_use"
    SERVICE = "service"
    LOSS = "loss"


@dataclass(frozen=True, slots=True)
class EnergyNode:
    node_id: str
    name: str
    kind: NodeKind
    carrier: str
    capacity_mw: float | None = None
    criticality: float = 0.0

    def __post_init__(self) -> None:
        if not self.node_id.strip() or not self.name.strip():
            raise ValueError("Node id and name are required")
        if self.capacity_mw is not None and self.capacity_mw < 0:
            raise ValueError("Capacity cannot be negative")
        if not 0.0 <= self.criticality <= 1.0:
            raise ValueError("Criticality must be in [0, 1]")


# Teaching-model link: input energy is MWh, emissions are kg CO2e per input
# MWh, and variable cost is USD per input MWh. Efficiency/availability are
# fractions in [0, 1]. These declared inputs are not measured grid flows.
@dataclass(frozen=True, slots=True)
class EnergyLink:
    link_id: str
    source: str
    target: str
    input_mwh: float
    efficiency: float
    emissions_kg_co2e_per_mwh_input: float = 0.0
    variable_cost_usd_per_mwh_input: float = 0.0
    availability: float = 1.0

    def __post_init__(self) -> None:
        if not self.link_id.strip() or not self.source.strip() or not self.target.strip():
            raise ValueError("Link id, source, and target are required")
        if self.input_mwh < 0:
            raise ValueError("Input energy cannot be negative")
        if not 0.0 <= self.efficiency <= 1.0:
            raise ValueError("Efficiency must be in [0, 1]")
        if self.emissions_kg_co2e_per_mwh_input < 0:
            raise ValueError("Emissions factor cannot be negative")
        if self.variable_cost_usd_per_mwh_input < 0:
            raise ValueError("Variable cost cannot be negative")
        if not 0.0 <= self.availability <= 1.0:
            raise ValueError("Availability must be in [0, 1]")

    @property
    def available_input_mwh(self) -> float:
        return self.input_mwh * self.availability

    @property
    def output_mwh(self) -> float:
        return self.available_input_mwh * self.efficiency

    @property
    def loss_mwh(self) -> float:
        return self.available_input_mwh - self.output_mwh

    @property
    def unavailable_mwh(self) -> float:
        return self.input_mwh * (1.0 - self.availability)

    @property
    def emissions_kg_co2e(self) -> float:
        return self.available_input_mwh * self.emissions_kg_co2e_per_mwh_input

    @property
    def variable_cost_usd(self) -> float:
        return self.available_input_mwh * self.variable_cost_usd_per_mwh_input


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    scenario: str
    primary_input_mwh: float
    delivered_final_energy_mwh: float
    useful_service_mwh_equivalent: float
    conversion_and_network_losses_mwh: float
    curtailed_or_unallocated_mwh: float
    unavailable_energy_mwh: float
    unserved_service_mwh_equivalent: float
    overall_primary_to_service_efficiency: float
    emissions_t_co2e: float
    variable_cost_usd: float
    renewable_input_share: float
    critical_service_served_share: float
    conservation_residual_mwh: float

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


# A directed acyclic teaching graph; validation rejects duplicate IDs,
# unknown endpoints, self-loops and cycles. The topological order supports
# deterministic flow accounting, not a full electrical-grid power-flow solve.
@dataclass(frozen=True, slots=True)
class EnergySystem:
    nodes: tuple[EnergyNode, ...]
    links: tuple[EnergyLink, ...]

    def node_map(self) -> dict[str, EnergyNode]:
        return {node.node_id: node for node in self.nodes}

    def validate(self) -> None:
        nodes = self.node_map()
        if len(nodes) != len(self.nodes):
            raise ValueError("Node identifiers must be unique")
        link_ids = {link.link_id for link in self.links}
        if len(link_ids) != len(self.links):
            raise ValueError("Link identifiers must be unique")
        for link in self.links:
            if link.source not in nodes or link.target not in nodes:
                raise ValueError(f"Unknown node referenced by {link.link_id}")
            if link.source == link.target:
                raise ValueError(f"Self-loop is not allowed: {link.link_id}")
        self.topological_order()

    def topological_order(self) -> tuple[str, ...]:
        nodes = self.node_map()
        indegree = {node_id: 0 for node_id in nodes}
        adjacency: dict[str, list[str]] = defaultdict(list)
        for link in self.links:
            adjacency[link.source].append(link.target)
            indegree[link.target] += 1
        queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
        ordered: list[str] = []
        while queue:
            node_id = queue.popleft()
            ordered.append(node_id)
            for target in sorted(adjacency[node_id]):
                indegree[target] -= 1
                if indegree[target] == 0:
                    queue.append(target)
        if len(ordered) != len(nodes):
            raise ValueError("Energy-system graph must be acyclic for this teaching model")
        return tuple(ordered)

    def incoming(self) -> dict[str, list[EnergyLink]]:
        result: dict[str, list[EnergyLink]] = defaultdict(list)
        for link in self.links:
            result[link.target].append(link)
        return result

    def outgoing(self) -> dict[str, list[EnergyLink]]:
        result: dict[str, list[EnergyLink]] = defaultdict(list)
        for link in self.links:
            result[link.source].append(link)
        return result

    def flow_balance(self) -> list[dict[str, float | str]]:
        """Return the declared baseline balance before scenario propagation."""
        nodes = self.node_map()
        incoming = self.incoming()
        outgoing = self.outgoing()
        rows: list[dict[str, float | str]] = []
        for node_id in self.topological_order():
            node = nodes[node_id]
            energy_in = sum(link.output_mwh for link in incoming.get(node_id, []))
            energy_out = sum(link.available_input_mwh for link in outgoing.get(node_id, []))
            rows.append(
                {
                    "node_id": node_id,
                    "name": node.name,
                    "kind": node.kind.value,
                    "carrier": node.carrier,
                    "energy_in_mwh": energy_in,
                    "energy_out_mwh": energy_out,
                    "net_accumulation_mwh": energy_in - energy_out,
                }
            )
        return rows


def build_system(nodes: Iterable[EnergyNode], links: Iterable[EnergyLink]) -> EnergySystem:
    system = EnergySystem(tuple(nodes), tuple(links))
    system.validate()
    return system


def _propagate(system: EnergySystem) -> tuple[list[dict[str, float | str]], dict[str, float]]:
    """Propagate available energy through the directed graph.

    Declared link inputs are requested flows. If upstream energy is insufficient,
    outgoing links share the available energy in proportion to their requests.
    """
    nodes = system.node_map()
    outgoing = system.outgoing()
    incoming_energy: dict[str, float] = defaultdict(float)
    curtailed_by_node: dict[str, float] = defaultdict(float)
    records: list[dict[str, float | str]] = []

    for node_id in system.topological_order():
        node = nodes[node_id]
        links = outgoing.get(node_id, [])
        if not links:
            continue

        requested = [link.input_mwh * link.availability for link in links]
        requested_total = sum(requested)
        if node.kind == NodeKind.RESOURCE:
            scale = 1.0
        else:
            supply = incoming_energy[node_id]
            scale = min(1.0, supply / requested_total) if requested_total else 0.0
            curtailed_by_node[node_id] = max(0.0, supply - requested_total * scale)

        for link, available_request in zip(links, requested):
            actual_input = available_request * scale
            output = actual_input * link.efficiency
            loss = actual_input - output
            incoming_energy[link.target] += output
            records.append(
                {
                    "link_id": link.link_id,
                    "source": link.source,
                    "target": link.target,
                    "declared_input_mwh": link.input_mwh,
                    "actual_input_mwh": actual_input,
                    "output_mwh": output,
                    "loss_mwh": loss,
                    "forced_unavailable_mwh": link.input_mwh * (1.0 - link.availability),
                    "upstream_shortfall_mwh": max(0.0, available_request - actual_input),
                    "emissions_kg_co2e": actual_input * link.emissions_kg_co2e_per_mwh_input,
                    "variable_cost_usd": actual_input * link.variable_cost_usd_per_mwh_input,
                }
            )

    terminal_energy = {
        node_id: incoming_energy[node_id]
        for node_id, node in nodes.items()
        if not outgoing.get(node_id)
    }
    terminal_energy.update({f"curtailed::{key}": value for key, value in curtailed_by_node.items()})
    return records, terminal_energy


def run_scenario(
    scenario: str,
    system: EnergySystem,
    renewable_resource_ids: set[str],
) -> ScenarioResult:
    system.validate()
    nodes = system.node_map()
    records, terminal = _propagate(system)

    by_link = {str(row["link_id"]): row for row in records}
    primary_records = [row for row in records if nodes[str(row["source"])].kind == NodeKind.RESOURCE]
    service_records = [row for row in records if nodes[str(row["target"])].kind == NodeKind.SERVICE]

    primary_input = sum(float(row["actual_input_mwh"]) for row in primary_records)
    renewable_input = sum(
        float(row["actual_input_mwh"])
        for row in primary_records
        if str(row["source"]) in renewable_resource_ids
    )
    delivered_final = sum(
        terminal.get(node.node_id, 0.0)
        for node in system.nodes
        if node.kind == NodeKind.END_USE
    )
    # End-use nodes are not terminal in this model; use actual energy delivered to them.
    delivered_final = sum(
        float(row["output_mwh"])
        for row in records
        if nodes[str(row["target"])].kind == NodeKind.END_USE
    )
    useful_service = sum(float(row["output_mwh"]) for row in service_records)
    losses = sum(float(row["loss_mwh"]) for row in records)
    forced_unavailable = sum(float(row["forced_unavailable_mwh"]) for row in records)
    emissions = sum(float(row["emissions_kg_co2e"]) for row in records) / 1000.0
    cost = sum(float(row["variable_cost_usd"]) for row in records)

    curtailed = sum(
        value for key, value in terminal.items() if key.startswith("curtailed::")
    )
    # Non-service terminal nodes would also represent energy outside useful service.
    for node_id, value in terminal.items():
        if node_id.startswith("curtailed::"):
            continue
        node = nodes[node_id]
        if node.kind not in {NodeKind.SERVICE, NodeKind.LOSS}:
            curtailed += value

    nominal_service = sum(link.input_mwh * link.efficiency for link in system.links if nodes[link.target].kind == NodeKind.SERVICE)
    unserved = max(0.0, nominal_service - useful_service)

    critical_nominal = 0.0
    critical_actual = 0.0
    for link in system.links:
        target = nodes[link.target]
        if target.kind != NodeKind.SERVICE:
            continue
        weight = target.criticality
        critical_nominal += link.input_mwh * link.efficiency * weight
        critical_actual += float(by_link[link.link_id]["output_mwh"]) * weight
    critical_share = critical_actual / critical_nominal if critical_nominal else 1.0

    residual = primary_input - useful_service - losses - curtailed
    if not isclose(residual, 0.0, abs_tol=1e-7):
        raise ValueError(f"Energy conservation residual is {residual}")

    return ScenarioResult(
        scenario=scenario,
        primary_input_mwh=primary_input,
        delivered_final_energy_mwh=delivered_final,
        useful_service_mwh_equivalent=useful_service,
        conversion_and_network_losses_mwh=losses,
        curtailed_or_unallocated_mwh=curtailed,
        unavailable_energy_mwh=forced_unavailable,
        unserved_service_mwh_equivalent=unserved,
        overall_primary_to_service_efficiency=(useful_service / primary_input if primary_input else 0.0),
        emissions_t_co2e=emissions,
        variable_cost_usd=cost,
        renewable_input_share=(renewable_input / primary_input if primary_input else 0.0),
        critical_service_served_share=critical_share,
        conservation_residual_mwh=residual,
    )
