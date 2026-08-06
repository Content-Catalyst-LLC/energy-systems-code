#!/usr/bin/env python3
"""Generate a deterministic 72-hour facility power profile."""
import csv, math, random
from datetime import datetime, timedelta
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "hourly_power_profile.csv"

def main() -> None:
    rng, start, rows = random.Random(20260806), datetime(2026, 7, 1), []
    for hour in range(73):
        stamp = start + timedelta(hours=hour)
        daytime = max(0.0, math.sin(math.pi * ((stamp.hour - 6) / 14)))
        weekday = 1.0 if stamp.weekday() < 5 else 0.82
        cooling = 85.0 * max(0.0, math.sin(math.pi * ((stamp.hour - 9) / 12)))
        power = max(200.0, 420.0 * weekday + 250.0 * daytime * weekday + cooling + rng.uniform(-18, 18))
        rows.append((stamp.isoformat(timespec="minutes"), round(power, 3)))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(["timestamp", "power_kw"]); writer.writerows(rows)
    print(f"Wrote {OUTPUT}")
if __name__ == "__main__": main()
