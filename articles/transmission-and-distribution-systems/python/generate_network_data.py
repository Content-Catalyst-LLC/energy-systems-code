#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

feeders = [
    ["North", 15.0, 11.2, 0.96, 4.5, 5.2, 0.35],
    ["Central", 18.0, 16.5, 0.95, 5.0, 6.0, 0.48],
    ["East", 12.0, 9.6, 0.97, 3.6, 4.4, 0.28],
    ["South", 10.0, 8.7, 0.94, 4.2, 5.1, 0.39],
    ["Industrial", 24.0, 20.8, 0.98, 2.8, 3.5, 0.61],
]

with (RAW / "feeders.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow([
        "feeder",
        "rating_mva",
        "peak_mva",
        "power_factor",
        "resistance_ohm",
        "reactance_ohm",
        "length_factor",
    ])
    writer.writerows(feeders)

hosting = [
    ["Residential EV growth", 15.0, 11.2, 2.4, 0.4, 0.96],
    ["Solar export", 12.0, 7.5, 0.0, 4.5, 0.97],
    ["Fleet charging depot", 18.0, 13.0, 5.5, 0.0, 0.95],
    ["Battery managed load", 10.0, 8.7, 1.8, 1.4, 0.94],
    ["Industrial electrification", 24.0, 20.8, 6.5, 0.0, 0.98],
]

with (RAW / "hosting_cases.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow([
        "name",
        "feeder_rating_mva",
        "base_peak_mva",
        "added_load_mw",
        "added_generation_mw",
        "power_factor",
    ])
    writer.writerows(hosting)

options = [
    ["New feeder", 18.0, 12.0, 320, 1.8, 3.0],
    ["Reconductoring", 9.0, 8.0, 780, 1.2, 1.5],
    ["Dynamic ratings", 3.0, 4.5, 0, 0.7, 0.8],
    ["Battery support", 7.0, 5.0, 260, 0.8, 1.0],
    ["New substation transformer", 12.0, 15.0, 180, 1.0, 2.5],
]

with (RAW / "expansion_options.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow([
        "name",
        "capital_cost_million",
        "added_capacity_mw",
        "annual_loss_reduction_mwh",
        "congestion_savings_million_per_year",
        "implementation_years",
    ])
    writer.writerows(options)

print(f"Wrote synthetic T&D data to {RAW}")
