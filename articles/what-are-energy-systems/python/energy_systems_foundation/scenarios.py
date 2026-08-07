"""Deterministic transformations used by the article scenarios."""

from __future__ import annotations

from dataclasses import replace

from .model import EnergyLink, EnergySystem, build_system


def transform_system(
    system: EnergySystem,
    *,
    efficiency_multiplier: float = 1.0,
    demand_multiplier: float = 1.0,
    availability_overrides: dict[str, float] | None = None,
    input_overrides: dict[str, float] | None = None,
) -> EnergySystem:
    availability_overrides = availability_overrides or {}
    input_overrides = input_overrides or {}
    links: list[EnergyLink] = []
    node_map = system.node_map()

    for link in system.links:
        target_kind = node_map[link.target].kind.value
        scaled_input = input_overrides.get(link.link_id, link.input_mwh)
        if target_kind == "service":
            scaled_input *= demand_multiplier
        links.append(
            replace(
                link,
                input_mwh=scaled_input,
                efficiency=min(1.0, link.efficiency * efficiency_multiplier),
                availability=availability_overrides.get(link.link_id, link.availability),
            )
        )
    return build_system(system.nodes, links)
