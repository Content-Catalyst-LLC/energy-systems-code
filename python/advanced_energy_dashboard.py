#!/usr/bin/env python3
"""Optional advanced energy systems dashboard outputs.

Requires:
    pip install -r requirements-advanced.txt
"""

from pathlib import Path

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit(
        "Advanced dependencies missing. Run: pip install -r requirements-advanced.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic" / "hourly_load_and_renewables.csv"
FIG_DIR = ROOT / "outputs" / "figures"


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    df["renewables_mwh"] = df["solar_mwh"] + df["wind_mwh"]

    ax = df.plot(
        x="hour",
        y=["demand_mwh", "renewables_mwh"],
        title="Synthetic hourly demand and renewable generation"
    )
    ax.set_xlabel("Hour")
    ax.set_ylabel("MWh")
    ax.figure.tight_layout()
    output = FIG_DIR / "hourly_demand_renewables.png"
    ax.figure.savefig(output, dpi=160)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
