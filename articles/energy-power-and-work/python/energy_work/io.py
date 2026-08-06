"""CSV and JSON helpers with explicit schema validation."""
from __future__ import annotations
import csv, json
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping
from .core import PowerObservation, ScenarioResult

REQUIRED_COLUMNS = {"timestamp", "power_kw"}

def read_power_profile(path: Path) -> list[PowerObservation]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
        rows = []
        for number, row in enumerate(reader, start=2):
            try:
                timestamp, power_kw = datetime.fromisoformat(row["timestamp"]), float(row["power_kw"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid row {number}: {row}") from exc
            if power_kw < 0: raise ValueError(f"Negative power at row {number}")
            rows.append(PowerObservation(timestamp, power_kw))
    if len(rows) < 2: raise ValueError("Power profile needs at least two rows")
    return rows

def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    materialized = list(rows)
    if not materialized: raise ValueError("Cannot write an empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized[0].keys()))
        writer.writeheader(); writer.writerows(materialized)

def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def scenario_rows(results: Iterable[ScenarioResult]) -> list[dict[str, object]]:
    return [item.to_dict() for item in results]
