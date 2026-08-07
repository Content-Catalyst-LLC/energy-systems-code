"""CSV and JSON input/output helpers with explicit schemas."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

from .model import EnergyLink, EnergyNode, NodeKind, build_system


def read_nodes(path: Path) -> list[EnergyNode]:
    rows: list[EnergyNode] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"node_id", "name", "kind", "carrier", "capacity_mw", "criticality"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing node columns: {sorted(missing)}")
        for number, row in enumerate(reader, start=2):
            try:
                capacity = float(row["capacity_mw"]) if row["capacity_mw"].strip() else None
                rows.append(
                    EnergyNode(
                        node_id=row["node_id"].strip(),
                        name=row["name"].strip(),
                        kind=NodeKind(row["kind"].strip()),
                        carrier=row["carrier"].strip(),
                        capacity_mw=capacity,
                        criticality=float(row["criticality"] or 0.0),
                    )
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid node row {number}: {row}") from exc
    return rows


def read_links(path: Path) -> list[EnergyLink]:
    rows: list[EnergyLink] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "link_id",
            "source",
            "target",
            "input_mwh",
            "efficiency",
            "emissions_kg_co2e_per_mwh_input",
            "variable_cost_usd_per_mwh_input",
            "availability",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing link columns: {sorted(missing)}")
        for number, row in enumerate(reader, start=2):
            try:
                rows.append(
                    EnergyLink(
                        link_id=row["link_id"].strip(),
                        source=row["source"].strip(),
                        target=row["target"].strip(),
                        input_mwh=float(row["input_mwh"]),
                        efficiency=float(row["efficiency"]),
                        emissions_kg_co2e_per_mwh_input=float(
                            row["emissions_kg_co2e_per_mwh_input"] or 0.0
                        ),
                        variable_cost_usd_per_mwh_input=float(
                            row["variable_cost_usd_per_mwh_input"] or 0.0
                        ),
                        availability=float(row["availability"] or 1.0),
                    )
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid link row {number}: {row}") from exc
    return rows


def read_system(nodes_path: Path, links_path: Path):
    return build_system(read_nodes(nodes_path), read_links(links_path))


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    materialized = list(rows)
    if not materialized:
        raise ValueError("Cannot write an empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized[0].keys()))
        writer.writeheader()
        writer.writerows(materialized)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
